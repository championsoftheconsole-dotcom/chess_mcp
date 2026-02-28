import json
import chess
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()
board = chess.Board()


async def event_stream():
    init_message = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        }
    }

    yield "data: " + json.dumps(init_message) + "\n\n"


@app.get("/sse")
async def sse():
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/")
async def rpc_endpoint(request: Request):
    global board

    body = await request.json()
    method = body.get("method")
    id_ = body.get("id")
    params = body.get("params", {})

    if method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "start_game",
                    "description": "Start a new chess game",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "make_move",
                    "description": "Make move in SAN format",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "move": {"type": "string"}
                        },
                        "required": ["move"]
                    }
                },
                {
                    "name": "get_board",
                    "description": "Get board state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }

    elif method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})

        if tool == "start_game":
            board = chess.Board()
            result = {"fen": board.fen()}

        elif tool == "make_move":
            try:
                board.push_san(args["move"])
                result = {"fen": board.fen(), "board": str(board)}
            except Exception as e:
                result = {"error": str(e)}

        elif tool == "get_board":
            result = {"fen": board.fen(), "board": str(board)}

        else:
            result = {"error": "Unknown tool"}

    else:
        result = {"error": "Unknown method"}

    return {
        "jsonrpc": "2.0",
        "id": id_,
        "result": result
    }
