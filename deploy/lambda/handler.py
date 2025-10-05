from __future__ import annotations

import json
import os
from typing import Any, Dict

from reddit_researcher.core.probe import main as probe_main


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Optionally override LOG_LEVEL via event
    level = event.get("LOG_LEVEL") if isinstance(event, dict) else None
    if level:
        os.environ["LOG_LEVEL"] = str(level)

    # Run the probe; it prints a JSON summary and returns 0
    exit_code = probe_main([])

    # Respond with a basic payload; CloudWatch logs contain detailed INFO lines
    body = {"status": "ok" if exit_code == 0 else "error", "exit_code": exit_code}
    return {"statusCode": 200 if exit_code == 0 else 500, "body": json.dumps(body)}


