import asyncio
import websockets
import aiohttp
from aiohttp import web

# Armazena conexões WebSocket ativas
clients = set()

async def websocket_handler(websocket, path):
    """Gerencia conexões WebSocket do cliente local (Programa 1)."""
    print("Novo túnel WebSocket estabelecido.")
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Requisição recebida via WebSocket ({len(message)} bytes)")

            # Encaminha a requisição HTTP para o Apache local no Render
            async with aiohttp.ClientSession() as session:
                async with session.request("GET", "https://127.0.0.1:443", data=message, ssl=False) as response:
                    data = await response.read()

            print(f"Resposta do Apache enviada ({len(data)} bytes)")
            await websocket.send(data)  # Envia resposta de volta para o WebSocket
    except websockets.exceptions.ConnectionClosed:
        print("Conexão WebSocket encerrada.")
    finally:
        clients.remove(websocket)

async def http_handler(request):
    """Aceita requisições HTTP normais e as envia para um túnel WebSocket."""
    if not clients:
        return web.Response(status=503, text="Nenhum túnel WebSocket ativo.")

    client = next(iter(clients))  # Pega um WebSocket disponível
    data = await request.read()
    
    print(f"Recebida requisição HTTP ({len(data)} bytes), encaminhando via WebSocket...")
    await client.send(data)  # Encaminha para WebSocket

    response = await client.recv()  # Aguarda resposta do WebSocket
    print(f"Resposta recebida via WebSocket ({len(response)} bytes), enviando ao cliente...")

    return web.Response(body=response)

async def main():
    """Inicia o servidor WebSocket e o servidor HTTP no Render."""
    ws_server = websockets.serve(websocket_handler, "0.0.0.0", 10000)
    app = web.Application()
    app.router.add_route("*", "/", http_handler)  # Todas as rotas passam pelo WebSocket

    print("Servidor WebSocket e Proxy HTTP rodando no Render...")
    await asyncio.gather(ws_server, web._run_app(app, port=8080))

if __name__ == "__main__":
    asyncio.run(main())
