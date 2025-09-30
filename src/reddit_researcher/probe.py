from __future__ import annotations

import json
import sys
from pathlib import Path

from .config import AppConfig, generate_run_id, load_config


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]

    try:
        cfg: AppConfig = load_config("config.yaml")
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    run_id = generate_run_id()

    # For Phase 1, just print a summary and write a trivial report scaffold
    summary = {
        "run_id": run_id,
        "config": {
            "subreddit": cfg.probe.subreddit,
            "listing": cfg.probe.listing,
            "post_limit": cfg.probe.post_limit,
            "comment_sample": cfg.probe.comment_sample,
            "comment_replace_more_limit": cfg.probe.comment_replace_more_limit,
            "qpm_cap": cfg.probe.qpm_cap,
            "raw_json": cfg.probe.raw_json,
        },
    }

    print(json.dumps(summary, indent=2))

    report_path = Path(cfg.probe.reports_dir) / f"run_{run_id}.md"
    lines = [
        f"# Reddit Probe — r/{cfg.probe.subreddit} ({cfg.probe.listing}) — {run_id}",
        "",
        "This is a Phase-1 stub report.",
        "Data collection will be implemented in later phases.",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


