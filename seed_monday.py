import os
import sys
import requests
import json
import pandas as pd

def seed_monday(api_token: str):
    """
    Creates two boards on Monday.com:
    1. Skylark Deals Board
    2. Skylark Work Orders Board
    And populates them with rows from the Excel files.
    """
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }

    def create_board(board_name: str) -> str:
        query = """
        mutation CreateBoard($name: String!) {
            create_board(board_name: $name, board_kind: public) {
                id
            }
        }
        """
        res = requests.post("https://api.monday.com/v2", json={"query": query, "variables": {"name": board_name}}, headers=headers)
        data = res.json()
        board_id = data.get("data", {}).get("create_board", {}).get("id")
        print(f"Created board '{board_name}' with ID: {board_id}")
        return board_id

    def create_item(board_id: str, item_name: str):
        query = """
        mutation CreateItem($board_id: ID!, $item_name: String!) {
            create_item(board_id: $board_id, item_name: $item_name) {
                id
            }
        }
        """
        requests.post("https://api.monday.com/v2", json={"query": query, "variables": {"board_id": board_id, "item_name": item_name}}, headers=headers)

    print("--- Seeding Monday.com Boards ---")
    
    # 1. Deals Board
    deals_df = pd.read_excel("Deal_funnel_Data.xlsx", sheet_name="Deal tracker")
    deals_board_id = create_board("Skylark Deals Funnel")
    if deals_board_id:
        print("Populating Deals items...")
        for _, row in deals_df.head(50).iterrows(): # seed first 50 rows
            name = str(row.get('Deal Name', 'Unnamed Deal'))
            create_item(deals_board_id, name)
            
    # 2. Work Orders Board
    wo_df = pd.read_excel("Work_Order_Tracker_Data.xlsx", sheet_name="work order tracker")
    wo_df.columns = wo_df.iloc[0]
    wo_df = wo_df[1:].reset_index(drop=True)
    wo_board_id = create_board("Skylark Work Orders Tracker")
    if wo_board_id:
        print("Populating Work Orders items...")
        for _, row in wo_df.head(50).iterrows():
            name = str(row.get('Deal name masked', 'Unnamed Work Order'))
            create_item(wo_board_id, name)

    print("\n--- Seeding Complete! ---")
    print(f"Deals Board ID: {deals_board_id}")
    print(f"Work Orders Board ID: {wo_board_id}")
    return deals_board_id, wo_board_id

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MONDAY_API_TOKEN", "")
    if not token:
        print("Usage: python seed_monday.py <MONDAY_API_TOKEN>")
        sys.exit(1)
    seed_monday(token)
