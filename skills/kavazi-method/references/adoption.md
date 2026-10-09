# Adoption and installation

Use this reference when setting up Kavazi or fitting it to an established repository. Python 3.10+ is required. The local tools use the standard library and need no service account or network connection.

## Use one shared installation

Install the payload in the target repository so developers and agents share the same version and project records. Create or select that directory first; it must exist before `init`. Preview the changes, then apply them:

```bash
python3 /path/to/kavazi-method/skills/kavazi-method/scripts/kavazi.py init \
  --repo /path/to/project --project "Project name" \
  --prompt "Create the complete requested project" --dry-run
python3 /path/to/kavazi-method/skills/kavazi-method/scripts/kavazi.py init \
  --repo /path/to/project --project "Project name" \
  --prompt "Create the complete requested project"
```

`--prompt` captures a short or multiline request. Use `--brief-file /path/to/spec.md` for a detailed UTF-8 specification. Setup installs `.agents/skills/kavazi-method`, config and state, a managed root `AGENTS.md` block, the Core, the captured Project Brief, missing masters, and only Phase 01's package.

New adoption defaults to `autonomous`: the agent makes routine design choices and develops through reviewed phases toward a usable finished product. Use `--mode phase_checkpoint` when the user wants an approval stop after each fully closed phase. In either mode, preserve actual input, distinguish assumptions from requirements and observations, and honor subsequent user steering. [Core](core-method.md) defines the operating rules.

The dry run writes nothing. An identical repeat is a no-op; a different payload or unsafe document/history conflict requires deliberate reconciliation. There is no force-overwrite option. Each file replacement is atomic, but an unexpected I/O failure can leave a partial multi-file setup. Inspect the result before retrying.

To install the skill without creating project records:

```bash
python3 /path/to/kavazi-method/skills/kavazi-method/scripts/kavazi.py install \
  --repo /path/to/project --dry-run
python3 /path/to/kavazi-method/skills/kavazi-method/scripts/kavazi.py install \
  --repo /path/to/project
```

If the host has not discovered the skill, start a fresh session or explicitly load `.agents/skills/kavazi-method/SKILL.md`. Installation does not establish that a host refreshed its UI. Other hosts can read the file explicitly; automatic integration requires separate validation.

## Fit the existing repository

Before adoption, inspect applicable `AGENTS.md` files and overrides, product documents, implementation, unfinished work, milestones, historical evidence, and available checks. Identify which files already own project decisions. Preserve user content and accepted choices.

Map those documents explicitly:

```bash
python3 /path/to/kavazi-method/skills/kavazi-method/scripts/kavazi.py init \
  --repo /path/to/project --project "Project name" \
  --brief docs/project-input.md \
  --core docs/CORE.md \
  --architecture docs/architecture.md \
  --methodology docs/methods.md \
  --technical-core docs/technical-design.md \
  --master-plan docs/roadmap.md \
  --phases docs/development-phases --dry-run
```

Apply the same mapping without `--dry-run`. Paths must stay inside the target repository and must not traverse symlinks. If established phase history cannot be mapped safely, automatic setup stops before writes. Reconcile that history under the Core, preserve provenance and stable phase numbers, then validate. Existing code alone does not prove completed Kavazi phases.

When preserving an existing mapped brief, omit `--prompt` and `--brief-file`. Supplying new input at the same time is refused before writes so neither source is silently discarded. Add the new request deliberately to the existing brief. Use a source flag when the selected brief is absent and should capture that request.

Omitting `--mode` preserves the mode of an existing adoption. Upgrading or removing the integration must preserve project documents and evidence; this version provides no automatic migration or removal command.

## Turn templates into a project

Generated files begin the work. Preserve the supplied text and derive a complete project within a stated scope. Make routine missing choices yourself and label assumptions with their rationale and evidence.

Follow the sequence: **Brief → Architecture → Methodology → Technical Core → Master Implementation Plan → needed supporting documents → current phase.** Architecture defines project logic and contracts. Methodology explains how to build and verify them. Technical Core connects that logic to concrete technical decisions. The plan sequences the work; the current package carries its scope, methods, and observations.

Choose meaningful project checks in `.kavazi/config.json` and put their IDs in the current phase's `required_checks`. Run the checks under existing permissions and record actual results. The tools never execute configured commands; `init` does not infer test selection or successful execution. Closure requires at least one required check and passing evidence. Record missing prerequisites openly.

Use the installed `status`, `doctor`, and `check` commands to inspect the effective mode, next action, missing files, instruction conflicts, and register drift. Nested instructions and host loading rules may affect arrival. Verify actual arrival and resumption before claiming host integration support.

In checkpoint mode, fully close the phase, capture the human's actual approval in its evidence, and record it with `approve` before `next`. Never self-approve. [Record examples](records.md) describe the fields and transitions.

When requested, commit the payload, instructions, records, and completed project documents through the project's normal review process. The source directory `skills/kavazi-method/` is the self-contained distributable payload. Its MIT notice travels with the installed skill; setup preserves the target project's own license.
