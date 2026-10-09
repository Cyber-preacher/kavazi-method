# Kavazi Method

**Carry the idea into code. Let evidence decide when the work is done.**

Kavazi gives coding agents a shared way to develop a project inside its repository. Start with one sentence or a detailed brief. The agent turns that input into a design, connects the design to implementation, and works through reviewed phases with a clear record of what happened.

The agent makes routine design decisions and labels its assumptions. You can let it continue autonomously or choose a human checkpoint after each completed phase. The same documents help developers understand, review, and resume the work.

This repository provides a reusable skill, local Python tools, and a portable plugin package. The tools require **Python 3.10+**, use only the standard library, and run without a service account or network connection.

## Get Kavazi

The source repository is [Cyber-preacher/kavazi-method](https://github.com/Cyber-preacher/kavazi-method). For the development checkout:

```bash
git clone --branch dev https://github.com/Cyber-preacher/kavazi-method.git
cd kavazi-method
```

For the packaged **0.1.0** version, download `kavazi-method-0.1.0.zip` from the [release page](https://github.com/Cyber-preacher/kavazi-method/releases/tag/v0.1.0). Extract it and open the directory containing this README. The same setup commands below work from either the source checkout or the extracted package.

## Start in your project

Use a source checkout or an extracted distribution archive. Run these commands from its top-level directory. Create or select the target project directory first, then preview setup:

```bash
python3 skills/kavazi-method/scripts/kavazi.py init \
  --repo /path/to/project --project "Puzzle game" \
  --prompt "Create a complete playable puzzle game" --dry-run
```

Inspect the preview and apply it by repeating the command without `--dry-run`:

```bash
python3 skills/kavazi-method/scripts/kavazi.py init \
  --repo /path/to/project --project "Puzzle game" \
  --prompt "Create a complete playable puzzle game"
```

For a detailed specification, replace `--prompt "..."` with `--brief-file /path/to/spec.md`. Setup captures the supplied text, installs the skill in `.agents/skills/kavazi-method/`, and creates the project records.

Open the target repository and ask your agent:

> Use $kavazi-method. Build the complete project described in the brief. Make the missing design decisions, label your assumptions, and implement, test, and review each phase until the finished product is usable.

If your host does not discover the skill, start a fresh session or tell the agent to read `.agents/skills/kavazi-method/SKILL.md` explicitly. Setup supplies the starting documents; the agent develops their actual content and builds the product.

For an established repository, read [adoption and path mapping](skills/kavazi-method/references/adoption.md) first. Existing project documents can be mapped in place. Setup preserves their content, adds a marked instructions block, and stops on conflicts that need deliberate reconciliation. An identical repeat makes no changes.

To install only the skill, use `install --repo /path/to/project`, optionally with `--dry-run`. This creates no project records.

## Choose your involvement

| Mode | During a phase | After a phase closes |
|---|---|---|
| `autonomous` — default | The agent makes routine choices, implements, checks, and reviews | It continues into the next phase toward the requested outcome |
| `phase_checkpoint` | The same work | It stops until you approve advancement |

Add `--mode phase_checkpoint` to the setup command for checkpoints. Your later instructions can steer or pause either mode. A checkpoint approval must come from a human, be captured in phase evidence, and be recorded with `approve`; an agent must never approve itself.

Autonomy depends on the host's ability to keep the agent running and the tools and permissions it provides. The agent records concrete blockers, such as missing credentials or essential dependencies, and continues independent work where possible.

## Follow an idea through the method

The Core sets the operating rules. Project reasoning follows this sequence:

**User input → Project Brief → Master Architecture → Master Methodology → Master Technical Core → Master Implementation Plan → needed supporting documents → current phase.**

| Document | What it establishes |
|---|---|
| Project Brief | The supplied request, its requirements, and their provenance |
| Master Architecture | What the project must do and how its parts relate |
| Master Methodology | How to develop and verify it |
| Master Technical Core | How its logic becomes components, interfaces, data, algorithms, and checks |
| Master Implementation Plan | The sequence of development |
| Current phase package | The work to do, the method to use, and the results observed |

Every phase has three documents: `IMPLEMENTATION_PLAN.md`, `METHODOLOGY.md`, and `EVIDENCE.md`. Only the current phase gets a detailed package. Future phases remain high-level roadmap entries until their predecessor is complete, reviewed, and reconciled.

Closing a phase requires functional acceptance, passing required checks, a bug hunt, justified refactoring, a fresh full-scope review with no unresolved or new actionable findings, and updated project documents. Repeat fixes and review until that standard is met. Every fifth phase also reviews the whole repository. Keep everyday records proportionate; a small change can use one compact evidence entry.

The [Core reference](skills/kavazi-method/references/core-method.md) gives the complete rules. The [record guide](skills/kavazi-method/references/records.md) explains closure and phase transitions. The validator checks record structure; product checks and substantive review establish whether the work behaves as intended.

## Know where things live

Setup creates this structure in your project:

```text
your-project/
├── AGENTS.md                         where an agent starts
├── CORE_KAVAZI_METHOD.md             the operating rules
├── .agents/skills/kavazi-method/      shared skill and tools
├── .kavazi/
│   ├── config.json                   document paths, mode, and check definitions
│   └── state.json                    phase status and next action
└── docs/
    ├── PROJECT_BRIEF.md
    ├── MASTER_ARCHITECTURE.md
    ├── MASTER_METHODOLOGY.md
    ├── MASTER_TECHNICAL_CORE.md
    ├── MASTER_IMPLEMENTATION_PLAN.md
    └── phases/phase-01/
        ├── IMPLEMENTATION_PLAN.md
        ├── METHODOLOGY.md
        └── EVIDENCE.md
```

New adoption starts with an unfinished Phase 01. Existing code does not establish accepted design or completed Kavazi phases.

Resume or inspect a project from its root:

```bash
python3 .agents/skills/kavazi-method/scripts/kavazi.py status --repo .
python3 .agents/skills/kavazi-method/scripts/kavazi.py doctor --repo .
python3 .agents/skills/kavazi-method/scripts/kavazi.py check --repo .
```

Use `--help` for command options. The tools never execute configured project checks; run those separately and record their actual results. State owns status and next action; `sync` updates the master plan's generated register. See the [record guide](skills/kavazi-method/references/records.md) before using `snapshot`, `close`, `approve`, or `next`.

## Package status and contributions

The package declares version `0.1.0`; see [CHANGELOG](CHANGELOG.md) for release status. `plugin.json` describes the portable package, `skills/kavazi-method/` contains the self-contained implementation, and `skills/kavazi-setup/` provides the onboarding entry.

Local tools and regression behavior have been exercised on Linux. Windows, macOS, automatic discovery in additional hosts, plugin UI import, and external pilots still need validation. Instructions and stored attestations cannot guarantee agent compliance or authenticate a human approval; maintainers need meaningful review and suitable required CI checks.

To improve Kavazi, use a full source checkout and read [CONTRIBUTING](CONTRIBUTING.md). The checkout's `docs/README.md` maps its design records and history. An archive contains the runtime package and public guides; build tools, tests, and this project's development records stay in the source checkout.

Contributions target `dev`. David Kavazi (`@Cyber-preacher`) merges contributions and promotes this repository's `dev` into `master`. Both routes require the regression, record-validation, archive-build, and pull-request routing checks. The source checkout's `docs/BRANCH_WORKFLOW.md` explains the branch rules and records how to verify their live configuration. Installing the skill does not impose these hosting settings on your project.

Report security concerns through the process in [SECURITY](SECURITY.md).

## License

[MIT](LICENSE) · Copyright © 2026 David Kavazi.
