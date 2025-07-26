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

    game = Connect4Game()

    while True:
        try:
            data = await websocket.receive_json()

            if game.is_game_over:
                await websocket.send_json(game.get_state())
                continue

            if data["action"] == "drop":
                game.make_move(data["column"] - 1)
                game.check_winner()

            if not game.is_game_over:
                game.switch_turn()

            await websocket.send_json(game.get_state())

        except WebSocketDisconnect:
            print("WebSocket disconnected!")
            break
