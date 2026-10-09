"""Conservative, dependency-free installation and repository adoption.

Templates use string.Template. Available fields are project, number, phase_id,
title, outcome, register, date, tool, sync_command, tool_location_note;
canonical *_path and per-document *_link;
current_phase_link and state_link, brief, brief_source, and execution_mode.
Initialization never executes project checks.
"""

from __future__ import annotations

import html
import json
import hashlib
import os
from pathlib import Path
import re
import shlex
import stat
from string import Template
import tempfile
from datetime import datetime, timezone
from dataclasses import dataclass
from urllib.parse import quote

import core


DEFAULT_PATHS = {
    "core": "CORE_KAVAZI_METHOD.md",
    "brief": "docs/PROJECT_BRIEF.md",
    "architecture": "docs/MASTER_ARCHITECTURE.md",
    "methodology": "docs/MASTER_METHODOLOGY.md",
    "technical_core": "docs/MASTER_TECHNICAL_CORE.md",
    "master_plan": "docs/MASTER_IMPLEMENTATION_PLAN.md",
    "phases": "docs/phases",
}
INSTALL_PATH = ".agents/skills/kavazi-method"
INSTRUCTIONS_START = b"<!-- kavazi:instructions:start -->"
INSTRUCTIONS_END = b"<!-- kavazi:instructions:end -->"
REGISTER_START = b"<!-- kavazi:register:start -->"
REGISTER_END = b"<!-- kavazi:register:end -->"
_EXCLUDED_PAYLOAD_NAMES = {"__pycache__", ".git", ".DS_Store"}


@dataclass
class _Write:
    path: Path
    data: bytes
    expected: bytes | None


def _target(root: Path, relative: str) -> Path:
    path = core.safe_path(root, relative)
    if path == root:
        raise core.KavaziError(f"Expected a file or directory below the repository: {relative}")
    for parent in path.parents:
        if parent == root:
            break
        if parent.exists() and not parent.is_dir():
            raise core.KavaziError(f"Parent is not a directory: {parent.relative_to(root)}")
    return path


def _existing(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise core.KavaziError(f"Expected a regular file: {path}")
    try:
        return path.read_bytes()
    except OSError as error:
        raise core.KavaziError(f"Cannot read {path}: {error}") from error


def _add(writes: list[_Write], root: Path, relative: str, data: bytes, *, update=False) -> None:
    path = _target(root, relative)
    existing = _existing(path)
    if existing == data:
        return
    for write in writes:
        if write.path == path:
            if write.data != data:
                raise core.KavaziError(f"Two outputs target the same path: {relative}")
            return
    if existing is not None and not update:
        raise core.KavaziError(f"Preserving conflicting existing file: {relative}. Reconcile it manually; no files were written.")
    writes.append(_Write(path, data, existing))


def _apply(root: Path, writes: list[_Write], *, dry_run: bool) -> list[str]:
    # Validate the complete output set before creating even a directory.
    targets = {write.path for write in writes}
    for write in writes:
        _target(root, write.path.relative_to(root).as_posix())
        if any(parent in targets for parent in write.path.parents):
            raise core.KavaziError(f"Output file is also a parent directory: {write.path.relative_to(root)}")
        if _existing(write.path) != write.expected:
            raise core.KavaziError(f"Target changed during preflight: {write.path.relative_to(root)}; no files were written.")
    proposed = [write.path.relative_to(root).as_posix() for write in writes]
    if dry_run:
        return proposed
    completed: list[str] = []
    temporary: str | None = None
    try:
        for write in writes:
            # Recheck paths immediately before writing; do not follow symlinks.
            _target(root, write.path.relative_to(root).as_posix())
            if _existing(write.path) != write.expected:
                raise core.KavaziError(f"Target changed while writing: {write.path.relative_to(root)}")
            write.path.parent.mkdir(parents=True, exist_ok=True)
            mode = stat.S_IMODE(write.path.stat().st_mode) if write.path.exists() else 0o644
            with tempfile.NamedTemporaryFile(dir=write.path.parent, prefix=".kavazi-write-", delete=False) as handle:
                temporary = handle.name
                handle.write(write.data)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, mode)
            os.replace(temporary, write.path)
            temporary = None
            completed.append(write.path.relative_to(root).as_posix())
    except (OSError, core.KavaziError) as error:
        if temporary is not None:
            try:
                Path(temporary).unlink()
            except OSError:
                pass
        raise core.KavaziError(
            f"Write failed: {error}. Files already written: {', '.join(completed) or 'none'}. "
            "Individual writes are atomic; the operation is not a repository transaction."
        ) from error
    return proposed


def _root(root: Path) -> Path:
    root = Path(root).absolute()
    if root.is_symlink():
        raise core.KavaziError(f"Repository root cannot be a symlink: {root}")
    if not root.is_dir():
        raise core.KavaziError(f"Repository directory does not exist: {root}")
    return root.resolve()


def read_skill_license(source: Path) -> bytes:
    """Read a declared MIT notice before copying any part of a skill.

    This checks the supported package format, not legal equivalence. Release
    builds also require byte-identical root and skill notices.
    """
    for name in ("SKILL.md", "LICENSE"):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Skill requires a regular {name}: {path}")
    skill = (source / "SKILL.md").read_text(encoding="utf-8")
    parts = skill.split("---", 2)
    if len(parts) != 3 or parts[0] or not re.search(r"(?m)^license: MIT\s*$", parts[1]):
        raise ValueError(f"Skill frontmatter must declare license: MIT: {source / 'SKILL.md'}")
    notice = (source / "LICENSE").read_bytes()
    text = notice.decode("utf-8")
    required = (
        "MIT License", "Copyright (c)", "Permission is hereby granted, free of charge",
        "The above copyright notice and this permission notice",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    )
    if not all(fragment in text for fragment in required):
        raise ValueError(f"Skill LICENSE must contain its MIT copyright and permission notice: {source / 'LICENSE'}")
    return notice


def _payload(root: Path, source_skill: Path, writes: list[_Write]) -> None:
    source = Path(source_skill).absolute()
    if source.is_symlink() or not source.is_dir():
        raise core.KavaziError(f"Skill source must be a real directory: {source}")
    source = source.resolve()
    destination = _target(root, INSTALL_PATH)
    if destination.exists() and not destination.is_dir():
        raise core.KavaziError(f"Skill destination is not a directory: {INSTALL_PATH}")
    if source != destination and (source in destination.parents or destination in source.parents):
        raise core.KavaziError("Skill source and destination cannot contain one another.")
    if not (source / "SKILL.md").is_file() or (source / "SKILL.md").is_symlink():
        raise core.KavaziError(f"Skill source has no regular SKILL.md: {source}")
    try:
        read_skill_license(source)
    except (OSError, ValueError) as error:
        raise core.KavaziError(f"Cannot install skill: {error}") from error
    def inspect_error(error):
        raise error
    try:
        for directory, names, files in os.walk(source, followlinks=False, onerror=inspect_error):
            names.sort()
            files.sort()
            # Reject package symlinks instead of copying or following them.
            for name in names + files:
                if (Path(directory) / name).is_symlink():
                    raise core.KavaziError(f"Skill payload contains a symlink: {Path(directory) / name}")
            names[:] = [name for name in names if name not in _EXCLUDED_PAYLOAD_NAMES]
            for name in files:
                if name in _EXCLUDED_PAYLOAD_NAMES or name.endswith((".pyc", ".pyo")):
                    continue
                path = Path(directory) / name
                if not path.is_file():
                    raise core.KavaziError(f"Skill payload contains a nonregular file: {path}")
                relative = (Path(INSTALL_PATH) / path.relative_to(source)).as_posix()
                _add(writes, root, relative, path.read_bytes())
    except OSError as error:
        raise core.KavaziError(f"Cannot inspect skill payload: {error}") from error


def install_skill(root, source_skill, *, dry_run=False) -> list[str]:
    """Install an identical-or-absent payload; refuse all conflicting files."""
    root = _root(Path(root))
    writes: list[_Write] = []
    _payload(root, Path(source_skill), writes)
    return _apply(root, writes, dry_run=dry_run)


def _json(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _paths(root: Path, supplied: dict | None) -> dict[str, str]:
    if supplied is not None and not isinstance(supplied, dict):
        raise core.KavaziError("paths must be an object mapping canonical names to repository-relative paths")
    supplied = supplied or {}
    unknown = set(supplied) - set(DEFAULT_PATHS)
    if unknown:
        raise core.KavaziError(f"Unknown path keys: {', '.join(sorted(unknown))}")
    paths = {**DEFAULT_PATHS, **supplied}
    for key, value in paths.items():
        if not isinstance(value, str) or not value.strip():
            raise core.KavaziError(f"Path {key} must be a nonempty string")
        target = _target(root, value)
        paths[key] = target.relative_to(root).as_posix()
    if len(set(paths.values())) != len(paths):
        raise core.KavaziError("Canonical paths must be distinct")
    document_paths = [_target(root, paths[key]) for key in DEFAULT_PATHS if key != "phases"]
    for value in paths.values():
        if value == ".kavazi" or value.startswith(".kavazi/"):
            raise core.KavaziError(f"Canonical paths cannot use reserved .kavazi metadata: {value}")
    for document in document_paths:
        if _target(root, paths["phases"]) in document.parents:
            raise core.KavaziError(f"Canonical documents cannot be inside the phases directory: {document.relative_to(root)}")
        if any(document in other.parents for other in document_paths + [_target(root, paths["phases"])]):
            raise core.KavaziError(f"Canonical document would also be a directory: {document.relative_to(root)}")
    return paths


def _variables(root: Path, config: dict, target: Path, *, number=1, title="Adoption and baseline", outcome="Establish the current repository baseline and begin verified development.", state=None, source_skill=None) -> dict[str, str]:
    paths = config["paths"]
    script = (Path(source_skill) if source_skill is not None else root / INSTALL_PATH) / "scripts/kavazi.py"
    script = script.resolve()
    try:
        command_path = script.relative_to(root).as_posix()
        if command_path.startswith("-"):
            command_path = "./" + command_path
        location_note = ""
    except ValueError:
        command_path = str(script)
        location_note = "\nThis command uses an external Kavazi directory; keep that directory available.\n"
    if "\r" in command_path:
        raise core.KavaziError(
            "Cannot document a tool path containing a carriage return: Markdown rendering changes it. "
            "Use a source directory without carriage returns."
        )
    tool = f"python3 {shlex.quote(command_path)}"
    command = f"{tool} sync --repo ."
    # Paths may contain quotes, backticks, or Markdown-looking text. Shell
    # quoting preserves the argument; adaptive fencing preserves its display.
    fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", command)), default=0))
    variables = {
        "project": core.markdown_text(config["project"]), "number": str(number), "phase_id": f"P{number:02d}",
        "title": core.markdown_text(title), "outcome": core.markdown_text(outcome),
        "register": core.render_register(state) if state is not None else "",
        "date": datetime.now(timezone.utc).date().isoformat(),
        "tool": tool,
        "sync_command": f"{fence}sh\n{command}\n{fence}",
        "tool_location_note": location_note,
        "execution_mode": config["execution"]["mode"],
        "brief": "No initial user text has been captured. Populate this record from the actual user request before planning implementation; label assumptions explicitly.",
        "brief_source": "uncaptured (no --prompt or --brief-file supplied)",
    }
    for key, value in paths.items():
        variables[f"{key}_path"] = value
        variables[f"{key}_link"] = quote(Path(os.path.relpath(_target(root, value), target.parent)).as_posix(), safe="/")
    phase = _target(root, paths["phases"]) / f"phase-{number:02d}" / "IMPLEMENTATION_PLAN.md"
    variables["current_phase_link"] = quote(Path(os.path.relpath(phase, target.parent)).as_posix(), safe="/")
    variables["state_link"] = quote(Path(os.path.relpath(root / ".kavazi/state.json", target.parent)).as_posix(), safe="/")
    return variables


def _template(source: Path, name: str, variables: dict[str, str]) -> bytes:
    path = source / "assets/templates" / name
    if path.is_symlink() or not path.is_file():
        raise core.KavaziError(f"Missing regular onboarding template: {path}")
    try:
        return Template(path.read_text(encoding="utf-8")).substitute(variables).encode("utf-8")
    except (OSError, UnicodeError, KeyError, ValueError) as error:
        raise core.KavaziError(f"Cannot render template {name}: {error}") from error


def _phase_writes(root: Path, source: Path, config: dict, number: int, title: str, outcome: str, writes: list[_Write], *, source_skill=None) -> None:
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise core.KavaziError("Phase number must be a positive integer")
    if not isinstance(title, str) or not title.strip() or not isinstance(outcome, str) or not outcome.strip():
        raise core.KavaziError("Phase title and outcome must be nonempty strings")
    phase = f"{config['paths']['phases']}/phase-{number:02d}"
    directory = _target(root, phase)
    if directory.exists():
        raise core.KavaziError(f"Phase package already exists: {phase}")
    for filename, template in (("IMPLEMENTATION_PLAN.md", "phase-plan.md"), ("METHODOLOGY.md", "phase-methodology.md"), ("EVIDENCE.md", "phase-evidence.md")):
        relative = f"{phase}/{filename}"
        target = _target(root, relative)
        _add(writes, root, relative, _template(source, template, _variables(
            root, config, target, number=number, title=title, outcome=outcome, source_skill=source_skill)))


def create_phase_files(root, config, number, title, outcome, dry_run=False, *, source_skill=None) -> list[str]:
    """Create only three documents. Caller must establish transition eligibility.

    Templates default to the repository-local installed skill. A CLI executing
    from a source checkout or extracted bundle supplies its own skill directory.
    This helper does not write the ledger or mark any phase complete.
    """
    root = _root(Path(root))
    if not isinstance(config, dict) or not isinstance(config.get("project"), str):
        raise core.KavaziError("Expected validated Kavazi configuration")
    config = {**config, "paths": _paths(root, config.get("paths"))}
    writes: list[_Write] = []
    source = Path(source_skill) if source_skill is not None else root / INSTALL_PATH
    _phase_writes(root, source, config, number, title, outcome, writes, source_skill=source_skill)
    return _apply(root, writes, dry_run=dry_run)


def _instructions(config: dict) -> bytes:
    paths = config["paths"]
    lines = [
        "<!-- kavazi:instructions:start -->", "## Kavazi Method", "",
        "Carry the user's intent into working software. Use an empirical, rational approach and keep the wider product and system context in view.", "",
        f"Read [Core]({quote(paths['core'], safe='/')}) first, then:", "",
        f"1. [Project Brief]({quote(paths['brief'], safe='/')}): supplied input and requirement sources.",
        f"2. [Master Architecture]({quote(paths['architecture'], safe='/')}): project logic and required behavior.",
        f"3. [Master Methodology]({quote(paths['methodology'], safe='/')}): development and verification approaches.",
        f"4. [Master Technical Core]({quote(paths['technical_core'], safe='/')}): logic connected to implementation.",
        f"5. [Master Implementation Plan]({quote(paths['master_plan'], safe='/')}): development sequence.",
        "6. Needed supporting documents and the current phase's plan, methodology, and evidence.", "",
        f"From the repository root, run `python3 {INSTALL_PATH}/scripts/kavazi.py status --repo .` to find the current phase and next action. `.kavazi/state.json` owns that state.", "",
        "Follow `.agents/skills/kavazi-method/SKILL.md`. Make routine missing design choices yourself; keep user requirements, agent assumptions, and observed facts distinct.", "",
        "Keep one unfinished phase. Create no future detailed package until its predecessor has accepted implementation, passing required checks, clean full-scope reviews, and reconciled documents. Every fifth phase also requires a whole-repository review.", "",
        "Record actual choices, observations, failures, and unavailable checks in current-phase evidence. A structural pass does not establish runtime behavior or review quality.", "",
        f"Execution mode: `{config['execution']['mode']}`. " + (
            "Work autonomously within the phase, close it fully, then stop before creating its successor. Only actual human approval recorded with `approve` permits advancement. Never self-approve; the tool stores an attestation and cannot authenticate its origin."
            if config["execution"]["mode"] == "phase_checkpoint" else
            "Continue authorized development through fully reviewed sequential phases toward the requested finished product."
        ),
        "", "Honor user steering and host permissions. Inspect applicable nested agent instructions and resolve conflicting overrides before relying on this entry point.",
        "<!-- kavazi:instructions:end -->",
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _agent_writes(root: Path, config: dict, writes: list[_Write]) -> None:
    path = _target(root, "AGENTS.md")
    content = _existing(path) or b""
    block = _instructions(config)
    starts, ends = content.count(INSTRUCTIONS_START), content.count(INSTRUCTIONS_END)
    if starts or ends:
        if starts != 1 or ends != 1:
            raise core.KavaziError("AGENTS.md has malformed or duplicated Kavazi instruction markers")
        start = content.index(INSTRUCTIONS_START)
        end = content.index(INSTRUCTIONS_END) + len(INSTRUCTIONS_END)
        if end <= start:
            raise core.KavaziError("AGENTS.md Kavazi instruction markers are out of order")
        if content[start:end] != block.rstrip(b"\n"):
            raise core.KavaziError("AGENTS.md managed Kavazi block differs; reconcile it manually before initialization")
        core.validate_managed_block(content.decode("utf-8", errors="surrogateescape"),
                                    INSTRUCTIONS_START.decode(), INSTRUCTIONS_END.decode())
        return
    separator = b"" if not content else (b"\n" if content.endswith(b"\n") else b"\n\n")
    proposed = content + separator + block
    # Preserve even arbitrary prefix bytes, but never hide the new route inside
    # an unfinished user code/HTML block. All adoption outputs remain preflighted.
    core.validate_managed_block(proposed.decode("utf-8", errors="surrogateescape"),
                                INSTRUCTIONS_START.decode(), INSTRUCTIONS_END.decode())
    _add(writes, root, "AGENTS.md", proposed, update=True)


def _capture_brief(prompt, brief_file) -> tuple[str, str] | None:
    if prompt is not None and brief_file is not None:
        raise core.KavaziError("Supply only one of prompt or brief_file")
    if prompt is not None:
        if not isinstance(prompt, str):
            raise core.KavaziError("Prompt must be a string")
        text, source = prompt, "--prompt (user-supplied text, captured verbatim)"
    elif brief_file is not None:
        path = Path(brief_file).expanduser().absolute()
        if path.is_symlink() or not path.is_file():
            raise core.KavaziError(f"Brief source must be a regular UTF-8 file: {path}")
        try:
            # read_bytes avoids universal-newline translation of user input.
            text = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as error:
            raise core.KavaziError(f"Cannot capture UTF-8 brief source {path}: {error}") from error
        source = f"--brief-file: {path} (captured verbatim)"
    else:
        return None
    if not text.strip():
        raise core.KavaziError("Initial user input must contain nonempty text")
    encoded = text.encode("utf-8")
    source += f"; original UTF-8 bytes: {len(encoded)}; SHA-256: {hashlib.sha256(encoded).hexdigest()}"
    # Adaptive fencing prevents arbitrary user Markdown from creating fake
    # evidence headings or document links while preserving the input itself.
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    trailing = "" if text.endswith(("\n", "\r")) else "\n"
    return f"{fence}text\n{text}{trailing}{fence}", core.markdown_text(source)


def init_project(root, source_skill, *, project=None, paths=None, prompt=None, brief_file=None, mode=None, dry_run=False) -> list[str]:
    """Adopt a fresh repository conservatively, or verify an existing adoption.

    Existing canonical files are preserved only when their keys are explicitly
    mapped. An existing mapped master plan receives a generated register by
    appending bytes. Unconfigured inherited phase history requires a deliberate
    migration and is never relabeled as verified Kavazi history.
    """
    root = _root(Path(root))
    captured = _capture_brief(prompt, brief_file)
    if mode is not None and (not isinstance(mode, str) or mode not in {"autonomous", "phase_checkpoint"}):
        raise core.KavaziError("Execution mode must be autonomous or phase_checkpoint")
    source = Path(source_skill).absolute()
    writes: list[_Write] = []
    _payload(root, source, writes)
    config_path = _target(root, ".kavazi/config.json")
    state_path = _target(root, ".kavazi/state.json")
    if config_path.exists():
        config, state = core.load_project(root)
        if project is not None and project != config["project"]:
            raise core.KavaziError("Existing adoption has a different project name; reconcile configuration manually")
        if paths is not None:
            if not isinstance(paths, dict) or any(config["paths"].get(key) != value for key, value in paths.items()):
                raise core.KavaziError("Existing adoption has different canonical paths; reconcile configuration manually")
        if mode is not None and mode != config["execution"]["mode"]:
            raise core.KavaziError("Existing adoption has a different execution mode; reconcile configuration manually")
        if captured is not None:
            brief_content = _existing(_target(root, config["paths"]["brief"]))
            # User text can contain examples of other capture records. Only
            # provenance outside its fenced body identifies the stored input.
            provenance = html.unescape(core.visible_markdown(brief_content.decode("utf-8"))) if brief_content is not None else ""
            if brief_content is None or captured[0].encode("utf-8") not in brief_content or html.unescape(captured[1]) not in provenance:
                raise core.KavaziError("Incoming user input differs from the existing brief; reconcile it deliberately. No files were written.")
        errors = core.validate(root)
        if errors:
            raise core.KavaziError("Existing adoption needs reconciliation: " + "; ".join(errors))
        _agent_writes(root, config, writes)
        return _apply(root, writes, dry_run=dry_run)
    if state_path.exists():
        raise core.KavaziError("Found Kavazi state without configuration; explicit migration is required")
    selected = _paths(root, paths)
    project = root.name if project is None else project
    if not isinstance(project, str) or not project.strip() or "\n" in project or "\r" in project:
        raise core.KavaziError("Project name must be a nonempty single-line string")
    # Look at both selected and default history, because a new mapping must not
    # conceal pre-existing packages and silently restart phase numbering.
    for relative in {selected["phases"], DEFAULT_PATHS["phases"]}:
        phases = _target(root, relative)
        if phases.exists() and (not phases.is_dir() or any(phases.iterdir())):
            raise core.KavaziError(f"Unconfigured existing phase history at {relative}; reconcile it before adoption")
    explicit = set(paths or {})
    for key in DEFAULT_PATHS:
        if key == "phases":
            continue
        target = _target(root, selected[key])
        if target.exists() and key not in explicit:
            raise core.KavaziError(f"Existing {key} at {selected[key]}; provide an explicit path mapping to preserve it")
        if target.exists() and not target.is_file():
            raise core.KavaziError(f"Canonical {key} is not a regular file: {selected[key]}")
        if target.exists():
            try:
                _existing(target).decode("utf-8")
            except UnicodeError as error:
                raise core.KavaziError(
                    f"Canonical {key} at {selected[key]} must be UTF-8; reconcile its encoding before adoption. No files were written."
                ) from error
    if captured is not None and _target(root, selected["brief"]).exists():
        raise core.KavaziError("An explicitly mapped brief already exists and new user input was supplied; reconcile the input before adoption. No files were written.")
    config = {"schema_version": 1, "method_version": core.VERSION, "project": project, "paths": selected, "checks": [], "execution": {"mode": mode or "autonomous"}}
    core.validate_config(root, config)
    state = {"schema_version": 1, "phases": [{
        "number": 1, "title": "Adoption and baseline", "status": "in_progress",
        "next_action": "Inspect the repository baseline, reconcile inherited requirements, and configure required project checks before implementation and closure.",
        "required_checks": [], "closure": None,
    }]}
    # Create canonical documents in their reasoning order.
    for key, template in (("core", None), ("brief", "brief.md"), ("architecture", "architecture.md"), ("methodology", "methodology.md"), ("technical_core", "technical-core.md"), ("master_plan", "master-plan.md")):
        relative = selected[key]
        target = _target(root, relative)
        variables = _variables(root, config, target, state=state)
        if captured is not None:
            variables["brief"], variables["brief_source"] = captured
        content = _existing(target)
        if content is not None:
            if key == "master_plan":
                if REGISTER_START in content or REGISTER_END in content:
                    raise core.KavaziError("Existing master plan has a Kavazi register but no configured ledger; explicit migration is required")
                separator = b"\n" if content.endswith(b"\n") else b"\n\n"
                data = content + separator + core.render_register(state).encode("utf-8") + b"\n"
                core.validate_register_text(data.decode("utf-8"))
                _add(writes, root, relative, data, update=True)
            continue
        if key == "core":
            reference = source / "references/core-method.md"
            if reference.is_symlink() or not reference.is_file():
                raise core.KavaziError(f"Missing regular Core reference: {reference}")
            header = (
                f"# {variables['project']}: Core Kavazi Method\n\n"
                f"Read the [user input and project brief]({variables['brief_link']}), [Architecture]({variables['architecture_link']}), "
                f"[Methodology]({variables['methodology_link']}), [Technical Core]({variables['technical_core_link']}), "
                f"[Master Plan]({variables['master_plan_link']}), then needed supporting documents and the active phase package. "
                f"The [initial adoption package]({variables['current_phase_link']}) records the onboarding baseline.\n\n"
                "The authoritative phase ledger is `.kavazi/state.json`; use the repository-local Kavazi tool to inspect the active phase.\n\n"
            )
            data = header.encode("utf-8") + reference.read_bytes()
        else:
            data = _template(source, template, variables)
        if key == "master_plan":
            core.validate_register_text(data.decode("utf-8"))
        _add(writes, root, relative, data)
    _phase_writes(root, source, config, 1, state["phases"][0]["title"], "Establish the actual repository baseline, accepted scope, and required checks without claiming inherited work is freshly verified.", writes)
    _add(writes, root, ".kavazi/config.json", _json(config))
    _add(writes, root, ".kavazi/state.json", _json(state))
    _agent_writes(root, config, writes)
    return _apply(root, writes, dry_run=dry_run)
