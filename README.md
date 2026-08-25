# Skylark Drones - Monday.com Business Intelligence Agent & MCP Server

An AI-powered Business Intelligence Agent, Dedicated MCP Server, and Executive Dashboard that integrates with Monday.com boards (Deals & Work Orders), normalizes messy data, handles data resilience, answers founder-level queries across boards, and generates leadership updates.

---

## 🌟 Key Features

1. **Monday.com MCP Server (`monday_mcp_server.py`)**:
   - Standalone Model Context Protocol (MCP) server adhering to the official MCP specification using stdio transport.
   - Exposes tools:
     - `get_monday_board`: Fetch board items and column data directly via Monday.com GraphQL API v2.
     - `query_monday_bi`: Execute cross-board natural language BI queries.
   - Includes `mcp_config.json` for registration with Claude Code, Cursor, Antigravity, or Gemini CLI.

2. **Monday.com GraphQL API Integration**:
   - Live GraphQL API v2 client (`backend/monday_client.py`).
   - Includes `seed_monday.py` script to create and populate Monday.com boards programmatically.
   - Dynamic mirror fallback powered by the Data Resilience Engine for local testing without API keys.

3. **Data Resilience & Normalization Engine**:
   - Standardizes date formats across formats and text strings.
   - Cleans sector names (`Mining`, `Powerline`, `Renewables`, `Railways`, `Construction`, etc.).
   - Handles missing values gracefully (imputing missing deal values to ₹0 for safe aggregations).
   - Generates explicit **Data Resilience Audit Warnings** for executive transparency.

4. **Minimalist Executive BI Dashboard (`frontend/`)**:
   - Built following **UI/UX Pro Max** and **Taste Skill** anti-slop principles.
   - High legibility, tabular financial metrics, crisp borders, clean navigation, and concise executive reports.

---

## 📁 Repository Structure

```
skylark_drones/
├── monday_mcp_server.py        # Dedicated Model Context Protocol (MCP) Server
├── mcp_config.json             # MCP Client registration config
├── backend/
│   ├── main.py                 # FastAPI backend endpoints
│   ├── monday_client.py        # Monday.com GraphQL v2 client
│   ├── resilience_engine.py    # Data cleaning & resilience engine
│   ├── bi_agent.py             # Founder BI query interpreter & aggregator
│   └── leadership_updates.py   # Executive brief generator
├── frontend/
│   ├── src/
│   │   ├── components/         # React UI components (Header, Chat, Explorer, Leadership)
│   │   ├── App.jsx             # Main dashboard layout
│   │   └── index.css           # Minimalist design system
│   ├── package.json
│   └── vite.config.js
├── Deal_funnel_Data.xlsx       # Sample Deals dataset
├── Work_Order_Tracker_Data.xlsx# Sample Work Orders dataset
├── seed_monday.py              # Script to seed Monday.com boards
├── test_suite.py               # End-to-end automated test suite
├── package_submission.py       # Submission ZIP packager
├── DECISION_LOG.md             # Decision log document
└── README.md                   # Setup & architecture guide
```

---

## 🔌 Using the Monday.com MCP Server

To use the Monday.com MCP server with any MCP client host (Claude, Cursor, Antigravity, etc.):

```json
{
  "mcpServers": {
    "monday-mcp-server": {
      "command": "python",
      "args": ["monday_mcp_server.py"],
      "env": {
        "MONDAY_API_TOKEN": "YOUR_MONDAY_API_TOKEN"
      }
    }
  }
}
```

---

## 🚀 Setup & Installation Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Install dependencies
pip install openpyxl pandas fastapi uvicorn requests pydantic python-dotenv mcp

# Launch FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Backend API will be live at `http://127.0.0.1:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 🧪 Running Automated Tests

Run the full test suite:
```bash
python test_suite.py
```
