"""The offline evaluation suite doubles as a regression test."""

from evals.run_evals import run_all


async def test_offline_eval_suite_passes():
    results = await run_all(live=False)
    assert len(results) >= 10
    failed = {r["case"]["id"]: [n for n, ok in r["checks"] if not ok] for r in results if not r["passed"]}
    assert not failed, failed
