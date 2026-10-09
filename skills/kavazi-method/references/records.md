# Phase records and transitions

Schema version 1; method version 0.1.0. This guide explains how to record observed results and use the tool to advance a phase. Project-specific technical decisions belong in the Master Technical Core.

## Configuration and state

`.kavazi/config.json` owns document paths (`brief`, `core`, `architecture`, `methodology`, `technical_core`, `master_plan`, `phases`), check definitions, and `execution.mode`: `autonomous` or `phase_checkpoint`.

`.kavazi/state.json` owns phase status and next action. It contains `schema_version: 1` and a contiguous `phases` list starting at 1. Each phase has `number`, `title`, `status`, `next_action`, `required_checks`, and `closure`. Status is `not_planned`, `planned`, `in_progress`, `blocked`, or `complete`. Future `not_planned` entries have no package. At most one created phase is unfinished; created predecessors need supported completion.

Define checks as unique IDs with nonempty command arrays in configuration. Reference those IDs in the current phase's `required_checks` array. For example:

```json
{"id": "project-tests", "command": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]}
```

This is a check definition inside `config.checks`; the phase would reference `"required_checks": ["project-tests"]`. Choose commands suitable for the actual project. The tool describes these commands but never executes them.

The master register between `<!-- kavazi:register:start -->` and `<!-- kavazi:register:end -->` is generated. Edit state, then run `sync --repo .`. Keep editable status in the ledger rather than the register or phase documents.

## Record evidence first

Use visible headings such as `## P01-E002 — Acceptance` in the current phase's `EVIDENCE.md`. Headings inside fences, comments, or raw HTML are examples and cannot be evidence targets. The scanner supports plain Markdown forms rather than a complete CommonMark renderer.

Record the actual procedure, baseline, environment, inputs, observations, failures, limits, and follow-up. Preserve earlier failures and every review round. Hashing a tree cannot renew stale observations.

When implementation, checks, and full reviews are ready:

1. Reconcile the input, architecture, methodology, Technical Core, affected documents, and delivered files.
2. Run `snapshot --repo .` to obtain the current fingerprint. It must describe the state actually checked and reviewed. If substantive files changed afterward, renew the affected checks and review.
3. Enter the supported record in the current phase's `closure` field in `.kavazi/state.json`. Preserve the rest of that file and the phase's metadata. State and phase evidence are excluded from the fingerprint so recording closure does not invalidate itself.
4. Run `check --repo . --closure`, then `close --repo .`. These validate the records and mark completion; they do not perform reviews or run project checks.
5. In `autonomous`, continue with `next --repo . --title "Next phase" --outcome "Accepted outcome"`. In `phase_checkpoint`, stop after closure. After actual human approval, append its evidence and record it with `approve` before `next`.

Example shape for the current phase's `closure` field; replace every example with actual observations:

```json
{
  "baseline": "fingerprint from the observed snapshot",
  "acceptance": {"evidence": "P01-E002", "summary": "Actual accepted outcomes and limits"},
  "checks": [{"id": "project-tests", "result": "passed", "evidence": "P01-E002"}],
  "reviews": [{
    "kind": "phase", "reviewer": "Actual reviewer", "fresh": true,
    "coverage": ["Entire phase scope and integrations actually inspected"],
    "findings": [], "refactoring": "Actual rationale or why no change was warranted",
    "evidence": "P01-E003"
  }],
  "documentation": {"evidence": "P01-E004", "summary": "Affected documents actually reconciled"}
}
```

Each finding is `{"id": "F001", "status": "open|resolved|rejected", "evidence": "P01-E003"}`. Keep rounds in order and use stable IDs. A false-positive rejection needs supporting evidence. An earlier open finding cannot disappear from a later empty list. The final round of each required kind must be fresh, fully scoped, and free of unresolved findings. Every fifth phase also needs `kind: "whole_repository"` with whole-project coverage and evidence.

## Human checkpoints

Only actual human approval given after phase completion permits advancement in `phase_checkpoint`. Record its source and context in a visible evidence entry, then use:

```text
python3 .agents/skills/kavazi-method/scripts/kavazi.py approve --repo . --evidence P01-E005 --summary "Actual approval to continue" --by "Actual approver"
```

Use the actual evidence ID and approver. Never self-approve or turn an agent decision into human approval. `approve` stores `closure.human_approval` with `evidence`, `summary`, and `granted_by`. It checks the record's shape and evidence reference; it cannot authenticate human origin. `next` validates predecessor closure, the current baseline, and required checkpoint approval before creating exactly one successor package.

## What the fingerprint covers

`snapshot` hashes scoped regular file paths and bytes and rejects scoped symlinks. It excludes Git metadata, fixed dependency, build, and cache directories, phase state, and phase evidence. Only the generated master-register block is normalized. Substantive project documents, configuration, tools, source, assets, and tests remain covered. Consult the command help or implementation for exact exclusions. The fingerprint describes that file tree, not external dependencies or the execution environment.

Completed phases retain historical fingerprints. Current closure and advancement require a matching current fingerprint. Failed, unavailable, missing, or `not_run` checks cannot satisfy closure. No command supplies a missing review or truthful execution evidence; maintainers and reviewers must inspect the observations behind the records.
