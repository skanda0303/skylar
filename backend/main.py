import sys
import os
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.monday_client import MondayClient
from backend.bi_agent import BIAgent
from backend.leadership_updates import LeadershipUpdateGenerator
from backend.resilience_engine import DataResilienceEngine
from backend.composio_integration import ComposioIntegration

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

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    print(f"[API ERROR] Exception on {request.url.path}: {error_msg}\n{stack_trace}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_type": type(exc).__name__,
            "message": f"Internal Server Error: {error_msg}",
            "path": request.url.path
        }
    )

# Request Models
class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language executive query string")
    deals_board_id: Optional[str] = None
    wo_board_id: Optional[str] = None
    api_token: Optional[str] = None

class LeadershipRequest(BaseModel):
    report_type: Optional[str] = "executive"
    sector: Optional[str] = "All"
    deals_board_id: Optional[str] = None
    wo_board_id: Optional[str] = None
    api_token: Optional[str] = None

class ComposioSlackRequest(BaseModel):
    channel: Optional[str] = "executive-alerts"
    message: str

class ComposioEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    body_markdown: str

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Monday.com BI Agent Backend",
        "resilience_engine": "Active",
        "composio_integration": "Ready"
    }

@app.post("/api/query")
def process_query(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    try:
        client = MondayClient(api_token=req.api_token)
        agent = BIAgent(monday_client=client)
        res = agent.answer_query(req.query, deals_board_id=req.deals_board_id, wo_board_id=req.wo_board_id)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query Processing Failure: {str(e)}"
        )

@app.post("/api/leadership-update")
def generate_leadership_update(req: LeadershipRequest):
    try:
        client = MondayClient(api_token=req.api_token)
        generator = LeadershipUpdateGenerator(monday_client=client)
        res = generator.generate_update(
            report_type=req.report_type or "executive",
            sector=req.sector or "All",
            deals_board_id=req.deals_board_id,
            wo_board_id=req.wo_board_id
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Leadership Report Generation Failure: {str(e)}"
        )

@app.get("/api/boards")
def get_boards_data(api_token: Optional[str] = None, deals_board_id: Optional[str] = None, wo_board_id: Optional[str] = None):
    try:
        client = MondayClient(api_token=api_token)
        data = client.get_all_data(deals_board_id, wo_board_id)
        
        deals_records = data['deals'].fillna("").to_dict(orient="records")
        wo_records = data['work_orders'].fillna("").to_dict(orient="records")

        return {
            "data_source": data.get("data_source"),
            "deals_count": len(deals_records),
            "wo_count": len(wo_records),
            "deals_audit": data['deals_audit'],
            "wo_audit": data['work_orders_audit'],
            "deals": deals_records[:100],
            "work_orders": wo_records[:100]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Board Data Fetch Error: {str(e)}"
        )

@app.post("/api/composio/slack")
def dispatch_composio_slack(req: ComposioSlackRequest):
    composio = ComposioIntegration()
    return composio.dispatch_slack_alert(req.channel or "executive-alerts", req.message)

@app.post("/api/composio/email")
def dispatch_composio_email(req: ComposioEmailRequest):
    composio = ComposioIntegration()
    return composio.dispatch_email_brief(req.recipient_email, req.subject, req.body_markdown)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
