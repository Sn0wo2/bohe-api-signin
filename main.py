import asyncio
import random
from dataclasses import dataclass

from client import BoheClient
from store.token import load_accounts
from utils.logger import setup_logger

logger = setup_logger()


@dataclass(frozen=True)
class RunResult:
    success: bool
    summary: str
    details: str = ""

    @property
    def exit_code(self) -> int:
        return 0 if self.success else 1


async def main() -> RunResult:
    accounts = load_accounts()
    logger.info(f"Loaded {len(accounts)} account(s)")

    results: list[tuple[int, bool]] = []
    for index, account in enumerate(accounts):
        logger.info(
            f"[account{index + 1}] Processing account {index + 1}/{len(accounts)}"
        )
        try:
            client = BoheClient(account, index)
            await client.authenticate()
            ok = await client.signin()
        except Exception:
            logger.exception(f"[account{index + 1}] Account processing failed")
            ok = False
        results.append((index, ok))

        if index < len(accounts) - 1:
            delay = random.uniform(5, 20)
            logger.info(f"Sleeping {delay:.0f}s before next account...")
            await asyncio.sleep(delay)

    succeeded = [idx for idx, ok in results if ok]
    failed = [idx for idx, ok in results if not ok]
    logger.info(f"Done: {len(succeeded)} succeeded, {len(failed)} failed")
    if failed:
        logger.warning(
            f"Failed accounts: {', '.join(f'account{idx + 1}' for idx in failed)}"
        )

    summary = f"✅{len(succeeded)} ❌{len(failed)}"
    details = f"Done: {len(succeeded)} succeeded, {len(failed)} failed"
    if failed:
        details += f"\nFailed accounts: {', '.join(f'account{idx + 1}' for idx in failed)}"

    # success if at least one account succeeded (preserves prior exit-code semantics)
    return RunResult(len(succeeded) > 0, summary, details)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()).exit_code)
