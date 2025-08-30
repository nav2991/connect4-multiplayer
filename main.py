import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game import Connect4Game

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

rooms = {} # {room_id: {"game": Connect4Game(), "players": [ws1, ws2]}}
lobby_clients = set()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/game")
def read_game():
    return FileResponse("static/connect4.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    lobby_clients.add(websocket)
    print("WebSocket connected (lobby)")

    await websocket.send_json({
        "type": "room_list",
        "rooms": list(rooms.keys())
    })

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "create_room":
                room_id = str(len(rooms) + 1)
                rooms[room_id] = {"game": Connect4Game(), "players": []}

                # Broadcast the updated list to everyone
                await broadcast(lobby_clients, {
                    "type": "room_list",
                    "rooms": list(rooms.keys())
                })
                
            elif action == "join_room":
                room_id = data.get("room_id")
                if room_id in rooms:
                    room = rooms[room_id]
                    if len(room["players"]) < 2:
                        player_num = len(room["players"]) + 1
                        room["players"].append(websocket)
                        
                        await websocket.send_json({
                            "type": "join_success",
                            "player": player_num,
                            "room_id": room_id
                        })
                        
                        if len(room["players"]) == 2:
                            await broadcast(room["players"], {
                                "type": "game_start",
                                "board": room["game"].board,
                                "current_player": room["game"].current_player
                            })
                    else:
                        await websocket.send_json({
                            "type": "join_error",
                            "message": "Room is full"
                        })

    except WebSocketDisconnect:
        lobby_clients.discard(websocket)
        print("WebSocket disconnected (lobby)")


@app.websocket("/ws/connect4/{room_id}/{player_id}")
async def connect4_websocket(websocket: WebSocket, room_id: str, player_id: int):
    await websocket.accept()
    print(f"WebSocket connected (connect4) - Room: {room_id}, Player: {player_id}")
    
    if room_id not in rooms:
        await websocket.close(code=4004, reason="Room not found")
        return
    
    room = rooms[room_id]
    if player_id < 1 or player_id > 2:
        await websocket.close(code=4005, reason="Invalid player ID")
        return
    
    room["players"][player_id - 1] = websocket
    
    await websocket.send_json(room["game"].get_state())
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "drop":
                if len(room["players"]) < 2:
                    await websocket.send_json({"error": "Waiting for second player to join"})
                    continue
                
                if room["game"].is_game_over:
                    await websocket.send_json(room["game"].get_state())
                    continue

                if data.get("action") == "drop" and data.get("player") == room["game"].current_player:
                    room["game"].make_move(data["column"])
                    room["game"].check_winner()

                    if not room["game"].is_game_over:
                        room["game"].switch_turn()

                    await broadcast(room["players"], room["game"].get_state())
            
    except WebSocketDisconnect:
        if room_id in rooms:
            room = rooms[room_id]
            if websocket in room["players"]:
                room["players"].remove(websocket)
                print(f"Player {player_id} disconnected from game room {room_id}")
                
                if len(room["players"]) == 0:
                    del rooms[room_id]
                    print(f"Game room {room_id} removed (no players left)")

async def broadcast(targets, message: dict):
    if targets:
        msg_json = json.dumps(message)
        for ws in list(targets):
            try:
                await ws.send_text(msg_json)
            except:
                targets.discard(ws)
