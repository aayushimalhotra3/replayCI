# ReplayCI

V1 foundation for ReplayCI developer tool.

## Quickstart

1.  **Install**:
    ```bash
    pip install -e .
    ```

2.  **Run a scenario (Record mode)**:
    Default mode is `record`. This executes tools and saves fixtures to `runs/<run_id>/fixtures`.
    ```bash
    replayci run scenarios/s01_basic_research.yaml --mode record
    ```
    Output: `runs/20260120_...`

3.  **Replay a scenario**:
    Uses saved fixtures from a specific directory. No real tool execution.
    **Requires** `--fixtures-dir` pointing to the fixtures you want to replay.
    ```bash
    replayci run scenarios/s01_basic_research.yaml \
      --mode replay \
      --fixtures-dir runs/20260120_.../fixtures
    ```
    Fails explicitly if a required fixture is missing in that directory.

## Artifacts

Runs are stored in the `runs/` directory (locally).
Each run creates a folder `runs/<run_id>/` containing:
-   `events.jsonl`: Trace of events (run_start, tool_call, tool_result, gate_result, etc.)
-   `fixtures/`: Directory for tool fixtures.

### Fixtures Layout
`runs/<run_id>/fixtures/<tool_name>/<args_hash>.json`

Example:
`runs/20231025_.../fixtures/web_fetch/a1b2c3d4....json`

Content:
```json
{
  "tool": "web_fetch",
  "args": {"url": "http://..."},
  "result": "..."
}
```

## Gates

Scenarios can define assertions, like `max_tool_calls`.
If a run exceeds the limit, the CLI exits with a non-zero status code and emits a failed `gate_result` event.

## Structure

-   `replayci/`: Source code
-   `scenarios/`: YAML scenario definitions
-   `runs/`: Output artifacts (ignored by git)

## Sanity Test Plan

To verify replay functionality:

1.  **Record a run**:
    ```bash
    replayci run scenarios/s01_basic_research.yaml --mode record
    ```
    Note the `run_id` from the output (e.g., `20260120_1234`).

2.  **Replay using that run's fixtures**:
    ```bash
    replayci run scenarios/s01_basic_research.yaml --mode replay --fixtures-dir runs/<run_id>/fixtures
    ```

3.  **Verify**:
    -   The replay run completes successfully.
    -   No new fixture files are created in the *new* run's `fixtures` directory (it should be empty).
    -   The output `latency_ms` should be very low (since tools are mocked).
