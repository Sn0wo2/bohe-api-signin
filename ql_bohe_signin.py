#!/usr/bin/env python3
"""
cron: 0 0 * * *
new Env("bohe-api-signin")
"""
import asyncio
import builtins
import os
from pathlib import Path
from typing import NoReturn

SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

from main import RunResult, main


def _notify(result: RunResult) -> None:
    ql_api = getattr(builtins, "QLAPI", None)
    if ql_api is None:
        return

    status = "[OK]" if result.success else "[FAIL]"
    content = result.details or result.summary
    try:
        ql_api.systemNotify({
            "title": f"{status} bohe-api-signin {result.summary}",
            "content": content,
        })
    except Exception as error:
        print(f"QLAPI notification failed: {error}")


def run() -> NoReturn:
    try:
        result = asyncio.run(main())
    except Exception as error:
        result = RunResult(False, "Unexpected error", str(error))
        print(f"bohe-api-signin failed: {error}")
    _notify(result)
    raise SystemExit(result.exit_code)


if __name__ == "__main__":
    run()
