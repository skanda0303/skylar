import os
import json
import requests
from typing import Dict, Any, List, Optional

class ComposioIntegration:
    """
    Composio Tool Integrator for Monday.com BI Agent.
    Enables automatic Slack alerts, Email executive brief dispatches,
    and automated Monday.com status updates via Composio platform.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def dispatch_slack_alert(self, channel: str, message: str) -> Dict[str, Any]:
        """Dispatches an executive alert to a Slack channel using Composio Slack tool."""
        if not self.api_key:
            return {
                "status": "simulation",
                "message": f"Simulated Slack alert to #{channel}: {message[:100]}...",
                "note": "Set COMPOSIO_API_KEY environment variable to enable live Composio integration."
            }
        
        # Composio API Tool Execution Endpoint
        url = "https://backend.composio.dev/api/v1/actions/SLACK_CHAT_POST_MESSAGE/execute"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel,
            "text": message
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                return {"status": "success", "response": res.json()}
            return {"status": "error", "message": res.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def dispatch_email_brief(self, recipient_email: str, subject: str, body_markdown: str) -> Dict[str, Any]:
        """Dispatches executive brief email using Composio Gmail/Email tool."""
        if not self.api_key:
            return {
                "status": "simulation",
                "message": f"Simulated Email brief to {recipient_email}: Subject: {subject}",
                "note": "Set COMPOSIO_API_KEY environment variable to enable live Composio integration."
            }

        url = "https://backend.composio.dev/api/v1/actions/GMAIL_SEND_EMAIL/execute"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "recipient_email": recipient_email,
            "subject": subject,
            "body": body_markdown
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                return {"status": "success", "response": res.json()}
            return {"status": "error", "message": res.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
