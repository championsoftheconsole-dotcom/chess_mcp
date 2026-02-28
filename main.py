from mcp.server.fastapi import FastAPIMCP
import chess

# Create chess board instance
board = chess.Board()

# Create MCP server
mcp = FastAPIMCP("Chess MCP Server")

@mcp.tool()
def start_game():
    """
    Start a new chess game.
    """
    global board
    board = chess.Board()
    return {
        "status": "game_started",
        "fen": board.fen()
    }

@mcp.tool()
def make_move(move: str):
    """
    Make a chess move using SAN notation (e4, Nf3, etc.)
    """
    global board
    try:
        board.push_san(move)
        return {
            "status": "move_played",
            "fen": board.fen(),
            "board": str(board)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Invalid move: {str(e)}"
        }

@mcp.tool()
def get_board():
    """
    Get current board state.
    """
    return {
        "fen": board.fen(),
        "board": str(board)
    }

# FastAPI app exposed for Railway
app = mcp.app
