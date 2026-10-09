# Master Architecture

This document defines what Kavazi must do: its users, behavior, and product contracts. It interprets the [Project Brief](PROJECT_BRIEF.md) under the [Core](../CORE_KAVAZI_METHOD.md). [Master Methodology](MASTER_METHODOLOGY.md) explains how to develop and verify this design; [Master Technical Core](MASTER_TECHNICAL_CORE.md) connects it to implementation.

## Project vision and users

Kavazi lets a developer bring a coding agent into a new or existing repository with a short idea or detailed specification, then turn it into a coherent design and working software through reviewed phases. Start with one repository-local skill that the team can share. The local package works without a service account; support for additional hosts and platforms and public distribution require their own evidence.

## Behavioral contracts

| Brief requirement | Required behavior | Boundaries and acceptance |
|---|---|---|
| R01: plug-and-play adoption | Inspect and preserve established work; create mapped canonical files and one current phase | No competing masters, fabricated history, duplicate instruction blocks, unsafe overwrite, or hidden runtime requirements |
| R02: ordered project reasoning | Capture user input → Architecture → Methodology → Technical Core → Implementation Master → needed supporting docs → current phase | Core governs every stage; earlier shorter navigation is superseded while provenance remains |
| R03: connect logic and mechanisms | Trace accepted requirements and behaviors to concrete technical decisions and checks | Technical Core covers owners, interfaces, data, algorithms, invariants, runtime, failures, dependencies, and verification |
| R04 and R05: autonomous completion from sparse input | Define a complete project within a stated scope and make routine missing design choices | Label assumptions separately from requirements and facts; honor user steering, real permissions, and genuine execution prerequisites |
| R06: optional phase checkpoint | Work autonomously within the phase, fully close it, then stop before successor creation | Advance only after actual human approval; never fabricate or self-approve |
| R07: clear guidance for both audiences | Give humans a short setup path and agents explicit operating instructions; give each document a distinct purpose | Keep one current route, put advanced procedures in references, and preserve old wording as clearly marked history |
| R08: MIT licensing | Identify MIT and David Kavazi in metadata; retain the standard notice in the repository, both skills, and plugin archive | Installing Kavazi preserves the target project's license; publication readiness does not establish publication |
| R09: focused public repository | Keep one distributable skill entry, practical contribution and release guidance, and a documented source layout | Remove redundant wrappers; archive dated sources without changing their observations; keep runtime and template resources self-contained |
| R10: protected contribution workflow | Accept contributor PRs into `dev`; accept only the same repository's `dev` into `master`; only `Cyber-preacher` merges either branch | Server-side owner gate is independent of mandatory PR/CI rules; no direct pushes, force pushes, or branch deletion; fork contributions remain possible |
| R11: first public release | Publish v0.1.0 from accepted stable source with a reproducible downloadable archive and actual release URL | Verify tag target, asset bytes, and public availability; distinguish a prepared artifact from a published release |
| Existing Core: disciplined progression | One created unfinished phase; high-level future roadmap; review, fixes, verification, and fresh review before closure | Required failed/unavailable checks, actionable findings, missing dependencies, or unreconciled documents block closure |

## Input and assumptions

Actual supplied input belongs to the Project Brief. Derived requirements retain provenance; agent assumptions identify rationale, evidence, alternatives, and conditions for reconsideration. A one-sentence brief can lead to a complete design. Missing details chosen by the agent remain assumptions until supported by user direction or observations. Design decisions should be made autonomously using project context and relevant primary sources.

No routine design question is needed in either mode. When credentials, external access, host limits, or indispensable dependencies prevent a concrete action, preserve the limitation and continue independent authorized work. Prompt-and-forget means making routine choices and continuing authorized work within the host's execution limits.

## Execution-mode flows

In `autonomous`, the agent captures input, develops the project documents in order, and implements the current phase. It runs acceptance checks, completes reviews, reconciles the documents, closes the phase, and plans only its immediate successor. Continue until the authorized outcome is delivered or a real execution boundary prevents further work.

In `phase_checkpoint`, the same design and development occur within each phase. After complete closure, stop and present evidence and the next high-level outcome for human review. Actual approval is recorded with a current-phase evidence entry and the `approve` command; only then may the next package be created. Steering or pausing by the user remains authoritative in either mode.

## Completion and wider consequences

Functional readiness, record validity, formal phase completion, and public release are distinct claims. Every phase needs a bug hunt, refactoring pass, and fresh review of the full scope; every fifth also needs the whole-repository gate. Reviews include inherited work and integrations. Documentation cannot replace implementation or execution evidence.

The local validator can reject unsupported records and transitions but cannot prove truthful execution, thoughtful review, or human origin of an approval. Direct file access can bypass agent instructions. Maintainers still need substantive review and appropriate required CI checks. Keep record size proportional to the work while retaining closure conditions.

## Source and distribution layout

The repository root contains the public introduction, license, contribution/security guidance, change history, plugin manifest, and checkout command. `skills/kavazi-method/` owns the reusable method and runtime; `skills/kavazi-setup/` owns the plugin setup route. Both carry their own MIT notice.

`docs/` contains Kavazi's own project design and phase evidence. `docs/history/` holds superseded source material. Tests, the archive builder, and GitHub configuration support development. The plugin archive contains the public guides, manifest, and skills; it excludes local metadata, project-specific design and history, tests, and build tools. No target-project license is replaced by adoption.

The public contribution process starts from a source checkout, reproduces the issue, verifies the affected behavior, and records work in the eligible phase. Release preparation produces a locally tested archive. Hosting settings, a published repository, actual CI results, and any release upload are separate operations that must be observed before being claimed.

## Hosted contribution workflow

The public source repository is `Cyber-preacher/kavazi-method`. `dev` is the contribution branch and default target; `master` is the stable promotion branch. Contributors normally use branches in forks. Trusted collaborators may have branch write access, while protected-branch updates remain restricted to the verified owner. Review requests do not grant merge permission.

Separate the owner-only update restriction from required PRs and checks so the owner still meets the quality gate. A trusted metadata-only workflow validates PR routing; ordinary read-only PR jobs test the proposed merge. Use merge commits for promotion and a temporary sync branch when incorporating master into dev. Do not require the sole owner to approve their own PR.

Files describe desired hosting configuration; only actual GitHub settings and runs establish deployment and enforcement. A repository administrator can change those settings. Required check names bound to GitHub Actions do not pin a particular workflow, so the owner must review workflow changes before merging.

The first release targets version `0.1.0` on accepted master history. Its archive must match the tagged source and retain licenses and usable setup guidance. Verify the published asset and URL before claiming release completion.
