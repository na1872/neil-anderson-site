from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sharpe_pint.config import load_config
from sharpe_pint.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate The Sharpe Pint daily briefing.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Briefing date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Folder where JSON output will be saved.",
    )
    args = parser.parse_args()

    config = load_config(PROJECT_ROOT)
    run_pipeline(config=config, today=args.date, output_dir=PROJECT_ROOT / args.output_dir)


if __name__ == "__main__":
    main()
