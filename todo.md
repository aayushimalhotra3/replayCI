# ReplayCI V1 TODO (Aayushi + Vanshika)

Goal for V1: PR-native regression testing for tool-using agents with deterministic replay, behavior diffs, and budget/safety gates.

Definition of done:
- [x] `replayci run` records a run with fixtures
- [x] `replayci run --mode replay --fixtures-dir ...` replays deterministically without calling real tools
- [ ] `replayci diff` shows tool sequence + budget + safety diffs, including first divergence
- [ ] `replayci report` generates a clean static HTML report
- [ ] GitHub Action runs on PR, compares to goldens, comments pass/fail + top deltas, uploads report

---

## 0) Agreements (shared, unblock everything)
- [x] Finalize Scenario YAML schema (fields + defaults)
- [x] Finalize JSONL event schema (types + required fields)
- [x] Finalize fixture keying (tool name + args hash) and fixture file format
- [ ] Document in `docs/spec-v1.md`

Owner: Aayushi + Vanshika  
Done when: both can implement independently without guessing.

---

## 1) Environment sanity (shared)
- [x] Pick one Python environment setup and document it in README (venv or conda)
- [x] Ensure `python`, `pip`, and `replayci` all come from same environment
- [x] Remove leftover `agentci.egg-info/` and stale references

Owner: Aayushi  
Done when: `which python`, `which pip`, `replayci --help` are consistent.

---

## 2) Core runner (Aayushi)
- [x] Scenario loader validates allowed_tools exist in registry
- [x] Research agent stub uses ToolExecutor (no direct registry calls)
- [x] Recorder writes `runs/<run_id>/events.jsonl` and creates fixtures dir

Done when: `replayci run scenarios/s01_basic_research.yaml` creates run artifacts.

---

## 3) Deterministic fixtures + replay (Aayushi)
- [x] Add CLI option `--fixtures-dir PATH` (replay reads from here)
- [x] Record mode saves fixtures to `runs/<run_id>/fixtures/<tool>/<args_hash>.json`
- [x] Replay mode loads fixtures only, never runs real tool callables
- [x] Missing fixture fails with clear error + nonzero exit code
- [x] Update README with record/replay commands

Done when: record once, then replay using `--fixtures-dir runs/<recorded_run_id>/fixtures` works with wifi off.

---

## 4) Event quality (Aayushi)
- [x] Ensure every JSONL event includes `ts_ms` (epoch ms)
- [x] Standardize event types: run_start, tool_call, tool_result, agent_note, gate_result, run_end
- [x] Add `step` as an int that increases predictably

Done when: events.jsonl is stable across runs and easy to parse.

---

## 5) Gates V1 (Aayushi)
Implement only these four:
- [x] max_tool_calls
- [ ] max_cost_usd (rough estimate ok for v1)
- [ ] max_latency_ms
- [ ] no_pii_in_logs (regex checks on payloads)

- [x] Emit gate_result events (passed true/false, observed, limit)
- [x] Fail run (exit nonzero) on any failing gate

Done when: you can intentionally trigger a failure and see which gate failed.

---

## 6) Diff engine V1 (Aayushi)
- [ ] `replayci diff <runA> <runB>` prints:
  - [ ] tool sequence diff (added/removed/reordered)
  - [ ] budgets diff (tool_calls/cost/latency)
  - [ ] safety diff (PII violations introduced/removed)
  - [ ] first divergence step index and summary
- [ ] Output is human readable and short

Done when: a small prompt/tool change produces an obvious diff.

---

## 7) Report generator (Vanshika)
- [ ] `replayci report <runA> <runB> --out reports/<id>/` generates static HTML
- Report must show:
  - [ ] summary deltas (tool calls, cost, latency, safety)
  - [ ] timeline of steps for A and B
  - [ ] first divergence highlighted
  - [ ] expandable raw payload per step
- [ ] Keep it simple: no React required unless you want it

Done when: opening index.html makes the regression obvious in 10 seconds.
