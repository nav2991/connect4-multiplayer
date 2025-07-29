from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game import Connect4Game

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

game = Connect4Game()
player1_socket = None
player2_socket = None


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global player1_socket, player2_socket
    await websocket.accept()
    print("🔌 WebSocket connected!")

    if player1_socket is None:
        player1_socket = websocket
        player_id = 1
    elif player2_socket is None:
        player2_socket = websocket
        player_id = 2
    else:
        await websocket.send_json({"error": "Game is full"})
        await websocket.close()
        return

    await websocket.send_json({"player": player_id, "current_player": game.current_player})

    while True:
        try:
            data = await websocket.receive_json()

            if game.is_game_over:
                await websocket.send_json(game.get_state())
                continue

            if data.get("action") == "drop" and data.get("player") == game.current_player:
                game.make_move(data["column"])
                game.check_winner()

                if not game.is_game_over:
                    game.switch_turn()

            for player_ws in [player1_socket, player2_socket]:
                if player_ws:
                    await player_ws.send_json(game.get_state())

        except WebSocketDisconnect:
            if websocket is player1_socket:
                print("WebSocket 1 disconnected!")
                player1_socket = None
            elif websocket is player2_socket:
                print("WebSocket 2 disconnected!")
                player2_socket = None
            break
