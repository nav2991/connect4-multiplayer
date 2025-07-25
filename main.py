from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game import Connect4Game

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket connected!")

    while True:
        try:
            data = await websocket.receive_text()

            print(f"Received: {data}")

            await websocket.send_text(f"Echo: {data}")

        except WebSocketDisconnect:
            print("WebSocket disconnected!")
            break

test_game = Connect4Game()
