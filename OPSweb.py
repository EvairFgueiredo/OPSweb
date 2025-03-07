import asyncio
import websockets

async def handle_http_tunnel(websocket, path):
    # Cria uma conexão TCP para o Apache local (supondo que ele esteja rodando na porta 80)
    reader, writer = await asyncio.open_connection('127.0.0.1', 80)
    
    async def ws_to_tcp():
        try:
            async for message in websocket:
                writer.write(message)
                await writer.drain()
        except Exception as e:
            print(f"Erro no ws_to_tcp: {e}")
            writer.close()

    async def tcp_to_ws():
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                await websocket.send(data)
        except Exception as e:
            print(f"Erro no tcp_to_ws: {e}")
    
    await asyncio.gather(ws_to_tcp(), tcp_to_ws())

async def main():
    async with websockets.serve(handle_http_tunnel, "0.0.0.0", 8080):
        print("Servidor de túnel HTTP rodando na porta 8080")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
