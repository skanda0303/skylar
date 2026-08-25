import sys
import os
import json
import asyncio
import requests
from typing import Optional, Dict, Any, List

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.monday_client import MondayClient
from backend.bi_agent import BIAgent

MONDAY_API_URL = "https://api.monday.com/v2"

server = Server("monday-mcp-server")

async def handle_list_tools(req: types.ListToolsRequest) -> types.ListToolsResult:
    """List available Monday.com MCP tools."""
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="get_monday_board",
                description="Fetch items and column data from a Monday.com board using GraphQL v2 API.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board_id": {
                            "type": "string",
                            "description": "Monday.com Board ID to fetch items from"
                        },
                        "api_token": {
                            "type": "string",
                            "description": "Optional Monday.com API Token"
                        }
                    },
                    "required": ["board_id"]
                }
            ),
            types.Tool(
                name="query_monday_bi",
                description="Execute natural language business intelligence queries across Monday.com Work Orders and Deals boards.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Executive query string (e.g., 'How is Mining sector pipeline looking?')"
                        },
                        "deals_board_id": {
                            "type": "string",
                            "description": "Optional Deals Board ID"
                        },
                        "wo_board_id": {
                            "type": "string",
                            "description": "Optional Work Orders Board ID"
                        },
                        "api_token": {
                            "type": "string",
                            "description": "Optional Monday.com API Token"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    )

async def handle_call_tool(req: types.CallToolRequest) -> types.CallToolResult:
    """Execute Monday.com MCP tools."""
    name = req.name
    arguments = req.arguments or {}

    if name == "get_monday_board":
        board_id = arguments.get("board_id", "")
        token = arguments.get("api_token") or os.getenv("MONDAY_API_TOKEN", "")

        if not token:
            res_str = json.dumps({
                "status": "error",
                "message": "Monday.com API token not provided. Pass api_token or set MONDAY_API_TOKEN environment variable."
            })
        else:
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "API-Version": "2023-10"
            }
            query = """
            query GetBoardData($board_id: [ID!]) {
                boards(ids: $board_id) {
                    id
                    name
                    columns { id title type }
                    items_page(limit: 500) {
                        items {
                            id
                            name
                            column_values { id text value }
                        }
                    }
                }
            }
            """
            try:
                res = requests.post(MONDAY_API_URL, json={"query": query, "variables": {"board_id": [board_id]}}, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    boards = data.get("data", {}).get("boards", [])
                    if boards:
                        items = boards[0].get("items_page", {}).get("items", [])
                        records = []
                        for item in items:
                            rec = {"Item Name": item.get("name")}
                            for cv in item.get("column_values", []):
                                rec[cv.get("id")] = cv.get("text")
                            records.append(rec)
                        res_str = json.dumps({"status": "success", "board_id": board_id, "item_count": len(records), "items": records})
                    else:
                        res_str = json.dumps({"status": "error", "message": "No board found"})
                else:
                    res_str = json.dumps({"status": "error", "message": f"HTTP {res.status_code}"})
            except Exception as e:
                res_str = json.dumps({"status": "error", "message": str(e)})

        return types.CallToolResult(content=[types.TextContent(type="text", text=res_str)])

    elif name == "query_monday_bi":
        query = arguments.get("query", "")
        deals_board_id = arguments.get("deals_board_id")
        wo_board_id = arguments.get("wo_board_id")
        token = arguments.get("api_token")

        client = MondayClient(api_token=token)
        agent = BIAgent(monday_client=client)
        res_data = agent.answer_query(query, deals_board_id=deals_board_id, wo_board_id=wo_board_id)
        return types.CallToolResult(content=[types.TextContent(type="text", text=json.dumps(res_data, indent=2))])

    else:
        raise ValueError(f"Unknown tool: {name}")

# Register MCP request handlers
server.add_request_handler("tools/list", types.ListToolsRequest, handle_list_tools)
server.add_request_handler("tools/call", types.CallToolRequest, handle_call_tool)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
