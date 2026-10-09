#!/usr/bin/env python3
"""Repository-local Kavazi tooling. Requires Python 3.10+, no dependencies."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import stat
import tempfile

# Read-only commands and dry runs must not create caches in the installed payload.
sys.dont_write_bytecode = True

from core import VERSION, KavaziError, load_project, render_register, safe_path
from core import snapshot, sync_register, validate
from core import validate_human_approval
from onboarding import create_phase_files, init_project, install_skill


def write_text(path: Path, body: str) -> None:
    """Replace one regular file atomically; callers preflight the complete action."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".kavazi-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(body)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_state(root: Path, state: dict) -> None:
    write_text(safe_path(root, ".kavazi/state.json"), json.dumps(state, indent=2) + "\n")


def ensure_valid(root: Path, *, closure: bool = False) -> None:
    errors = validate(root, closure=closure)
    if errors:
        raise KavaziError("\n".join(errors))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=f"Kavazi {VERSION}")
    commands = result.add_subparsers(dest="command", required=True, title="commands")
    purposes = {
        "install": "Install the repository-local skill without creating project records.",
        "init": "Install the skill and create or preserve the project's starting documents.",
        "status": "Show the current phase, execution mode, and next action.",
        "check": "Validate project structure and recorded evidence; does not run product checks.",
        "doctor": "Inspect the installation and explain project-record issues.",
        "snapshot": "Print a fingerprint of the files covered by phase acceptance.",
        "sync": "Refresh the master plan's generated phase register from state.",
        "close": "Validate recorded acceptance and reviews, then close the current phase; does not run tests or reviews.",
        "approve": "Record actual human approval to advance after a closed checkpoint phase.",
        "next": "Create only the immediately next phase after closure and any required approval.",
    }
    for name, purpose in purposes.items():
        command = commands.add_parser(name, help=purpose, description=purpose)
        command.add_argument("--repo", type=Path, default=Path.cwd(), help="target repository or directory")
        if name in {"install", "init", "sync", "close", "approve", "next"}:
            command.add_argument("--dry-run", action="store_true", help="report proposed changes without writing")
        if name == "init":
            command.add_argument("--project", help="project name (defaults to target directory name)")
            for flag in ("core", "brief", "architecture", "methodology", "technical-core", "master-plan", "phases"):
                command.add_argument(f"--{flag}", help="explicit repository-relative path for this authoritative document or phase directory")
            source = command.add_mutually_exclusive_group()
            source.add_argument("--prompt", help="capture initial user text verbatim in the project brief")
            source.add_argument("--brief-file", type=Path, help="capture initial user text from a regular UTF-8 file")
            command.add_argument("--mode", choices=("autonomous", "phase_checkpoint"),
                                 help="execution mode (new adoption defaults to autonomous; omission preserves existing mode)")
        if name == "check":
            command.add_argument("--closure", action="store_true", help="also require complete closure records for the current file baseline")
        if name == "next":
            command.add_argument("--title", required=True, help="next phase title")
            command.add_argument("--outcome", required=True, help="next phase intended outcome")
        if name == "approve":
            command.add_argument("--evidence", required=True, help="current phase evidence heading recording explicit human approval")
            command.add_argument("--summary", required=True, help="what the human approved")
            command.add_argument("--by", required=True, help="actual human who explicitly granted approval; agents cannot self-grant")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = args.repo.expanduser().absolute()
        if root.is_symlink():
            raise KavaziError("Target repository cannot be a symlink; use its actual directory.")
        root = root.resolve()
        if not root.is_dir():
            raise KavaziError(f"Target directory does not exist: {root}")
        source = Path(__file__).resolve().parents[1]
        if args.command in {"install", "init"}:
            if args.command == "install":
                changes = install_skill(root, source, dry_run=args.dry_run)
            else:
                paths = {name: getattr(args, name) for name in (
                    "core", "brief", "architecture", "methodology", "technical_core", "master_plan", "phases"
                ) if getattr(args, name) is not None}
                changes = init_project(root, source, project=args.project,
                                       paths=paths or None, prompt=args.prompt,
                                       brief_file=args.brief_file, mode=args.mode,
                                       dry_run=args.dry_run)
            print(("Would write" if args.dry_run else "Wrote") + ":")
            print("\n".join(changes) if changes else "No changes; already installed.")
            if args.command == "init":
                print("Read AGENTS.md, preserve the captured user input, fill the source-backed masters and current phase, then configure and run your project checks.")
            return 0

        config, state = load_project(root)
        if args.command == "check":
            ensure_valid(root, closure=args.closure)
            print("Kavazi records are valid" + ("; current closure is supported." if args.closure else "."))
            print("Record validation does not execute project checks or establish review substance.")
            return 0
        if args.command == "sync":
            errors = [error for error in validate(root)
                      if error != "Master plan generated register is stale; run sync"]
            if errors:
                raise KavaziError("\n".join(errors))
            body = sync_register(root, config, state)
            destination = safe_path(root, config["paths"]["master_plan"])
            if not args.dry_run:
                write_text(destination, body)
            print(("Would update " if args.dry_run else "Updated ") + config["paths"]["master_plan"])
            return 0
        if args.command == "snapshot":
            print(snapshot(root, config))
            return 0
        if args.command == "doctor":
            errors = validate(root)
            print(f"Python {sys.version.split()[0]}; Kavazi {VERSION}; repository: {root}")
            print("Installed skill: " + ("present" if (root / ".agents/skills/kavazi-method/SKILL.md").is_file() else "absent (run install)"))
            overrides = sorted(p.relative_to(root).as_posix() for p in root.rglob("AGENTS.override.md")
                               if not any(part in {".git", "node_modules", ".venv"} for part in p.parts))
            if overrides:
                print("Instruction overrides to inspect: " + ", ".join(overrides))
            if not config["checks"]:
                print("Project check definitions are empty; configure them before closure.")
            for error in errors:
                print("ERROR: " + error)
            if not errors:
                print("No structural errors. Verify skill discovery and applicable host instructions in a new agent session.")
            return 1 if errors else 0

        ensure_valid(root)
        created = [phase for phase in state["phases"] if phase["status"] != "not_planned"]
        if not created:
            raise KavaziError("No current or completed phase package; initialize or reconcile the ledger.")
        current = created[-1]
        if args.command == "status":
            print(f"Phase {current['number']:02d}: {current['title']} ({current['status']})")
            print(f"Execution mode: {config['execution']['mode']}")
            print(f"Next action: {current['next_action']}")
            print(f"Package: {config['paths']['phases']}/phase-{current['number']:02d}/")
            print("Required checks: " + (", ".join(current["required_checks"]) or "not yet selected"))
            if config["execution"]["mode"] == "phase_checkpoint":
                approval = (current.get("closure") or {}).get("human_approval")
                if current["status"] == "complete" and approval is None:
                    print("Waiting for explicit human approval before creating or planning the next phase.")
                elif approval is not None:
                    print(f"Human checkpoint: approval recorded from {approval['granted_by']}.")
                else:
                    print("Human checkpoint: explicit approval will be required after phase closure.")
            return 0
        if args.command == "close":
            if current["status"] == "blocked":
                raise KavaziError("Resolve the blocked prerequisite and return the phase to in_progress before closure.")
            ensure_valid(root, closure=True)
            current["status"] = "complete"
            current["next_action"] = (
                "Wait for explicit human approval before deriving the immediately next phase."
                if config["execution"]["mode"] == "phase_checkpoint" and current["closure"].get("human_approval") is None else
                "Derive only the immediately next phase from accepted evidence."
            )
            body = sync_register(root, config, state)
            master = safe_path(root, config["paths"]["master_plan"])
            safe_path(root, ".kavazi/state.json")
            if not args.dry_run:
                save_state(root, state)
                write_text(master, body)
            print(("Would close " if args.dry_run else "Closed ") + f"Phase {current['number']:02d}; no next package was created.")
            if config["execution"]["mode"] == "phase_checkpoint" and current["closure"].get("human_approval") is None:
                print("Waiting for explicit human approval. Agents must not grant their own approval.")
            return 0
        if args.command == "approve":
            if config["execution"]["mode"] != "phase_checkpoint":
                raise KavaziError("Human phase approval is recorded only in phase_checkpoint mode.")
            if current["status"] != "complete":
                raise KavaziError("Close the current phase with supported acceptance and reviews before recording human approval.")
            ensure_valid(root, closure=True)
            approval = {"evidence": args.evidence.strip(), "summary": args.summary.strip(),
                        "granted_by": args.by.strip()}
            validate_human_approval(root, config, current, approval)
            existing = current["closure"].get("human_approval")
            if existing is not None:
                if existing != approval:
                    raise KavaziError("A different human approval is already recorded; preserve its provenance and reconcile deliberately.")
                print("Identical human approval is already recorded; no changes.")
                return 0
            current["closure"]["human_approval"] = approval
            current["next_action"] = "Derive only the immediately next phase from accepted evidence and recorded human approval."
            body = sync_register(root, config, state)
            master = safe_path(root, config["paths"]["master_plan"])
            safe_path(root, ".kavazi/state.json")
            if not args.dry_run:
                save_state(root, state)
                write_text(master, body)
            print(("Would record " if args.dry_run else "Recorded ") + f"human approval from {approval['granted_by']} for Phase {current['number']:02d}.")
            print("This records an attestation; agents must not self-grant or invent human authorization.")
            return 0
        if args.command == "next":
            if current["status"] != "complete":
                raise KavaziError(f"Phase {current['number']:02d} is unfinished; do not create its successor.")
            ensure_valid(root, closure=True)
            if config["execution"]["mode"] == "phase_checkpoint" and current["closure"].get("human_approval") is None:
                raise KavaziError("The completed phase is waiting for explicit human approval; do not create or plan its successor.")
            number = current["number"] + 1
            if not args.title.strip() or not args.outcome.strip():
                raise KavaziError("Next phase title and outcome must be nonempty.")
            candidate = next((phase for phase in state["phases"] if phase["number"] == number), None)
            phase = {"number": number, "title": args.title.strip(), "status": "planned",
                     "next_action": "Frame acceptance criteria and methods before implementation.",
                     "required_checks": [], "closure": None}
            if candidate is None:
                state["phases"].append(phase)
            else:
                candidate.clear()
                candidate.update(phase)
            body = sync_register(root, config, state)
            master = safe_path(root, config["paths"]["master_plan"])
            safe_path(root, ".kavazi/state.json")
            # Preflight package files before ledger/register writes.
            changes = create_phase_files(root, config, number, args.title.strip(), args.outcome.strip(),
                                         dry_run=True, source_skill=source)
            if not args.dry_run:
                create_phase_files(root, config, number, args.title.strip(), args.outcome.strip(), source_skill=source)
                save_state(root, state)
                write_text(master, body)
            print(("Would create " if args.dry_run else "Created ") + f"only Phase {number:02d}:")
            print("\n".join(changes))
            return 0
        raise KavaziError("Unknown command")
    except (KavaziError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Kavazi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
