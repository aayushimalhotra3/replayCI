import datetime
import random
import string
import time
from pathlib import Path
from typing import Optional, Literal

import typer

from replayci.agent.research_agent import ResearchAgentStub
from replayci.runlog.recorder import Recorder
from replayci.runlog.events import Event
from replayci.scenario.loader import load_scenario

app = typer.Typer()

@app.callback()
def callback():
    """
    ReplayCI CLI tool.
    """

def generate_run_id() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{timestamp}_{random_str}"

@app.command()
def run(
    scenario_path: Path = typer.Argument(..., help="Path to the scenario YAML file"),
    mode: str = typer.Option("record", help="Execution mode: record or replay"),
    out: Path = typer.Option(Path("runs"), help="Directory to store run artifacts"),
    fixtures_dir: Optional[Path] = typer.Option(None, help="Directory containing fixtures (required for replay)"),
    use_latest_fixtures: bool = typer.Option(False, help="Automatically use latest run fixtures in replay mode")
):
    """
    Run a scenario with the agent.
    """
    if mode not in ["record", "replay"]:
        typer.echo(f"Invalid mode: {mode}. Must be 'record' or 'replay'.", err=True)
        raise typer.Exit(code=1)

    # Handle --use-latest-fixtures for replay mode
    if mode == "replay" and use_latest_fixtures and not fixtures_dir:
        # Find latest run in runs dir
        if not out.exists():
            typer.echo(f"Error: Runs directory '{out}' does not exist.", err=True)
            raise typer.Exit(code=1)
        
        runs = sorted([d for d in out.iterdir() if d.is_dir() and (d / "fixtures").exists()], key=lambda p: p.name, reverse=True)
        if not runs:
             typer.echo(f"Error: No valid runs with fixtures found in '{out}'.", err=True)
             raise typer.Exit(code=1)
             
        latest_run = runs[0]
        fixtures_dir = latest_run / "fixtures"
        typer.echo(f"Auto-selected latest fixtures: {fixtures_dir}")

    # Validate fixtures_dir for replay mode
    if mode == "replay":
        if not fixtures_dir:
            typer.echo("Error: --fixtures-dir is required in replay mode (or use --use-latest-fixtures).", err=True)
            raise typer.Exit(code=1)
        if not fixtures_dir.exists():
            typer.echo(f"Error: Fixtures directory not found: {fixtures_dir}", err=True)
            raise typer.Exit(code=1)
        
        typer.echo(f"replay: loading fixtures from {fixtures_dir}")

    # a) Load scenario
    try:
        scenario = load_scenario(scenario_path)
    except Exception as e:
        typer.echo(f"Error loading scenario: {e}", err=True)
        raise typer.Exit(code=1)

    # b) Create run_id
    run_id = generate_run_id()

    # c) Create runs directory and recorder
    # Recorder handles directory creation (events.jsonl, fixtures/)
    recorder = Recorder(run_id=run_id, runs_dir=out)
    recorder.start()

    try:
        # d) Execute agent
        agent = ResearchAgentStub(recorder=recorder, scenario=scenario, mode=mode, fixtures_dir=fixtures_dir) # type: ignore
        
        start_time = time.time()
        agent.run()
        end_time = time.time()
        
        latency_ms = int((end_time - start_time) * 1000)

        # Gate Check: max_tool_calls
        max_calls = scenario.assertions.max_tool_calls
        actual_calls = agent.tool_calls_count
        passed = actual_calls <= max_calls
        
        gate_payload = {
            "gate": "max_tool_calls",
            "passed": passed,
            "observed": actual_calls,
            "limit": max_calls
        }
        
        # Emit gate_result event
        # Note: step count needs to be maintained. Agent has step count. 
        # But we are outside agent now. 
        # Let's just use agent.step_count + 1
        recorder.log(Event(
            run_id=run_id,
            step=agent.step_count + 1,
            type="gate_result",
            payload=gate_payload
        ))

        # f) Print summary
        typer.echo(f"run_id={run_id}, tool_calls={actual_calls}, latency_ms={latency_ms}, mode={mode}, fixtures_dir={fixtures_dir}")

        if not passed:
            typer.echo(f"Gate failed: max_tool_calls (limit {max_calls}, actual {actual_calls})", err=True)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"Run failed: {e}", err=True)
        # Still raise exit 1
        raise typer.Exit(code=1)
