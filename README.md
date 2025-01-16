# 🔍 Search1api DarpServer

A powerful server implementation that provides real-time search capabilities through DARP, integrating with Search1API services.

## ✨ Features

### Search Capabilities
- 🌐 Web Search - Fast and comprehensive web search functionality
- 📰 News Search - Real-time news article search


## 🛠️ Prerequisites

This project uses [uv](https://docs.astral.sh/uv) for package management.

### Installing UV

**Unix-like systems (Linux/macOS):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installing Dependencies
```bash
uv pip install -r requirements.txt
```

## ⚙️ Environment Setup

1. Create a `.env` file in the root directory:
```bash
SEARCH1API_KEY=your-api-key  # Required for all API operations
```

## 🚀 Running the Server

Start the server (default port: 3001):
```bash
cd search1api-mcp-main
uv run ./server.py
```



### Search Tool
- Query web search results
- Configurable max results (1-50)
- Multiple search service options

### News Tool
- Search news articles
- Customizable result limit
- Multiple news source options



## 📝 Notes
- Server runs on `0.0.0.0:3001` by default
- Requires valid Search1API key for all operations
- Implements proper error handling and request timeouts

