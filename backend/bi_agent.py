import os
import json
import requests
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from backend.monday_client import MondayClient

def format_inr(val: float) -> str:
    """Formats numeric values into clean Indian financial notation (Crores / Lakhs)."""
    if abs(val) >= 1e7:
        return f"₹{val / 1e7:,.2f} Cr"
    elif abs(val) >= 1e5:
        return f"₹{val / 1e5:,.2f} L"
    else:
        return f"₹{val:,.2f}"

class BIAgent:
    """
    Founder-level Business Intelligence Agent.
    Interprets executive queries, joins Deals and Work Orders boards,
    computes key metrics (Revenue, Pipeline Health, Operational Performance, Sector Breakdown),
    includes data quality caveats, and supports optional AI model synthesis (Google Gemini / OpenAI).
    """

    def __init__(self, monday_client: Optional[MondayClient] = None):
        self.client = monday_client or MondayClient()

    def answer_query(self, user_query: str, deals_board_id: Optional[str] = None, wo_board_id: Optional[str] = None) -> Dict[str, Any]:
        data = self.client.get_all_data(deals_board_id, wo_board_id)
        deals_df = data['deals']
        wo_df = data['work_orders']
        deals_audit = data['deals_audit']
        wo_audit = data['work_orders_audit']
        data_source = data.get('data_source', 'Local Dataset Mirror')

        query_lower = user_query.lower()

        # Combine caveats
        all_caveats = deals_audit['quality_caveats'] + wo_audit['quality_caveats']

        # Core analytics calculation using Data Resilience Engine
        if any(w in query_lower for w in ['sector', 'energy', 'mining', 'powerline', 'renewables', 'railways']):
            base_res = self._handle_sector_query(user_query, query_lower, deals_df, wo_df, all_caveats, data_source)
        elif any(w in query_lower for w in ['pipeline', 'stage', 'funnel', 'probability', 'conversion']):
            base_res = self._handle_pipeline_query(user_query, deals_df, wo_df, all_caveats, data_source)
        elif any(w in query_lower for w in ['revenue', 'billing', 'billed', 'collected', 'unbilled', 'receivable', 'money']):
            base_res = self._handle_revenue_query(user_query, deals_df, wo_df, all_caveats, data_source)
        elif any(w in query_lower for w in ['operations', 'operational', 'bottleneck', 'stuck', 'execution', 'software', 'spectra', 'dmo']):
            base_res = self._handle_operations_query(user_query, wo_df, deals_df, all_caveats, data_source)
        elif any(w in query_lower for w in ['owner', 'bd', 'kam', 'team', 'personnel', 'rep']):
            base_res = self._handle_owner_query(user_query, deals_df, wo_df, all_caveats, data_source)
        else:
            base_res = self._handle_overview_query(user_query, deals_df, wo_df, all_caveats, data_source)

        # Check for Google Gemini API Key first
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                prompt_text = f"""You are an Executive Business Intelligence AI Agent for Skylark Drones.
The user asked: "{user_query}"
Here are the exact calculated financial metrics:
{json.dumps(base_res.get('key_metrics', {}), indent=2)}

Original calculated insights:
{json.dumps(base_res.get('summary_insights', []), indent=2)}

Please refine these insights into clean bullet points with bold financial figures formatted in Crores (Cr) or Lakhs (L). Return ONLY JSON format like: {{"summary_insights": ["insight 1", "insight 2"]}}."""

                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                headers = {"Content-Type": "application/json"}
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    raw_text = resp_json['candidates'][0]['content']['parts'][0]['text']
                    parsed = json.loads(raw_text)
                    if "summary_insights" in parsed and isinstance(parsed["summary_insights"], list):
                        base_res["summary_insights"] = parsed["summary_insights"]
                        base_res["data_source"] = f"{data_source} + Gemini AI Synthesis"
            except Exception as e:
                print("Gemini API fallback to local engine:", e)

        # Fallback check for OpenAI API Key if Gemini is not present
        elif os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                prompt = f"""You are an Executive Business Intelligence AI Agent for Skylark Drones.
The user asked: "{user_query}"
Here are the exact computed financial metrics:
{json.dumps(base_res.get('key_metrics', {}), indent=2)}

Original calculated insights:
{json.dumps(base_res.get('summary_insights', []), indent=2)}

Please refine these summary insights into bullet points with bold financial values in Crores (Cr) or Lakhs (L). Return JSON with key "summary_insights" as a list of strings."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                res_content = json.loads(response.choices[0].message.content)
                if "summary_insights" in res_content and isinstance(res_content["summary_insights"], list):
                    base_res["summary_insights"] = res_content["summary_insights"]
                    base_res["data_source"] = f"{data_source} + GPT-4o Synthesis"
            except Exception as e:
                print("OpenAI LLM Synthesis fallback to local engine:", e)

        return base_res

    def _handle_sector_query(self, original_query: str, query_lower: str, deals_df: pd.DataFrame, wo_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        target_sector = None
        for s in ['mining', 'powerline', 'renewables', 'railways', 'construction', 'dsp', 'tender']:
            if s in query_lower:
                target_sector = s.title()
                break

        if target_sector:
            sub_deals = deals_df[deals_df['sector'].str.lower() == target_sector.lower()]
            sub_wo = wo_df[wo_df['sector'].str.lower() == target_sector.lower()]
            sector_name = target_sector
        else:
            sub_deals = deals_df
            sub_wo = wo_df
            sector_name = "All Sectors"

        total_deals = len(sub_deals)
        total_deal_val = float(sub_deals['deal_value'].sum())
        weighted_val = float(sub_deals['weighted_deal_value'].sum())
        won_deals = len(sub_deals[sub_deals['deal_status'].str.lower() == 'won'])

        total_wo = len(sub_wo)
        total_po_val = float(sub_wo['amount_excl_gst'].sum())
        total_billed = float(sub_wo['billed_excl_gst'].sum())
        total_collected = float(sub_wo['collected_incl_gst'].sum())

        billing_coverage = (total_billed / total_po_val * 100) if total_po_val > 0 else 0.0

        chart_data = {
            "type": "bar",
            "title": f"Financial Breakdown for {sector_name}",
            "labels": ["Total Deal Value", "Weighted Pipeline", "Work Order PO Value", "Billed Value", "Collected Value"],
            "values": [round(total_deal_val, 2), round(weighted_val, 2), round(total_po_val, 2), round(total_billed, 2), round(total_collected, 2)]
        }

        insights = [
            f"**Sector**: {sector_name}",
            f"**Pipeline Health**: {total_deals} active deals totaling **{format_inr(total_deal_val)}** (Probability-weighted: **{format_inr(weighted_val)}**).",
            f"**Deals Won**: {won_deals} deals won.",
            f"**Work Orders Execution**: {total_wo} active work orders worth **{format_inr(total_po_val)}**.",
            f"**Billing Coverage**: **{format_inr(total_billed)}** billed out of total PO value ({billing_coverage:.1f}% billing progress).",
            f"**Collections**: **{format_inr(total_collected)}** total collected (incl. GST)."
        ]

        return {
            "query": original_query,
            "headline": f"Sector Analysis: {sector_name}",
            "summary_insights": insights,
            "key_metrics": {
                "total_deals": total_deals,
                "pipeline_value_inr": total_deal_val,
                "weighted_pipeline_inr": weighted_val,
                "work_orders_count": total_wo,
                "po_value_inr": total_po_val,
                "billed_value_inr": total_billed,
                "collected_value_inr": total_collected
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                f"Which {sector_name} deals have closure probability > 80%?",
                f"Show unbilled work orders for {sector_name}",
                "Compare pipeline health across all sectors"
            ]
        }

    def _handle_pipeline_query(self, original_query: str, deals_df: pd.DataFrame, wo_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        stage_group = deals_df.groupby('deal_stage').agg(
            deal_count=('deal_name', 'count'),
            total_val=('deal_value', 'sum'),
            weighted_val=('weighted_deal_value', 'sum')
        ).reset_index().sort_values('total_val', ascending=False)

        total_deals = len(deals_df)
        total_pipeline = float(deals_df['deal_value'].sum())
        total_weighted = float(deals_df['weighted_deal_value'].sum())
        high_prob_deals = len(deals_df[deals_df['closure_probability'] >= 0.8])

        chart_data = {
            "type": "pie",
            "title": "Pipeline Distribution by Stage",
            "labels": stage_group['deal_stage'].tolist()[:6],
            "values": [round(x, 2) for x in stage_group['total_val'].tolist()[:6]]
        }

        insights = [
            f"**Total Funnel Volume**: {total_deals} active deals in the pipeline.",
            f"**Raw Pipeline Value**: **{format_inr(total_pipeline)}**.",
            f"**Probability-Weighted Pipeline**: **{format_inr(total_weighted)}** (accounts for closure confidence).",
            f"**High Confidence Deals**: {high_prob_deals} deals have ≥80% closure probability.",
            f"**Top Stage by Value**: {stage_group.iloc[0]['deal_stage']} with **{format_inr(stage_group.iloc[0]['total_val'])}**."
        ]

        return {
            "query": original_query,
            "headline": "Pipeline & Deal Funnel Analysis",
            "summary_insights": insights,
            "key_metrics": {
                "total_deals": total_deals,
                "total_pipeline_val": total_pipeline,
                "weighted_pipeline_val": total_weighted,
                "high_probability_deals_count": high_prob_deals
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                "Which owners have the highest pipeline value?",
                "What is the average closure time for high probability deals?",
                "Show deals scheduled to close this quarter"
            ]
        }

    def _handle_revenue_query(self, original_query: str, deals_df: pd.DataFrame, wo_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        total_po = float(wo_df['amount_excl_gst'].sum())
        total_billed = float(wo_df['billed_excl_gst'].sum())
        unbilled = float(wo_df['amount_to_be_billed_excl'].sum())
        receivable = float(wo_df['amount_receivable'].sum())
        collected = float(wo_df['collected_incl_gst'].sum())

        chart_data = {
            "type": "bar",
            "title": "Revenue & Billing Flow",
            "labels": ["Total Contract Value", "Billed Value", "Unbilled Value", "Collected Value", "Receivables"],
            "values": [round(total_po, 2), round(total_billed, 2), round(unbilled, 2), round(collected, 2), round(receivable, 2)]
        }

        insights = [
            f"**Total Contract Value (Work Orders)**: **{format_inr(total_po)}** (excl. GST).",
            f"**Billed Value**: **{format_inr(total_billed)}** ({total_billed/total_po*100:.1f}% billed).",
            f"**Unbilled Backlog**: **{format_inr(unbilled)}** pending billing.",
            f"**Outstanding Receivables**: **{format_inr(receivable)}** awaiting customer remittance.",
            f"**Total Collected**: **{format_inr(collected)}** cash realized (incl. GST)."
        ]

        return {
            "query": original_query,
            "headline": "Revenue, Billing & Cashflow Metrics",
            "summary_insights": insights,
            "key_metrics": {
                "total_contract_val": total_po,
                "billed_val": total_billed,
                "unbilled_backlog": unbilled,
                "receivable_val": receivable,
                "collected_val": collected
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                "Which clients have the largest unbilled amounts?",
                "Show billing status breakdown by sector",
                "What is the collection efficiency ratio?"
            ]
        }

    def _handle_operations_query(self, original_query: str, wo_df: pd.DataFrame, deals_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        exec_status = wo_df.groupby('execution_status')['deal_name'].count().to_dict()
        stuck_wo = len(wo_df[wo_df['billing_status'].str.lower() == 'stuck'])
        update_req = len(wo_df[wo_df['billing_status'].str.lower() == 'update required'])

        software_attached = len(wo_df[wo_df['software_deliverable'] != 'NONE'])
        attach_rate = (software_attached / len(wo_df) * 100) if len(wo_df) > 0 else 0.0

        chart_data = {
            "type": "pie",
            "title": "Work Order Execution Status",
            "labels": list(exec_status.keys()),
            "values": list(exec_status.values())
        }

        insights = [
            f"**Total Work Orders**: {len(wo_df)} projects tracked.",
            f"**Execution Progress**: {exec_status.get('Completed', 0)} Completed, {exec_status.get('Ongoing', 0)} Ongoing, {exec_status.get('Not Started', 0)} Not Started.",
            f"**Operational Bottlenecks**: {stuck_wo} Work Orders flagged as **STUCK**; {update_req} require billing updates.",
            f"**Software Platform Attachment Rate**: **{attach_rate:.1f}%** ({software_attached} work orders deliver Skylark SPECTRA / DMO platform)."
        ]

        return {
            "query": original_query,
            "headline": "Operations & Work Order Delivery Health",
            "summary_insights": insights,
            "key_metrics": {
                "total_work_orders": len(wo_df),
                "completed_count": exec_status.get('Completed', 0),
                "ongoing_count": exec_status.get('Ongoing', 0),
                "stuck_count": stuck_wo,
                "software_attach_rate_pct": round(attach_rate, 1)
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                "Which work orders are currently marked as STUCK?",
                "What is the software platform distribution (SPECTRA vs DMO)?",
                "Show work orders missing completion date"
            ]
        }

    def _handle_owner_query(self, original_query: str, deals_df: pd.DataFrame, wo_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        owner_deals = deals_df.groupby('owner_code').agg(
            deal_count=('deal_name', 'count'),
            total_val=('deal_value', 'sum'),
            weighted_val=('weighted_deal_value', 'sum')
        ).reset_index().sort_values('total_val', ascending=False)

        top_owner = owner_deals.iloc[0]

        chart_data = {
            "type": "bar",
            "title": "Top Sales Owners by Deal Value",
            "labels": owner_deals['owner_code'].tolist()[:5],
            "values": [round(x, 2) for x in owner_deals['total_val'].tolist()[:5]]
        }

        insights = [
            f"**Active Sales Owners**: {len(owner_deals)} BD/KAM personnel tracked.",
            f"**Top Performing Owner**: **{top_owner['owner_code']}** with **{top_owner['deal_count']}** deals worth **{format_inr(top_owner['total_val'])}**.",
            f"**Weighted Top Pipeline**: **{top_owner['owner_code']}** weighted value: **{format_inr(top_owner['weighted_val'])}**."
        ]

        return {
            "query": original_query,
            "headline": "BD & Sales Owner Performance",
            "summary_insights": insights,
            "key_metrics": {
                "active_owners_count": len(owner_deals),
                "top_owner_code": top_owner['owner_code'],
                "top_owner_pipeline_val": top_owner['total_val']
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                "Show full sales rep leaderboard",
                "Which owner has the highest win conversion rate?",
                "Show work order billing by BD owner"
            ]
        }

    def _handle_overview_query(self, original_query: str, deals_df: pd.DataFrame, wo_df: pd.DataFrame, caveats: List[str], data_source: str) -> Dict[str, Any]:
        total_deals = len(deals_df)
        pipeline_val = float(deals_df['deal_value'].sum())
        total_wo = len(wo_df)
        contract_val = float(wo_df['amount_excl_gst'].sum())
        billed_val = float(wo_df['billed_excl_gst'].sum())

        chart_data = {
            "type": "bar",
            "title": "Executive Summary Key Metrics",
            "labels": ["Active Deals", "Pipeline Value", "Work Orders", "Contract Val", "Billed Val"],
            "values": [total_deals, round(pipeline_val/1e5, 1), total_wo, round(contract_val/1e5, 1), round(billed_val/1e5, 1)]
        }

        insights = [
            f"**Deals Pipeline**: **{total_deals}** active deals worth **{format_inr(pipeline_val)}**.",
            f"**Work Orders Execution**: **{total_wo}** work orders totaling **{format_inr(contract_val)}** in contract value.",
            f"**Revenue Progress**: **{format_inr(billed_val)}** billed to date ({billed_val/contract_val*100:.1f}% billing conversion).",
            f"**Data Resilience Note**: {len(caveats)} automated cleaning actions applied to ensure accurate cross-board calculations."
        ]

        return {
            "query": original_query,
            "headline": "Business Intelligence Overview",
            "summary_insights": insights,
            "key_metrics": {
                "total_deals": total_deals,
                "pipeline_value_inr": pipeline_val,
                "total_work_orders": total_wo,
                "contract_value_inr": contract_val,
                "billed_value_inr": billed_val
            },
            "chart": chart_data,
            "caveats": caveats,
            "data_source": data_source,
            "suggested_followups": [
                "How is our pipeline looking for Mining sector?",
                "What is our revenue and unbilled backlog?",
                "Which work orders are stuck or pending updates?"
            ]
        }
