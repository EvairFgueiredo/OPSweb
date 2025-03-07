import asyncio
import websockets

# Variável global para armazenar a conexão do cliente (túnel)
tunnel = None

async def register_tunnel(websocket):
    """Registra o cliente local que ficará responsável por encaminhar as requisições."""
    global tunnel
    tunnel = websocket
    print("Túnel registrado pelo cliente local.")
    try:
        # Permanece ativo enquanto o cliente estiver conectado
        await websocket.wait_closed()
    finally:
        tunnel = None
        print("Túnel desconectado.")

async def handle_request(websocket, path):
    global tunnel
    # Se o caminho for "/register", tratamos como registro do túnel
    if path == "/register":
        await register_tunnel(websocket)
    else:
        # Se não houver túnel registrado, não é possível encaminhar a requisição
        if tunnel is None:
            await websocket.send("Nenhum túnel disponível.")
            await websocket.close()
            return
        
        try:
            # Recebe os dados da requisição (pode ser, por exemplo, uma string contendo a requisição HTTP)
            request_data = await websocket.recv()
            print("Requisição recebida do usuário:", request_data)
            
            # Encaminha a requisição para o túnel (cliente local)
            await tunnel.send(request_data)
            print("Requisição encaminhada para o túnel local.")
            
            # Aguarda a resposta do cliente local
            response_data = await tunnel.recv()
            print("Resposta recebida do túnel:", response_data)
            
            # Envia a resposta de volta para o usuário
            await websocket.send(response_data)
        except Exception as e:
            print("Erro no encaminhamento:", e)
            await websocket.close()

async def main():
    async with websockets.serve(handle_request, "0.0.0.0", 10000):
        print("Servidor de túnel reverso rodando na porta 8080.")
        await asyncio.Future()  # Mantém o servidor rodando

if __name__ == "__main__":
    asyncio.run(main())
