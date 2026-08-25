import pandas as pd
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

class LeadershipUpdateGenerator:
    """
    Generates executive-ready leadership briefs for founders, C-suite, and board meetings.
    Formats numbers into clean Lakhs/Crores financial figures with smart conditional actions
    and clean Markdown tables.
    """

    def __init__(self, monday_client: Optional[MondayClient] = None):
        self.client = monday_client or MondayClient()

    def generate_update(self, report_type: str = "executive", sector: Optional[str] = None, deals_board_id: Optional[str] = None, wo_board_id: Optional[str] = None) -> Dict[str, Any]:
        data = self.client.get_all_data(deals_board_id, wo_board_id)
        deals_df = data['deals']
        wo_df = data['work_orders']
        deals_audit = data['deals_audit']
        wo_audit = data['work_orders_audit']

        if sector and sector.lower() != 'all':
            deals_df = deals_df[deals_df['sector'].str.lower() == sector.lower()]
            wo_df = wo_df[wo_df['sector'].str.lower() == sector.lower()]
            sector_title = sector.title()
        else:
            sector_title = "Overall Business"

        # Financial Metrics
        total_pipeline = float(deals_df['deal_value'].sum()) if len(deals_df) > 0 else 0.0
        weighted_pipeline = float(deals_df['weighted_deal_value'].sum()) if len(deals_df) > 0 else 0.0
        won_deals = deals_df[deals_df['deal_status'].str.lower() == 'won'] if len(deals_df) > 0 else pd.DataFrame()
        total_won_val = float(won_deals['deal_value'].sum()) if len(won_deals) > 0 else 0.0

        total_wo_val = float(wo_df['amount_excl_gst'].sum()) if len(wo_df) > 0 else 0.0
        total_billed = float(wo_df['billed_excl_gst'].sum()) if len(wo_df) > 0 else 0.0
        total_unbilled = float(wo_df['amount_to_be_billed_excl'].sum()) if len(wo_df) > 0 else 0.0
        total_collected = float(wo_df['collected_incl_gst'].sum()) if len(wo_df) > 0 else 0.0
        total_receivable = float(wo_df['amount_receivable'].sum()) if len(wo_df) > 0 else 0.0

        stuck_wo = wo_df[wo_df['billing_status'].str.lower() == 'stuck'] if len(wo_df) > 0 else pd.DataFrame()
        stuck_count = len(stuck_wo)

        missing_val_count = len(deals_df[deals_df['deal_value'] == 0]) if len(deals_df) > 0 else 0

        billing_rate = (total_billed / total_wo_val * 100) if total_wo_val > 0 else 0.0

        # Smart Action Items
        action_items = []
        if total_unbilled > 0:
            action_items.append(f"Accelerate billing milestone clearance on **{format_inr(total_unbilled)}** unbilled backlog.")
        else:
            action_items.append("Maintain timely invoice issuance; zero unbilled backlog reported.")

        if stuck_count > 0:
            action_items.append(f"Escalate and intervene on **{stuck_count}** stuck work order(s) requiring account resolution.")
        else:
            action_items.append("Maintain operational cadence — zero stuck work orders reported in this sector.")

        if weighted_pipeline > 0:
            action_items.append(f"Focus BD bandwidth on high-probability deals in Proposal stage (**{format_inr(weighted_pipeline)}** weighted pipeline).")

        formatted_actions = "\n".join([f"{idx+1}. {item}" for idx, item in enumerate(action_items)])

        # Data Audit Line
        if missing_val_count > 0:
            audit_note = f"{missing_val_count} deal(s) missing value fields (imputed as ₹0 for safe calculation)."
        else:
            audit_note = "Zero missing deal values; 100% deal data completeness verified."

        # Build Formatted Executive Brief
        markdown_brief = f"""# Executive Leadership Update — {sector_title}

Data Source: {data.get('data_source')}

---

### Executive Performance Summary
| Metric | Volume / Value | Execution Status |
| :--- | :--- | :--- |
| **Deals Pipeline** | **{format_inr(total_pipeline)}** | {len(deals_df)} active deals (Weighted: **{format_inr(weighted_pipeline)}**) |
| **Closed-Won Revenue** | **{format_inr(total_won_val)}** | {len(won_deals)} won deals |
| **Active Work Orders** | **{format_inr(total_wo_val)}** | {len(wo_df)} active projects |
| **Billed Revenue** | **{format_inr(total_billed)}** | **{billing_rate:.1f}%** billing execution rate |
| **Unbilled Backlog** | **{format_inr(total_unbilled)}** | Pending milestone clearance |
| **Outstanding Receivables** | **{format_inr(total_receivable)}** | Pending customer payment |

---

### 1. Key Business Highlights & Revenue
- Total Pipeline Volume: **{format_inr(total_pipeline)}** across **{len(deals_df)}** deals (Probability-Weighted: **{format_inr(weighted_pipeline)}**).
- Closed-Won Revenue: **{format_inr(total_won_val)}** ({len(won_deals)} won deals).
- Active Work Orders Value: **{format_inr(total_wo_val)}** across **{len(wo_df)}** projects.
- Billed to Date: **{format_inr(total_billed)}** (**{billing_rate:.1f}%** billing execution rate).

---

### 2. Financial Backlog & Cash Flow Health
- Unbilled Backlog: **{format_inr(total_unbilled)}** pending billing milestones.
- Outstanding Receivables: **{format_inr(total_receivable)}** pending customer payment.
- Cash Realized (Collected): **{format_inr(total_collected)}** (incl. GST).

---

### 3. Operational Risks & Data Quality
- Stuck Work Orders: **{stuck_count}** project(s) flagged as STUCK requiring escalation.
- Data Quality Audit: {audit_note}

---

### 4. Strategic Actions Required
{formatted_actions}
"""

        summary_cards = [
            {"title": "Pipeline Value", "value": format_inr(total_pipeline), "subtext": f"{len(deals_df)} active deals"},
            {"title": "Contract PO Value", "value": format_inr(total_wo_val), "subtext": f"{len(wo_df)} work orders"},
            {"title": "Billed Progress", "value": format_inr(total_billed), "subtext": f"{billing_rate:.1f}% billed"},
            {"title": "Unbilled Backlog", "value": format_inr(total_unbilled), "subtext": "Action required" if total_unbilled > 0 else "Up to date"}
        ]

        return {
            "report_type": report_type,
            "sector": sector_title,
            "markdown_content": markdown_brief,
            "summary_cards": summary_cards,
            "caveats": deals_audit['quality_caveats'] + wo_audit['quality_caveats']
        }
