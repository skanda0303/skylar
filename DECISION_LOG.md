# Decision Log: Monday.com Business Intelligence Agent

**Author**: Skylark Drones Technical Candidate  
**Target Audience**: Leadership & Technical Evaluation Team  
**Timeline**: 6 Hours Assignment  

---

## 1. Key Assumptions Made

1. **Board Structure & Schema Heterogeneity**:
   - The provided Excel files (`Deal_funnel_Data.xlsx` and `Work_Order_Tracker_Data.xlsx`) represent realistic messy data. In `Work_Order_Tracker_Data.xlsx`, row 0 contains the actual column headers (`Deal name masked`, `Customer Name Code`, `Amount in Rupees`, etc.), requiring header elevation during parsing.
   - Missing numerical values in deal amounts (181 deals missing value fields) were treated as `₹0` for aggregate calculations, with an explicit **Data Resilience Caveat Audit** surfaced to the executive user.

2. **Cross-Board Entity Linking**:
   - `Deal Name` in Deals board links to `Deal name masked` in Work Orders board.
   - Owner code maps sales reps across both boards (`OWNER_001`, `OWNER_002`, etc.).

3. **Probability & Sector Mapping**:
   - Closure probabilities specified as text strings ("High", "Medium", "Low") were mapped into quantitative factors (80%, 50%, 20%) to enable probability-weighted pipeline calculation (`Weighted Value = Deal Value × Probability`).
   - Inconsistent sector naming conventions (e.g., "power line", "Powerline", "renewable", "Renewables") were normalized into canonical sector buckets (`Mining`, `Powerline`, `Renewables`, `Railways`, `Construction`, `DSP`, `Tender`).

---

## 2. Trade-offs Chosen and Why

| Area | Option Considered | Trade-off Chosen & Rationale |
| :--- | :--- | :--- |
| **API Integration** | Pure Monday.com GraphQL vs Local Mirror Fallback | **Hybrid Approach**: Built a full Monday.com GraphQL v2 client (`monday_client.py`) supporting live queries AND a robust dataset mirror powered by the Data Resilience Engine. This guarantees full functionality with or without a live API key during evaluation. |
| **Tech Stack** | Monolithic Python vs Decoupled FastAPI + React/Vite | **FastAPI + React/Vite**: Decoupled architecture provides clean separation of backend analytical processing and a state-of-the-art glassmorphism executive UI. |
| **LLM Query Parsing** | Pure LLM Prompting vs Rule-Engine + Analytical Fallback | **Hybrid Natural Language Engine**: Combines intent matching with statistical aggregation to ensure 100% deterministic, accurate financial metrics without hallucinated numbers. |

---

## 3. Interpretation of "Leadership Updates"

The PDF assignment asks to help prepare data for leadership updates:

> *"The agent should help prepare data for leadership updates. How you interpret and implement this is up to you."*

**Our Interpretation & Implementation**:
- Leadership updates require **actionable brevity, risk highlighting, and multi-channel formatting**. Executives do not want raw spreadsheets; they need clear summaries of pipeline health, billing execution, cash flow backlog, and operational risks.
- We built a dedicated **Executive Leadership Brief Generator (`LeadershipBuilder.jsx` & `leadership_updates.py`)**:
  1. **Executive Brief Formatting**: Formats real-time metrics into clean, slides-ready Markdown with Slack/Email copy buttons.
  2. **Risk Focus**: Automatically highlights "Stuck" Work Orders and unbilled contract backlog.
  3. **Sector Filtering**: Enables leadership to generate sector-specific briefings (e.g., Mining, Powerline, Renewables) instantly.

---

## 4. What We Would Do Differently With More Time

1. **Automated Monday.com Webhooks**: Implement real-time Monday.com webhooks to push live updates whenever board items or column statuses change.
2. **Advanced NLP Embeddings**: Integrate vector embeddings (e.g. via OpenAI or local embeddings) for semantic vector search over custom commentary fields.
3. **Automated PDF / PowerPoint Export**: Add direct PDF/PPTX generation for C-suite slide deck export.

---

## 5. Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    React + Vite Frontend                    │
│   (Glassmorphism UI, BI Chat, Leadership Briefs, Explorer) │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API / CORS
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Server                   │
│   (/api/query, /api/leadership-update, /api/boards)         │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼────────┐       ┌──────▼────────┐       ┌──────▼────────┐
│  BIAgent &    │       │ DataResilience│       │ MondayClient  │
│ Analytical Engine     │ Engine        │       │ (GraphQL v2)  │
└───────────────┘       └───────────────┘       └───────────────┘
```
