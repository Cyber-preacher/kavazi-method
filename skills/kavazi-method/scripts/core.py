"""Read-only protocol validation and content baselines for Kavazi Method."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import stat
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit

VERSION = "0.1.0"
REGISTER_START = "<!-- kavazi:register:start -->"
REGISTER_END = "<!-- kavazi:register:end -->"
_PATH_KEYS = ("core", "brief", "architecture", "methodology", "technical_core", "master_plan", "phases")
_STATUSES = {"not_planned", "planned", "in_progress", "blocked", "complete"}
_EXCLUDED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
                  ".pytest_cache", "build", "dist"}
_BASELINE = re.compile(r"[0-9a-f]{64}\Z")


class KavaziError(Exception):
    """A project/configuration error suitable for display without a traceback."""


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def safe_path(root, relative):
    """Return an in-repository path, rejecting traversal and symlink components."""
    root = Path(root)
    if root.is_symlink():
        raise KavaziError(f"Repository root is a symlink: {root}")
    if not isinstance(relative, (str, os.PathLike)):
        raise KavaziError("Repository paths must be relative strings")
    value = os.fspath(relative)
    if not isinstance(value, str) or not value or "\x00" in value:
        raise KavaziError("Repository paths must be nonempty relative strings")
    win = PureWindowsPath(value)
    if Path(value).is_absolute() or win.is_absolute() or win.drive or "\\" in value:
        raise KavaziError(f"Path must be repository-relative: {value!r}")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise KavaziError(f"Path must not contain empty, dot, or parent components: {value!r}")
    current = root
    for part in Path(value).parts:
        current = current / part
        if current.is_symlink():
            raise KavaziError(f"Symlink traversal is not supported: {value}")
    return current


def _read_text(path):
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise KavaziError(f"Cannot read {path}: expected a regular file")
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        raise KavaziError(f"Cannot read {path}: {exc}") from exc


def _read_json(path):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise KavaziError(f"Duplicate JSON key in {path}: {key}")
            value[key] = item
        return value
    try:
        return json.loads(_read_text(path), object_pairs_hook=unique_object)
    except (ValueError, RecursionError) as exc:
        raise KavaziError(f"Invalid JSON in {path}: {exc}") from exc


def _config_errors(root, config):
    errors = []
    if not isinstance(config, dict):
        return ["Configuration must be an object"]
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        errors.append("Configuration schema_version must be 1")
    if config.get("method_version") != VERSION:
        errors.append(f"Configuration method_version must be {VERSION}")
    if not _nonempty(config.get("project")):
        errors.append("Configuration project must be a nonempty string")
    execution = config.get("execution")
    if not isinstance(execution, dict) or execution.get("mode") not in ("autonomous", "phase_checkpoint"):
        errors.append("Configuration execution.mode must be autonomous or phase_checkpoint")
    paths = config.get("paths")
    if not isinstance(paths, dict):
        errors.append("Configuration paths must be an object")
    else:
        seen = set()
        for key in _PATH_KEYS:
            value = paths.get(key)
            if not _nonempty(value):
                errors.append(f"Configuration paths.{key} must be a relative path")
                continue
            try:
                safe_path(root, value)
            except KavaziError as exc:
                errors.append(f"Configuration paths.{key}: {exc}")
            if value in seen:
                errors.append(f"Configuration paths must be distinct: {value}")
            if any(part in _EXCLUDED_DIRS for part in Path(value).parts):
                errors.append(f"Configuration paths.{key} cannot use snapshot-excluded directories: {value}")
            seen.add(value)
        valid_paths = [paths.get(k) for k in _PATH_KEYS if _nonempty(paths.get(k))]
        for value in valid_paths:
            if value == ".kavazi" or value.startswith(".kavazi/"):
                errors.append(f"Canonical paths cannot use reserved .kavazi metadata: {value}")
        for key in _PATH_KEYS[:-1]:
            value, phases = paths.get(key), paths.get("phases")
            if _nonempty(value) and _nonempty(phases) and value.startswith(phases + "/"):
                errors.append(f"Canonical paths.{key} cannot be inside the phases directory")
    checks = config.get("checks")
    if not isinstance(checks, list):
        errors.append("Configuration checks must be an array")
    else:
        seen = set()
        for index, check in enumerate(checks):
            label = f"Configuration checks[{index}]"
            if not isinstance(check, dict):
                errors.append(f"{label} must be an object")
                continue
            identifier = check.get("id")
            if not _nonempty(identifier):
                errors.append(f"{label}.id must be a nonempty string")
            elif identifier in seen:
                errors.append(f"Duplicate configured check ID: {identifier}")
            else:
                seen.add(identifier)
            command = check.get("command")
            if not isinstance(command, list) or not command or not all(_nonempty(v) for v in command):
                errors.append(f"{label}.command must be a nonempty string array")
    return errors


def validate_config(root, config):
    """Validate proposed configuration before either loading or onboarding writes."""
    errors = _config_errors(root, config)
    if errors:
        raise KavaziError("Invalid configuration: " + "; ".join(errors))


def validate_register_text(body):
    """Check a proposed register's real Markdown context before writing it."""
    _register_span(body)


def load_project(root):
    """Load safe configuration and parsed state; validate() diagnoses state shape."""
    config = _read_json(safe_path(root, ".kavazi/config.json"))
    validate_config(root, config)
    state = _read_json(safe_path(root, ".kavazi/state.json"))
    return config, state


_HTML_BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|"
    "dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|"
    "frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|"
    "nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|"
    "tfoot|th|thead|title|tr|track|ul"
)


def _code_spans(line):
    """Locate matched inline code; literal comment/anchor examples stay inert."""
    spans, offset = [], 0
    while offset < len(line):
        opener = re.search(r"`+", line[offset:])
        if not opener:
            break
        start, end = offset + opener.start(), offset + opener.end()
        closer = re.search(r"(?<!`)" + re.escape(line[start:end]) + r"(?!`)", line[end:])
        if closer:
            offset = end + closer.end()
            spans.append((start, offset))
        else:
            offset = end
    return spans


def _inline_comments(line, active):
    spans = _code_spans(line) if not active else []
    output, offset = [], 0
    while offset < len(line):
        if active:
            end = line.find("-->", offset)
            stop = len(line) if end < 0 else end + 3
            output.append(" " * (stop - offset))
            offset = stop
            active = end < 0
        else:
            start = line.find("<!--", offset)
            if start < 0:
                output.append(line[offset:])
                break
            code = next((span for span in spans if span[0] <= start < span[1]), None)
            if code:
                output.append(line[offset:code[1]])
                offset = code[1]
            else:
                output.append(line[offset:start])
                offset, active = start, True
    return "".join(output), active


def _html_start(line, paragraph):
    """CommonMark HTML-block boundaries; None terminator means blank-line end."""
    raw = re.match(r"^ {0,3}<(?i:pre|script|style|textarea)(?=\s|>|$)", line)
    if raw:
        return re.compile(r"</(?:pre|script|style|textarea)>", re.IGNORECASE), True
    for start, end in (("<!--", "-->"), ("<?", "?>"), ("<![CDATA[", "]]>")):
        if re.match(r"^ {0,3}" + re.escape(start), line):
            return re.compile(re.escape(end)), True
    if re.match(r"^ {0,3}<![A-Za-z]", line):
        return re.compile(">"), True
    if re.match(r"^ {0,3}</?(?:" + _HTML_BLOCK_TAGS + r")(?=\s|/?>|$)", line, re.IGNORECASE):
        return None, False
    # A standalone ordinary HTML tag cannot interrupt a paragraph.
    tag = r"</?[A-Za-z][A-Za-z0-9-]*(?:\s+[A-Za-z_:][\w.:-]*(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*\s*/?>"
    if not paragraph and re.fullmatch(r" {0,3}" + tag + r"\s*", line):
        return None, False
    return False


def _markdown_views(text, keep_register=False, markers=()):
    """Separate live Markdown from visible HTML anchors, retaining line positions.

    This scanner supports the plain document forms used by Kavazi, rather than
    claiming to be a complete Markdown renderer. Code, comments and raw-text
    HTML never supply evidence headings. HTML blocks can contain real anchors.
    """
    markdown, anchors = [], []
    fence, html_block, comment, paragraph = None, False, False, False
    protected = set(markers) | ({REGISTER_START, REGISTER_END} if keep_register else set())
    for original in text.splitlines():
        if fence:
            match = re.match(r"^ {0,3}([`~]+)\s*$", original)
            if match and set(match[1]) == {fence[0]} and len(match[1]) >= fence[1]:
                fence = None
            markdown.append("")
            anchors.append("")
            continue
        if html_block is not False and html_block[0] is None and not original.strip():
            html_block, paragraph = False, False
        if html_block is not False:
            end, hidden = html_block
            markdown.append("")
            anchors.append("" if hidden else original)
            if end is not None and end.search(original):
                html_block = False
            continue
        if not comment:
            match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", original)
            if match and not (match[1][0] == "`" and "`" in match[2]):
                fence, paragraph = (match[1][0], len(match[1])), False
                markdown.append("")
                anchors.append("")
                continue
            if original in protected or original in (REGISTER_START, REGISTER_END):
                markdown.append(original if original in protected else "")
                anchors.append("")
                paragraph = False
                continue
            block = _html_start(original, paragraph)
            if block is not False:
                end, hidden = block
                html_block, paragraph = block, False
                markdown.append("")
                anchors.append("" if hidden else original)
                if end is not None and end.search(original):
                    html_block = False
                continue
        line, comment = _inline_comments(original, comment)
        markdown.append(line)
        anchor_line = line
        for start, end in reversed(_code_spans(line)):
            anchor_line = anchor_line[:start] + " " * (end - start) + anchor_line[end:]
        anchors.append(anchor_line)
        paragraph = bool(line.strip()) and not re.match(r"^ {0,3}(?:#{1,6}\s|[-=]+\s*$)", line)
    return "\n".join(markdown), "\n".join(anchors)


def _unfenced(text, keep_register=False):
    return _markdown_views(text, keep_register)[0]


def visible_markdown(text):
    """Return live document text for shared record/provenance preflight."""
    return _unfenced(text)


def validate_managed_block(text, start_marker, end_marker):
    """Require a single standalone managed pair in live Markdown context."""
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise KavaziError("Managed instruction block requires exactly one marker pair")
    if text.index(end_marker) < text.index(start_marker):
        raise KavaziError("Managed instruction block markers are out of order")
    visible = _markdown_views(text, markers=(start_marker, end_marker))[0]
    for marker in (start_marker, end_marker):
        if not re.search(r"(?m)^" + re.escape(marker) + r"$", visible):
            raise KavaziError("Managed instruction block markers must occupy their own unfenced, visible Markdown lines; reconcile existing instructions before adoption")


def _headings(text):
    lines = _unfenced(text).splitlines()
    result = []
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            result.append(match[1])
        elif (index and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line)
              and re.match(r"^ {0,3}\S", lines[index - 1])):
            result.append(lines[index - 1].strip())
    return result


def _slugs(text):
    seen = set()
    for heading in _headings(text):
        heading = re.sub(r"<[^>]*>", "", html.unescape(heading)).lower()
        heading = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"[^\w\-\s]", "", heading, flags=re.UNICODE)
        base = re.sub(r"\s", "-", heading)
        slug, suffix = base, 0
        while slug in seen:
            suffix += 1
            slug = f"{base}-{suffix}"
        seen.add(slug)
    visible_html = _markdown_views(text)[1]
    visible_html = re.sub(r"<!--.*?(?:-->|\Z)", "", visible_html, flags=re.DOTALL)
    visible_html = re.sub(r"<(?P<tag>pre|script|style|textarea)(?=\s|>).*?(?:</(?P=tag)\s*>|\Z)",
                          "", visible_html, flags=re.DOTALL | re.IGNORECASE)
    for values in re.findall(r'<a\b[^>]*\bid\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))',
                             visible_html, flags=re.IGNORECASE):
        seen.add(next(value for value in values if value))
    return seen


def _register_span(body):
    if body.count(REGISTER_START) != 1 or body.count(REGISTER_END) != 1:
        raise KavaziError("Master plan must contain exactly one generated register marker pair")
    start, end = body.index(REGISTER_START), body.index(REGISTER_END)
    if end < start:
        raise KavaziError("Master plan generated register markers are out of order")
    visible = _unfenced(body, keep_register=True)
    for marker in (REGISTER_START, REGISTER_END):
        if not re.search(r"(?m)^" + re.escape(marker) + r"\r?$", visible):
            raise KavaziError("Master plan register markers must occupy their own unfenced lines")
    return start, end + len(REGISTER_END)


def markdown_text(value):
    """Render supplied display text literally, without creating Markdown syntax."""
    value = html.escape(str(value), quote=False)
    return re.sub(r"[\\`*_\[\]()#|~\r\n]", lambda match: f"&#{ord(match[0])};", value)


def _cell(value):
    return markdown_text(str(value).replace("\r", " ").replace("\n", " "))


def render_register(state):
    if not isinstance(state, dict) or not isinstance(state.get("phases"), list):
        raise KavaziError("State phases must be an array to render the register")
    rows = [REGISTER_START, "| Phase | Title | Status | Next action |", "|---|---|---|---|"]
    for phase in state["phases"]:
        if not isinstance(phase, dict) or type(phase.get("number")) is not int or phase["number"] < 1:
            raise KavaziError("Each phase needs a positive integer number to render the register")
        if not all(_nonempty(phase.get(key)) for key in ("title", "status", "next_action")):
            raise KavaziError("Each phase needs a title, status and next_action to render the register")
        rows.append(f"| {phase['number']:02d} | {_cell(phase['title'])} | {_cell(phase['status'])} | {_cell(phase['next_action'])} |")
    return "\n".join(rows + [REGISTER_END])


def sync_register(root, config, state):
    errors = _config_errors(root, config)
    if errors:
        raise KavaziError("Invalid configuration: " + "; ".join(errors))
    body = _read_text(safe_path(root, config["paths"]["master_plan"]))
    start, end = _register_span(body)
    return body[:start] + render_register(state) + body[end:]


def snapshot(root, config):
    """Fingerprint scoped regular paths/content; phase records cannot hash themselves."""
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise KavaziError(f"Repository root must be an existing nonsymlink directory: {root}")
    errors = _config_errors(root, config)
    if errors:
        raise KavaziError("Invalid snapshot configuration: " + "; ".join(errors))
    phases_path = config["paths"]["phases"]
    master_path = config["paths"]["master_plan"]
    _register_span(_read_text(safe_path(root, master_path)))
    digest = hashlib.sha256(b"kavazi-snapshot-v1\0")
    files = []
    def walk_error(exc):
        raise KavaziError(f"Cannot inspect repository tree: {exc}") from exc
    for folder, directories, names in os.walk(root, followlinks=False, onerror=walk_error):
        directories[:] = sorted(d for d in directories if d not in _EXCLUDED_DIRS)
        for name in directories:
            path = Path(folder) / name
            if path.is_symlink():
                raise KavaziError(f"Symlink in snapshot scope: {path.relative_to(root)}")
        for name in names:
            path = Path(folder) / name
            relative = path.relative_to(root).as_posix()
            if name == ".git" or relative == ".kavazi/state.json":
                continue
            parts = relative.split("/")
            prefix = phases_path.split("/")
            if parts[:len(prefix)] == prefix and len(parts) == len(prefix) + 2 and re.fullmatch(r"phase-\d{2,}", parts[-2]) and parts[-1] == "EVIDENCE.md":
                continue
            if path.is_symlink():
                raise KavaziError(f"Symlink in snapshot scope: {relative}")
            try:
                if not stat.S_ISREG(path.stat().st_mode):
                    raise KavaziError(f"Nonregular file in snapshot scope: {relative}")
            except OSError as exc:
                raise KavaziError(f"Cannot inspect {relative}: {exc}") from exc
            files.append((relative, path))
    for relative, path in sorted(files):
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise KavaziError(f"Cannot fingerprint {relative}: {exc}") from exc
        if relative == master_path:
            try:
                body = content.decode("utf-8")
            except UnicodeError as exc:
                raise KavaziError(f"Master plan must be UTF-8: {exc}") from exc
            start, end = _register_span(body)
            content = (body[:start] + REGISTER_START + "\n" + REGISTER_END + body[end:]).encode("utf-8")
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _link_errors(root, source, body):
    errors = []
    visible = _unfenced(body)
    # Inline code does not contain navigable Markdown links.
    visible = re.sub(r"(`+)[^`\n]*?\1", "", visible)
    targets = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+[^)]*)?\)", visible)
    definitions = dict(re.findall(r"^ {0,3}\[([^]\n]+)\]:\s*(<[^>]*>|\S+)", visible, flags=re.MULTILINE))
    definitions = {key.lower(): value for key, value in definitions.items()}
    targets.extend(definitions.values())
    for label, ref in re.findall(r"!?\[([^]\n]+)\]\[([^]\n]*)\]", visible):
        identifier = (ref or label).lower()
        if identifier not in definitions:
            errors.append(f"{source}: missing Markdown link definition [{identifier}]")
        else:
            targets.append(definitions[identifier])
    for target in targets:
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        try:
            parsed = urlsplit(target)
        except ValueError as exc:
            errors.append(f"{source}: malformed link {target}: {exc}")
            continue
        if parsed.scheme or parsed.netloc:
            continue
        target_path, anchor = unquote(parsed.path), unquote(parsed.fragment)
        if target_path.startswith("/") or "\\" in target_path:
            errors.append(f"{source}: local link must be relative: {target}")
            continue
        # Links may use .. as long as normalization remains inside this repository.
        current = list(Path(source).parent.parts)
        escaped = False
        for part in target_path.split("/") if target_path else []:
            if part in ("", "."):
                continue
            if part == "..":
                if not current:
                    escaped = True
                    break
                current.pop()
            else:
                current.append(part)
        relative = "/".join(current) if target_path else source
        if escaped or not relative:
            errors.append(f"{source}: local link escapes repository: {target}")
            continue
        try:
            path = safe_path(root, relative)
            if not path.exists():
                errors.append(f"{source}: missing local link target: {target}")
            elif anchor and path.is_file():
                if anchor not in _slugs(_read_text(path)):
                    errors.append(f"{source}: missing heading anchor: {target}")
            elif anchor:
                errors.append(f"{source}: heading anchor requires a file: {target}")
        except (KavaziError, ValueError) as exc:
            errors.append(f"{source}: invalid local link {target}: {exc}")
    return errors


def _evidence_ids(root, config, number):
    path = f"{config['paths']['phases']}/phase-{number:02d}/EVIDENCE.md"
    counts = {}
    for heading in _headings(_read_text(safe_path(root, path))):
        identifier = re.split(r"\s|[—–:]", heading, maxsplit=1)[0]
        counts[identifier] = counts.get(identifier, 0) + 1
    return path, counts


def _approval_errors(phase, approval, evidence_ids, evidence_path):
    label = f"Phase {phase['number']:02d} human approval"
    if not isinstance(approval, dict):
        return [f"{label} must be an object"]
    errors = []
    if phase.get("status") != "complete":
        errors.append(f"{label} can only be recorded after the phase is complete")
    for key in ("summary", "granted_by"):
        if not _nonempty(approval.get(key)):
            errors.append(f"{label}.{key} must be a nonempty string")
    identifier = approval.get("evidence")
    if not _nonempty(identifier) or evidence_ids.get(identifier) != 1:
        errors.append(f"{label}: evidence must resolve to one unfenced heading ID in {evidence_path}: {identifier!r}")
    return errors


def validate_human_approval(root, config, phase, approval):
    """Validate a recorded human decision, without claiming to authenticate it."""
    path, identifiers = _evidence_ids(root, config, phase["number"])
    errors = _approval_errors(phase, approval, identifiers, path)
    if errors:
        raise KavaziError("; ".join(errors))


def _closure_errors(root, config, phase):
    number = phase["number"]
    label = f"Phase {number:02d} closure"
    errors = []
    closure = phase.get("closure")
    if not isinstance(closure, dict):
        return [f"{label} must be a recorded object"]
    baseline = closure.get("baseline")
    if not isinstance(baseline, str) or not _BASELINE.fullmatch(baseline):
        errors.append(f"{label}.baseline must be 64 lowercase hexadecimal characters")
    try:
        evidence_path, evidence_ids = _evidence_ids(root, config, number)
    except KavaziError as exc:
        return errors + [str(exc)]
    def evidence(value, context):
        if not _nonempty(value) or evidence_ids.get(value) != 1:
            errors.append(f"{label} {context}: evidence must resolve to one unfenced heading ID in {evidence_path}: {value!r}")
    for key in ("acceptance", "documentation"):
        record = closure.get(key)
        if not isinstance(record, dict):
            errors.append(f"{label}.{key} must be an object")
            continue
        evidence(record.get("evidence"), key)
        if not _nonempty(record.get("summary")):
            errors.append(f"{label}.{key}.summary must describe observed results")
    if "human_approval" in closure:
        errors.extend(_approval_errors(phase, closure["human_approval"], evidence_ids, evidence_path))
    required = phase.get("required_checks", [])
    required = required if isinstance(required, list) else []
    if not required:
        errors.append(f"{label} requires at least one configured required check")
    configured = {check["id"] for check in config["checks"]}
    checks = closure.get("checks")
    check_ids = set()
    if not isinstance(checks, list):
        errors.append(f"{label}.checks must be an array")
    else:
        for index, check in enumerate(checks):
            context = f"checks[{index}]"
            if not isinstance(check, dict):
                errors.append(f"{label}.{context} must be an object")
                continue
            identifier = check.get("id")
            if not _nonempty(identifier) or identifier not in configured:
                errors.append(f"{label}.{context}.id must identify a configured check")
            elif identifier in check_ids:
                errors.append(f"{label}: duplicate check result {identifier}")
            else:
                check_ids.add(identifier)
            if check.get("result") != "passed":
                errors.append(f"{label}.{context} must have an observed passed result")
            evidence(check.get("evidence"), context)
        for identifier in required:
            if isinstance(identifier, str) and identifier not in check_ids:
                errors.append(f"{label}: missing required check result {identifier}")
    reviews = closure.get("reviews")
    last = {}
    findings = {}
    if not isinstance(reviews, list) or not reviews:
        errors.append(f"{label}.reviews must be a nonempty array")
    else:
        for index, review in enumerate(reviews):
            context = f"reviews[{index}]"
            if not isinstance(review, dict):
                errors.append(f"{label}.{context} must be an object")
                continue
            kind = review.get("kind")
            if kind not in ("phase", "whole_repository"):
                errors.append(f"{label}.{context}.kind must be phase or whole_repository")
            else:
                last[kind] = review
            if not _nonempty(review.get("reviewer")):
                errors.append(f"{label}.{context}.reviewer must identify the actual reviewer")
            if type(review.get("fresh")) is not bool:
                errors.append(f"{label}.{context}.fresh must be boolean")
            coverage = review.get("coverage")
            if not isinstance(coverage, list) or not coverage or not all(_nonempty(item) for item in coverage):
                errors.append(f"{label}.{context}.coverage must be a nonempty string array")
            if not _nonempty(review.get("refactoring")):
                errors.append(f"{label}.{context}.refactoring must record a reason or why no refactor was warranted")
            evidence(review.get("evidence"), context)
            round_findings = review.get("findings")
            if not isinstance(round_findings, list):
                errors.append(f"{label}.{context}.findings must be an array")
                continue
            seen = set()
            for finding in round_findings:
                if not isinstance(finding, dict):
                    errors.append(f"{label}.{context}: findings must be objects")
                    continue
                identifier = finding.get("id")
                if not _nonempty(identifier):
                    errors.append(f"{label}.{context}: finding ID must be nonempty")
                elif identifier in seen:
                    errors.append(f"{label}.{context}: duplicate finding ID {identifier}")
                else:
                    seen.add(identifier)
                    findings[identifier] = finding.get("status")
                if finding.get("status") not in ("open", "resolved", "rejected"):
                    errors.append(f"{label}.{context}: finding status must be open, resolved, or rejected")
                evidence(finding.get("evidence"), context + " finding")
    kinds = ["phase"] + (["whole_repository"] if number % 5 == 0 else [])
    for kind in kinds:
        if kind not in last or last[kind].get("fresh") is not True:
            errors.append(f"{label}: last {kind} review must be fresh")
    for identifier, status in findings.items():
        if status not in ("resolved", "rejected"):
            errors.append(f"{label}: unresolved earlier finding {identifier}")
    return errors


def validate(root, closure=False):
    """Report structural/record errors without running configured product commands."""
    errors = []
    try:
        config, state = load_project(root)
    except KavaziError as exc:
        return [str(exc)]
    if not isinstance(state, dict):
        return ["State must be an object"]
    if type(state.get("schema_version")) is not int or state["schema_version"] != 1:
        errors.append("State schema_version must be 1")
    phases = state.get("phases")
    if not isinstance(phases, list) or not phases:
        return errors + ["State phases must be a nonempty array"]
    configured = {check["id"] for check in config["checks"]}
    created = []
    future_seen = False
    unfinished_seen = False
    valid_numbers = set()
    canonical = [config["paths"][key] for key in _PATH_KEYS[:-1]]
    for index, phase in enumerate(phases):
        label = f"Phase entry {index + 1}"
        if not isinstance(phase, dict):
            errors.append(f"{label} must be an object")
            continue
        number = phase.get("number")
        if type(number) is not int or number != index + 1:
            errors.append(f"{label}: numbers must be contiguous positive integers from 1")
            continue
        valid_numbers.add(number)
        for key in ("title", "next_action"):
            if not _nonempty(phase.get(key)):
                errors.append(f"{label}.{key} must be a nonempty string")
        status = phase.get("status")
        if not isinstance(status, str) or status not in _STATUSES:
            errors.append(f"{label}.status is unsupported")
            continue
        required = phase.get("required_checks")
        if not isinstance(required, list) or not all(_nonempty(item) for item in required):
            errors.append(f"{label}.required_checks must be a string array")
        else:
            if len(set(required)) != len(required):
                errors.append(f"{label}: required_checks must be unique")
            for identifier in required:
                if identifier not in configured:
                    errors.append(f"{label}: unknown required check {identifier}")
        if "closure" not in phase:
            errors.append(f"{label} must declare closure (null until recorded)")
        phase_path = f"{config['paths']['phases']}/phase-{number:02d}"
        try:
            directory = safe_path(root, phase_path)
        except KavaziError as exc:
            errors.append(str(exc))
            continue
        if status == "not_planned":
            future_seen = True
            if directory.exists():
                errors.append(f"{label}: future not_planned phase must not have a package")
            if phase.get("closure") is not None:
                errors.append(f"{label}: not_planned phase cannot have closure")
            continue
        created.append(phase)
        if config["execution"]["mode"] == "phase_checkpoint" and len(created) > 1:
            predecessor = created[-2].get("closure")
            if not isinstance(predecessor, dict) or "human_approval" not in predecessor:
                errors.append(f"{label}: predecessor requires recorded human approval before its successor")
        if future_seen:
            errors.append(f"{label}: created phases must form a contiguous prefix")
        if unfinished_seen:
            errors.append(f"{label}: predecessor must fully close before another package is created")
        if status != "complete":
            unfinished_seen = True
        for filename in ("IMPLEMENTATION_PLAN.md", "METHODOLOGY.md", "EVIDENCE.md"):
            canonical.append(f"{phase_path}/{filename}")
        if status == "complete" or phase.get("closure") is not None:
            errors.extend(_closure_errors(root, config, phase))
    if not created:
        errors.append("State must contain a created current phase")
    try:
        phases_directory = safe_path(root, config["paths"]["phases"])
        if not phases_directory.is_dir():
            errors.append("Configured phases path must be an existing directory")
        else:
            for child in phases_directory.iterdir():
                if child.is_symlink():
                    errors.append(f"Symlink in phase packages: {child.name}")
                    continue
                match = re.fullmatch(r"phase-(\d+)", child.name)
                if match:
                    number = int(match[1])
                    if number not in valid_numbers or child.name != f"phase-{number:02d}":
                        errors.append(f"Unregistered or noncanonical phase package: {child.name}")
                elif child.name.startswith("phase-"):
                    errors.append(f"Unregistered or noncanonical phase package: {child.name}")
    except (KavaziError, OSError) as exc:
        errors.append(str(exc))
    for relative in canonical:
        try:
            body = _read_text(safe_path(root, relative))
            errors.extend(_link_errors(root, relative, body))
        except KavaziError as exc:
            errors.append(str(exc))
    try:
        actual = _read_text(safe_path(root, config["paths"]["master_plan"]))
        if actual != sync_register(root, config, state):
            errors.append("Master plan generated register is stale; run sync")
    except KavaziError as exc:
        errors.append(str(exc))
    if created:
        current = created[-1]
        if closure and current.get("closure") is None:
            errors.extend(_closure_errors(root, config, current))
        if closure or current["status"] == "complete":
            record = current.get("closure")
            if isinstance(record, dict):
                try:
                    observed = snapshot(root, config)
                    if record.get("baseline") != observed:
                        errors.append(f"Phase {current['number']:02d} closure baseline differs from the current repository snapshot")
                except KavaziError as exc:
                    errors.append(str(exc))
    return errors
