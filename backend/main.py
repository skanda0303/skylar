import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.monday_client import MondayClient
from backend.bi_agent import BIAgent
from backend.leadership_updates import LeadershipUpdateGenerator
from backend.resilience_engine import DataResilienceEngine

app = FastAPI(
    title="Skylark Drones - Monday.com Business Intelligence Agent",
    description="AI Agent & Executive BI system for Monday.com Work Orders & Deals",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class QueryRequest(BaseModel):
    query: str
    deals_board_id: Optional[str] = None
    wo_board_id: Optional[str] = None
    api_token: Optional[str] = None

class LeadershipRequest(BaseModel):
    report_type: Optional[str] = "executive"
    sector: Optional[str] = "All"
    deals_board_id: Optional[str] = None
    wo_board_id: Optional[str] = None
    api_token: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Monday.com BI Agent Backend",
        "resilience_engine": "Active"
    }

@app.post("/api/query")
def process_query(req: QueryRequest):
    client = MondayClient(api_token=req.api_token)
    agent = BIAgent(monday_client=client)
    res = agent.answer_query(req.query, deals_board_id=req.deals_board_id, wo_board_id=req.wo_board_id)
    return res

@app.post("/api/leadership-update")
def generate_leadership_update(req: LeadershipRequest):
    client = MondayClient(api_token=req.api_token)
    generator = LeadershipUpdateGenerator(monday_client=client)
    res = generator.generate_update(
        report_type=req.report_type or "executive",
        sector=req.sector,
        deals_board_id=req.deals_board_id,
        wo_board_id=req.wo_board_id
    )
    return res

@app.get("/api/boards")
def get_boards_data(api_token: Optional[str] = None, deals_board_id: Optional[str] = None, wo_board_id: Optional[str] = None):
    client = MondayClient(api_token=api_token)
    data = client.get_all_data(deals_board_id, wo_board_id)
    
    # Convert DataFrames to JSON-serializable list of dicts
    deals_records = data['deals'].fillna("").to_dict(orient="records")
    wo_records = data['work_orders'].fillna("").to_dict(orient="records")

    return {
        "data_source": data.get("data_source"),
        "deals_count": len(deals_records),
        "wo_count": len(wo_records),
        "deals_audit": data['deals_audit'],
        "wo_audit": data['work_orders_audit'],
        "deals": deals_records[:100], # return first 100 for UI table view
        "work_orders": wo_records[:100]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
