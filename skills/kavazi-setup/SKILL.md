---
name: kavazi-setup
description: Set up the Kavazi Method plugin when the user requests onboarding in a repository. Preserve established documents and install the bundled workflow and local tools.
license: MIT
---

# Kavazi Setup

Put the method into the selected repository, then continue the authorized project work. This entry belongs to the plugin containing both skills. Standalone installation uses the self-contained [Kavazi Method skill](../kavazi-method/SKILL.md).

## Set up the repository

Read the sibling skill's [adoption procedure](../kavazi-method/references/adoption.md). Inspect applicable instructions, existing project documents, unfinished work, and phase history. Identify the files that already own project decisions.

Resolve `scripts/kavazi.py` from the actual sibling `kavazi-method` directory. Preview `init --repo <project> --project "Name" --prompt "<actual request>" --dry-run`, inspect the proposal, then apply it within existing authorization. Use `--brief-file` for a detailed specification. Map established masters explicitly. When preserving an existing brief, omit both source flags and reconcile any new input deliberately in that brief.

If historical phase records cannot be mapped safely, reconcile the dependency while preserving history. Never overwrite established records to make setup pass.

## Continue through the main skill

Default mode is `autonomous`; use `--mode phase_checkpoint` when the user requests a stop after every fully closed phase. Checkpoint advancement needs actual human approval; never self-approve.

Follow **Brief → Architecture → Methodology → Technical Core → Master Implementation Plan → needed supporting documents → current phase**, governed by Core. Make routine missing design choices yourself. Keep user requirements, agent assumptions, and observed facts distinct. Develop toward the user's complete usable outcome.

Report the installed command, mode, current phase, next action, unfinished templates, and observed validation limits. Generated documents are scaffolding; discovery does not establish accepted design or product behavior. Continue authorized current-phase work under the main skill. Create no later package until its predecessor is fully closed and any required human approval is recorded.
