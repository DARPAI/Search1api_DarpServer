from typing import Any, List, Optional
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
import urllib.parse
import json
import uvicorn
from dotenv import load_dotenv
import os
 
load_dotenv()

API_BASE = "api.search1api.com"
API_KEY = os.getenv("SEARCH1API_KEY")

server = Server("search1api")
sse = SseServerTransport("/messages/")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for search and crawling functionality."""
    return [
        types.Tool(
            name="search",
            description="A fast way to search the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "search_service": {
                        "type": "string",
                        "description": "Search service to use (default: google)",
                        "default": "google"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="news",
            description="Search for news articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "News search query"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "search_service": {
                        "type": "string",
                        "description": "Search service to use (default: google)",
                        "default": "google"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="crawl",
            description="Extract content from URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to crawl"
                    }
                },
                "required": ["url"]
            }
        ),
        # types.Tool(
        #     name="sitemap",
        #     description="Get all related links from a URL",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "url": {
        #                 "type": "string",
        #                 "description": "URL to get sitemap"
        #             }
        #         },
        #         "required": ["url"]
        #     }
        # )
    ]

async def make_search_request(client: httpx.AsyncClient, endpoint: str, data: dict) -> dict[str, Any] | None:
    """Make a request to the Search API with proper error handling."""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        response = await client.post(
            f"https://{API_BASE}{endpoint}",
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API request error: {str(e)}")
        return None

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Currently supported tools:
    - search: performs web search
    - news: searches news articles
    - crawl: extracts content from URLs
    - sitemap: gets site structure
    """
    
    if arguments is None:
        return [types.TextContent(type="text", text="No arguments provided")]

    async with httpx.AsyncClient() as client:
        if name == "search":
            if "query" not in arguments:
                return [types.TextContent(type="text", text="Search query is required")]

            request_data = {
                "query": arguments["query"],
                "max_results": arguments.get("max_results", 10),
                "search_service": arguments.get("search_service", "google")
            }

            search_data = await make_search_request(client, "/search", request_data)
            
            if not search_data:
                return [types.TextContent(type="text", text="Failed to retrieve search results")]

            return [types.TextContent(type="text", text=json.dumps(search_data["results"]))]

        elif name == "news":
            if "query" not in arguments:
                return [types.TextContent(type="text", text="News search query is required")]

            request_data = {
                "query": arguments["query"],
                "max_results": arguments.get("max_results", 10),
                "search_service": arguments.get("search_service", "google")
            }

            news_data = await make_search_request(client, "/news", request_data)
            
            if not news_data:
                return [types.TextContent(type="text", text="Failed to retrieve news results")]

            return [types.TextContent(type="text", text=json.dumps(news_data["results"]))]

        elif name == "crawl":
            if "url" not in arguments:
                return [types.TextContent(type="text", text="URL is required")]

            request_data = {"url": arguments["url"]}
            
            crawl_data = await make_search_request(client, "/crawl", request_data)
            
            if not crawl_data:
                return [types.TextContent(type="text", text="Failed to crawl URL")]

            return [types.TextContent(type="text", text=json.dumps(crawl_data["results"]))]

        elif name == "sitemap":
            if "url" not in arguments:
                return [types.TextContent(type="text", text="URL is required")]

            request_data = {"url": arguments["url"]}
            
            sitemap_data = await make_search_request(client, "/sitemap", request_data)
            
            if not sitemap_data:
                return [types.TextContent(type="text", text="Failed to retrieve sitemap")]

            return [types.TextContent(type="text", text=json.dumps(sitemap_data["links"]))]

        else:
            raise ValueError(f"Unknown tool: {name}")

async def handle_sse(request):
    """Handle SSE connection requests"""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

routes = [
    Route("/sse", endpoint=handle_sse),
    Mount("/messages/", app=sse.handle_post_message),
]

app = Starlette(routes=routes, debug=True)

def start_server(host: str = "0.0.0.0", port: int = 3001):
    """Start the server with the API key from environment variables"""
    if not API_KEY:
        raise ValueError("SEARCH1API_KEY environment variable is not set")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()