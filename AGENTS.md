# Working on Kavazi Method

Use an empirical, rational approach. Keep the wider project in view, and let observed results guide decisions.

## Read before working

Follow this order:

1. [Core Kavazi Method](CORE_KAVAZI_METHOD.md): the operating rules.
2. [Project Brief](docs/PROJECT_BRIEF.md): what the user asked for.
3. [Master Architecture](docs/MASTER_ARCHITECTURE.md): what the project must do.
4. [Master Methodology](docs/MASTER_METHODOLOGY.md): how to develop and verify it.
5. [Master Technical Core](docs/MASTER_TECHNICAL_CORE.md): how its logic becomes implementation.
6. [Master Implementation Plan](docs/MASTER_IMPLEMENTATION_PLAN.md): the development sequence.
7. Supporting documents needed for the current work.
8. The current phase's plan, methodology, and evidence. This checkout's package is [Phase 03](docs/phases/phase-03/IMPLEMENTATION_PLAN.md).

`.kavazi/state.json` owns phase status and next action; check it against the actual files before continuing.

## Work within the method

Derive a complete project within a stated scope from user input, repository evidence, and relevant sources. Make routine missing design choices yourself. Label assumptions separately from user requirements and observed facts. Honor later user steering and actual host permissions.

In `phase_checkpoint` mode, stop after the phase is fully reviewed and closed. Advance only after actual human approval has been recorded with `approve`. Never self-approve.

Keep parallel work in the current phase and assign explicit file ownership. Future phases remain high-level roadmap entries without packages until their predecessor is complete, reviewed, and reconciled. Preserve user work and dated evidence. Record meaningful choices, actual checks, failures, and limitations in the current phase's evidence.

The reusable skill and its tools live in `skills/kavazi-method/`; the plugin setup entry lives in `skills/kavazi-setup/`. Use [CONTRIBUTING.md](CONTRIBUTING.md) for checkout and release procedures. [Documentation map](docs/README.md) separates current project records from historical sources.

## Verify changes

Run:

```bash
python3 -m unittest discover -s tests -v
python3 skills/kavazi-method/scripts/kavazi.py check --repo .
```

A valid record does not prove product behavior. Closing a phase also requires the Core's acceptance, review, and evidence conditions. Do not edit protected environment metadata or claim a model switch, Git revision, external installation, or runtime result that was not observed.
