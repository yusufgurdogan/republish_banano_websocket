import asyncio
import json
import websockets

SOURCE_WS_URL = "wss://ws2.banano.trade"
TARGET_ACCOUNT = "ban_1w4unoqatatkpsztgdg4zfa4ucqsijsziapqqb7j53wm6e3es8zwgeooywi6" # Example BANANO account
CLIENTS = set()  # Keep track of connected clients

async def source_subscriber(ws_uri):
    async with websockets.connect(ws_uri) as websocket:
        await websocket.send(json.dumps({
            "action": "subscribe",
            "topic": "confirmation",
            "options": {"confirmation_type": "all"}
        }))
        async for message in websocket:
            data = json.loads(message)
            # Here comes the filtering!
            if data.get("message", {}).get("account") == TARGET_ACCOUNT:
                await publish_to_clients(data)

async def publish_to_clients(data):
    if CLIENTS:  # Only proceed if there are clients connected
        message = json.dumps(data)
        await asyncio.wait([client.send(message) for client in CLIENTS])

async def register_client(websocket):
    CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTS.remove(websocket)

async def websocket_server(websocket, path):
    # Register client connection
    await register_client(websocket)

async def main():
    # Start the WebSocket server
    start_server = websockets.serve(websocket_server, "localhost", 6789)
    
    # Run the server and the subscriber concurrently
    await asyncio.gather(
        start_server,
        source_subscriber(SOURCE_WS_URL),
    )

if __name__ == "__main__":
    asyncio.run(main())
