import json
import asyncio
import chess
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()
board = chess.Board()

# -----------------------------
# SSE Endpoint (MCP Transport)
# -----------------------------
async def event_stream():
    while True:
        # Send heartbeat to keep connection alive
        yield ":\n\n"
        await asyncio.sleep(15)


@app.get("/sse")
async def sse():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


# -----------------------------
# JSON-RPC Endpoint
# -----------------------------
@app.post("/")
async def rpc_endpoint(request: Request):
    global board

    body = await request.json()
    method = body.get("method")
    id_ = body.get("id")
    params = body.get("params", {})

    # ---- Initialize ----
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        }

    # ---- List Tools ----
    elif method == "tools/list":
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
                    "description": "Make move in SAN format (e4, Nf3, etc.)",
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
                    "description": "Get current board state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }

    # ---- Call Tool ----
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "start_game":
            board = chess.Board()
            result = {"fen": board.fen()}

        elif tool_name == "make_move":
            try:
                board.push_san(args["move"])
                result = {
                    "fen": board.fen(),
                    "board": str(board)
                }
            except Exception as e:
                result = {"error": str(e)}

        elif tool_name == "get_board":
            result = {
                "fen": board.fen(),
                "board": str(board)
            }

        else:
            result = {"error": "Unknown tool"}

    else:
        result = {"error": "Unknown method"}

    return {
        "jsonrpc": "2.0",
        "id": id_,
        "result": result
    }
