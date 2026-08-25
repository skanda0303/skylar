import os
import requests
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from backend.resilience_engine import DataResilienceEngine

MONDAY_API_URL = "https://api.monday.com/v2"

class MondayClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("MONDAY_API_TOKEN", "")
        self.deals_file = "Deal_funnel_Data.xlsx"
        self.wo_file = "Work_Order_Tracker_Data.xlsx"

    def is_connected(self) -> bool:
        if not self.api_token:
            return False
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        query = "{ me { id name email } }"
        try:
            res = requests.post(MONDAY_API_URL, json={"query": query}, headers=headers, timeout=5)
            return res.status_code == 200 and "data" in res.json()
        except Exception:
            return False

    def fetch_monday_board(self, board_id: str) -> Optional[List[Dict[str, Any]]]:
        if not self.api_token:
            return None
        headers = {
            "Authorization": self.api_token,
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
                    return records
        except Exception as e:
            print(f"Error querying Monday.com API: {e}")
        return None

    def get_all_data(self, deals_board_id: Optional[str] = None, wo_board_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Dynamically fetches dataset. If board IDs and API token are available,
        queries Monday.com directly. Otherwise, loads from local dataset mirror
        and applies the DataResilienceEngine.
        """
        source = "Local Dataset Mirror (Data Resilience Engine Active)"
        
        deals_raw = None
        wo_raw = None

        if self.api_token and deals_board_id and wo_board_id:
            m_deals = self.fetch_monday_board(deals_board_id)
            m_wo = self.fetch_monday_board(wo_board_id)
            if m_deals and m_wo:
                deals_raw = pd.DataFrame(m_deals)
                wo_raw = pd.DataFrame(m_wo)
                source = f"Live Monday.com GraphQL API (Board IDs: {deals_board_id}, {wo_board_id})"

        if deals_raw is None or wo_raw is None:
            cleaned_res = DataResilienceEngine.load_and_clean_all(self.deals_file, self.wo_file)
            cleaned_res["data_source"] = source
            return cleaned_res

        cleaned_deals, deals_audit = DataResilienceEngine.clean_deals_data(deals_raw)
        cleaned_wo, wo_audit = DataResilienceEngine.clean_work_orders_data(wo_raw)

        return {
            'deals': cleaned_deals,
            'work_orders': cleaned_wo,
            'deals_audit': deals_audit,
            'work_orders_audit': wo_audit,
            'data_source': source
        }
