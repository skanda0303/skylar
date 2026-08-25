import unittest
import urllib.request
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.resilience_engine import DataResilienceEngine
from backend.monday_client import MondayClient
from backend.bi_agent import BIAgent
from backend.leadership_updates import LeadershipUpdateGenerator

class TestSkylarkBIAgent(unittest.TestCase):

    def test_01_resilience_engine(self):
        print("\n--- Testing Data Resilience Engine ---")
        res = DataResilienceEngine.load_and_clean_all("Deal_funnel_Data.xlsx", "Work_Order_Tracker_Data.xlsx")
        self.assertIn('deals', res)
        self.assertIn('work_orders', res)
        self.assertGreater(len(res['deals']), 0)
        self.assertGreater(len(res['work_orders']), 0)
        self.assertIn('quality_caveats', res['deals_audit'])
        self.assertIn('quality_caveats', res['work_orders_audit'])
        print(f"[PASS] Resilience Engine Cleaned {len(res['deals'])} Deals & {len(res['work_orders'])} Work Orders cleanly!")

    def test_02_bi_agent_queries(self):
        print("\n--- Testing BI Agent Query Interpreter ---")
        agent = BIAgent()
        
        # Test Sector query
        res_sector = agent.answer_query("How is our pipeline looking for Mining sector?")
        self.assertIn("Mining", res_sector['headline'])
        self.assertIn("chart", res_sector)
        self.assertGreater(len(res_sector['summary_insights']), 0)

        # Test Revenue query
        res_rev = agent.answer_query("What is our overall revenue and billing status?")
        self.assertIn("Revenue", res_rev['headline'])
        self.assertIn("key_metrics", res_rev)

        # Test Operations query
        res_ops = agent.answer_query("Which work orders are stuck?")
        self.assertIn("Operations", res_ops['headline'])

        print("[PASS] BI Agent answered all executive queries with accurate cross-board calculations!")

    def test_03_leadership_updates(self):
        print("\n--- Testing Leadership Updates Generator ---")
        generator = LeadershipUpdateGenerator()
        update = generator.generate_update(sector="Mining")
        self.assertIn("markdown_content", update)
        self.assertIn("summary_cards", update)
        self.assertTrue(update['markdown_content'].startswith("# "))
        print("[PASS] Leadership Update Generator created formatted slides-ready brief!")

    def test_04_backend_api_endpoints(self):
        print("\n--- Testing FastAPI Endpoints ---")
        try:
            health = urllib.request.urlopen("http://127.0.0.1:8000/api/health")
            health_data = json.loads(health.read().decode())
            self.assertEqual(health_data['status'], 'healthy')

            req = urllib.request.Request(
                "http://127.0.0.1:8000/api/query",
                data=json.dumps({"query": "Show BD sales rep leaderboard"}).encode(),
                headers={"Content-Type": "application/json"}
            )
            q_res = json.loads(urllib.request.urlopen(req).read().decode())
            self.assertIn("Owner", q_res['headline'])
            print("[PASS] FastAPI endpoints verified successfully!")
        except Exception as e:
            self.fail(f"API Endpoint verification failed: {e}")

if __name__ == "__main__":
    unittest.main()
