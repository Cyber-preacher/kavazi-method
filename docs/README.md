# Documentation map

These files describe the development of Kavazi itself. To use the method in another project, start with the root [README](../README.md) and the [adoption guide](../skills/kavazi-method/references/adoption.md).

## Current project records

The [Core](../CORE_KAVAZI_METHOD.md) sets the operating rules. Read the project records in order:

| Document | Purpose |
|---|---|
| [Project Brief](PROJECT_BRIEF.md) | User requests, requirement sources, and explicit choices |
| [Master Architecture](MASTER_ARCHITECTURE.md) | Product behavior and contracts |
| [Master Methodology](MASTER_METHODOLOGY.md) | Development and verification approaches |
| [Master Technical Core](MASTER_TECHNICAL_CORE.md) | Requirements connected to implementation and data |
| [Master Implementation Plan](MASTER_IMPLEMENTATION_PLAN.md) | Development sequence and generated phase register |

Each created phase has a plan, methodology, and evidence. `.kavazi/state.json` owns status and next action. Use `python3 kavazi.py status --repo .` from the source checkout to find the current package. Completed packages remain as evidence; future packages are created only when eligible.

## Reusable method

The self-contained [main skill](../skills/kavazi-method/SKILL.md) owns the reusable instructions, references, tools, templates, and its MIT notice. The [setup skill](../skills/kavazi-setup/SKILL.md) routes plugin onboarding to it. Project-specific records here are not copied into another developer's repository.

## Historical sources

- [Initial research proposal](history/initial-proposal.md): the original investigation and candidate roadmap.
- [Historical skill wording](history/original-skill.md): the earlier instructions retained for provenance.

These archives and dated phase evidence explain how the method developed. Their old paths, counts, and limitations describe their recorded baselines. Temporary artifact paths may no longer exist; current tests and procedures provide the reproducible checks. History is excluded from the plugin archive and does not override current instructions.

Current hosting work: [Phase 03](phases/phase-03/IMPLEMENTATION_PLAN.md).
