import json
import logging
import os
from typing import List, Dict
from datetime import datetime

import config


logger = logging.getLogger("notifier")


def send_email_alert(applications: List[Dict]) -> bool:
    if not applications:
        logger.info("No applications to send")
        return True

    if not config.EMAIL["enabled"]:
        logger.warning("Email notifications disabled in config")
        return _save_to_json(applications)

    if not all([config.EMAIL["smtp_user"], config.EMAIL["smtp_password"], 
                config.EMAIL["from_email"], config.EMAIL["to_email"]]):
        logger.warning("Email not configured - saving to JSON instead")
        return _save_to_json(applications)

    return _save_to_json(applications)


def _save_to_json(applications: List[Dict]) -> bool:
    alerts_file = os.path.join(config.DATA_DIR, "alerts.json")
    os.makedirs(config.DATA_DIR, exist_ok=True)

    try:
        existing = []
        if os.path.exists(alerts_file):
            with open(alerts_file, "r") as f:
                existing = json.load(f)

        alert_entry = {
            "date": datetime.now().isoformat(),
            "count": len(applications),
            "applications": applications
        }
        existing.append(alert_entry)

        existing = existing[-100:]

        with open(alerts_file, "w") as f:
            json.dump(existing, f, indent=2)

        logger.info(f"Saved {len(applications)} applications to {alerts_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save alerts: {e}")
        return False


def _build_html(applications: List[Dict]) -> str:
    rows = []
    for app in applications:
        rows.append(f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">
                <strong>{app.get('reference', 'N/A')}</strong>
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {app.get('address', 'N/A')}
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {app.get('description', 'N/A')}
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {app.get('received_date', 'N/A')}
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {app.get('matched_keyword', 'N/A')}
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                <a href="{app.get('url', '#')}">View</a>
            </td>
        </tr>
        """)

    html = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th {{ background-color: #4a90d9; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Planning Application Alert</h2>
        <p>The following planning applications match your keywords:</p>
        <table>
            <thead>
                <tr>
                    <th>Reference</th>
                    <th>Address</th>
                    <th>Description</th>
                    <th>Date</th>
                    <th>Keyword</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <p style="margin-top: 20px; color: #666; font-size: 12px;">
            Sent by UK Planning Monitor on {datetime.now().isoformat()}
        </p>
    </body>
    </html>
    """
    return html