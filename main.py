# main.py
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import chess
import json
import asyncio

app = FastAPI()
board = chess.Board()

@app.get("/sse")
async def sse():
    async def event_generator():
        while True:
            await asyncio.sleep(1)
            yield {
                "event": "ping",
                "data": "alive"
            }

    return EventSourceResponse(event_generator())


@app.post("/start_game")
async def start_game():
    global board
    board = chess.Board()
    return {"status": "game_started", "fen": board.fen()}


@app.post("/make_move")
async def make_move(move: str):
    global board
    try:
        board.push_san(move)
        return {
            "status": "move_played",
            "fen": board.fen(),
            "board": str(board)
        }
    except:
        return {"error": "invalid_move"}


@app.get("/get_board")
async def get_board():
    return {
        "fen": board.fen(),
        "board": str(board)
    }