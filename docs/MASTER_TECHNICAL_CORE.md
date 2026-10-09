# Master Technical Core

This document connects project logic to concrete implementation. It follows [Master Architecture](MASTER_ARCHITECTURE.md) and [Master Methodology](MASTER_METHODOLOGY.md), then informs [Master Implementation Plan](MASTER_IMPLEMENTATION_PLAN.md). The [Core](../CORE_KAVAZI_METHOD.md) governs the sequence.

Architecture defines behavior; methodology defines how to develop and check it. This document identifies the components, records, algorithms, and failure handling that realize the design. Initial delivery observations belong to [Phase 01 evidence](phases/phase-01/EVIDENCE.md); release-preparation observations belong to [Phase 02 evidence](phases/phase-02/EVIDENCE.md); current hosting observations belong to [Phase 03 evidence](phases/phase-03/EVIDENCE.md).

## Logic-to-mechanism map

| Requirement | Implementation owner | Rules and failure handling | Verification |
|---|---|---|---|
| R01: portable repository adoption | `skills/kavazi-method/` self-contained payload; `scripts/onboarding.py`; `.agents/skills/kavazi-method/` installation | Preserve user bytes, preflight conflicts, no force overwrite; identical rerun is a no-op | Temporary target repos, dry-run byte comparison, installed operation independent of source checkout |
| R02: ordered canonical documents | `config.paths` maps `brief`, `core`, `architecture`, `methodology`, `technical_core`, `master_plan`, `phases`; templates and managed `AGENTS.md` | Canonical paths stay inside repo; no symlink traversal or competing masters; existing history requires reconciliation | Mapped-path onboarding, live-link checks, missing/aliased-path failures |
| R03: trace project behavior to implementation | Technical Core requirement matrix and concrete component/data/algorithm/runtime sections | Mechanisms follow accepted logic and actual source evidence; target design is distinguished from implementation | Trace a behavior through its owner, record representation, transition, error, and discriminating check |
| R04: accept brief or detailed input | `init --prompt` or `--brief-file`; configured Project Brief; dynamic fenced capture | Preserve supplied input, including special characters and multiline text; no inferred user decisions | Raw-input round trips, missing/conflicting input handling, source metadata checks |
| R05: autonomous development | Main skill's design derivation and sequential cycle; `config.execution.mode: autonomous`; guarded `close`/`next` | Derived assumptions labeled; reviews/checks still mandatory; external permissions and observed facts remain real | Independent skill scenarios and deterministic transition rejection tests; no claim of unlimited execution |
| R06: checkpoint after closed phase | `config.execution.mode: phase_checkpoint`; `approve` adds closure `human_approval`; `next` requires it | Close first; actual user approval only; never agent self-approval; structurally valid attestation cannot prove its origin | Reject pre-closure approval and unapproved next phase; verify real evidence references and approved transition |
| R07: clear human and agent guidance | README for setup; AGENTS and the skill for arrival; focused masters, references, and templates; CLI command help | One current reading route; old instructions marked as history; examples must work with actual options | Reader review, setup walkthrough, generated-file inspection, local links, and metadata validation |
| R08: MIT notices in every distribution path | Root and per-skill `LICENSE`; plugin `license` and `author`; skill frontmatter; builder and installer preflight | Recognize the declared notice format, require root and skill bytes to agree, and preserve the target project's own license | Standard-text regression, archive/source comparisons, copied-skill checks, missing or conflicting notice refusals, unchanged target-license bytes |
| R09: public source layout and contribution workflow | Root public guides; `docs/README.md`; `docs/history/`; issue/PR templates; pinned CI action revisions | One active skill entry, valid source and archive links, preserved historical statements, no fabricated publication or CI result | Full document review, standalone setup, archive inspection, and configured/local-check comparison |
| R10: owner-controlled contribution routes | `.github/rulesets/`, `validate.yml`, `pr-route.yml`, CODEOWNERS, and hosted settings | Exact dev/master refs; sole owner may update through PRs; independent no-bypass safety/CI requirements; trusted metadata enforces promotion source | Event fixtures, JSON policy tests, live setting read-back, actual PR CI on both routes, invalid-route failure |
| R11: published first release | Version metadata, changelog, deterministic builder, Git tag and GitHub release asset | v0.1.0 must target accepted master; archive bytes must match tagged source and downloaded release asset | Version/target read-back, archive comparison, actual public download and SHA-256 equality |
| Existing Core: evidence-supported closure | `scripts/core.py` state/link/fingerprint/closure validation | Passing required checks, fresh full-scope reviews, carried findings resolved, current baseline, reconciled documents | Failed/missing/stale/checkpoint/fifth-phase regression fixtures |

## Components and interfaces

| Owner | Responsibility |
|---|---|
| `skills/kavazi-method/SKILL.md` and references | Agent design derivation, operating workflow, recovery, and reusable Core |
| `skills/kavazi-method/scripts/kavazi.py` | Argument parsing, local inspection, guarded phase transitions, and approval recording |
| `skills/kavazi-method/scripts/core.py` | Config/state validation, generated register, fingerprint, closure/approval evaluation |
| `skills/kavazi-method/scripts/onboarding.py` | Payload installation, supplied-brief capture, canonical file creation, preserved instructions |
| `skills/kavazi-method/assets/templates/` | Brief, architecture, methodology, Technical Core, master plan, and eligible phase documents |
| `skills/kavazi-setup/` and `plugin.json` | Plugin onboarding route and portable metadata |
| `tests/` and `.github/workflows/validate.yml` | Behavior verification and CI execution |
| `scripts/build_plugin.py` | Reproducible archive from an explicit distribution allowlist with license preflight and atomic replacement |
| `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | Public terms, contribution/release procedures, reporting route, and unreleased changes |
| `docs/README.md` and `docs/history/` | Project-document navigation and superseded sources kept outside the distribution |

The local tool creates initial records and validates structural conditions. The agent synthesizes actual project logic, source-backed methodology, technical design, and implementation; templates alone do not perform that reasoning. No configured command is executed by inspection or transition commands.

## Configuration and phase data

`.kavazi/config.json` defines the local contract:

| Field | Meaning |
|---|---|
| `schema_version` | Record format, currently `1` |
| `method_version` | Method contract, currently `"0.1.0"` |
| `project` | Project display name |
| `paths` | Repository-relative locations for `brief`, `core`, `architecture`, `methodology`, `technical_core`, `master_plan`, and `phases` |
| `execution.mode` | `autonomous` or `phase_checkpoint` |
| `checks` | Check definitions, each with a unique `id` and a nonempty string-array `command` |

Default paths place the Core at root, the brief and masters under `docs/`, and phase packages under `docs/phases/`. Paths must stay inside the repository and cannot traverse symlinks.

`.kavazi/state.json` contains `schema_version: 1` and a `phases` array. Each entry has:

| Field | Meaning |
|---|---|
| `number` | Stable positive phase number, contiguous from 1 |
| `title` | Intended phase outcome |
| `status` | `not_planned`, `planned`, `in_progress`, `blocked`, or `complete` |
| `next_action` | The immediate action to resume |
| `required_checks` | Unique IDs drawn from configured checks |
| `closure` | `null` until a complete acceptance and review record is entered |

Created phases form a consecutive prefix of the roadmap, with at most one unfinished package. Every created predecessor needs supported closure. New adoption starts Phase 01 `in_progress`; existing code does not establish historical completion.

The current phase's `closure` object records its file `baseline`, `acceptance`, `checks`, `reviews`, and `documentation`. [Record examples](../skills/kavazi-method/references/records.md) give the exact fields and update procedure. Closure requires at least one declared required project check.

Reviews preserve their rounds in order. Findings have stable IDs, a status of `open`, `resolved`, or `rejected`, and an evidence reference. The last round of each required review kind must be fresh, cover the full scope, and leave no unresolved carried findings. Fifth phases require both `phase` and `whole_repository` review records.

Each evidence reference resolves to a visible heading in that phase's `EVIDENCE.md`. A heading inside a fence, comment, or raw HTML block cannot support closure. The scanner supports defined plain-Markdown forms; it is not a complete CommonMark renderer. Records are attestations, not proof of execution.

After a checkpoint phase is fully complete, `approve --evidence P01-E005 --summary "Actual user approval" --by "Actual approver"` records `closure.human_approval: {"evidence": "P01-E005", "summary": "Actual user approval", "granted_by": "Actual approver"}`. The command validates structure and references; agents must record actual user authorization, never fabricate human origin. Autonomous mode does not require this per-phase checkpoint.

Only state owns status and next action. The master plan's `<!-- kavazi:register:start -->` / `<!-- kavazi:register:end -->` block is generated. Phase plans reference the ledger. `sync` updates only a valid existing generated block.

## Runtime and failure handling

### Adoption

Parse intake, mode, and path options; inspect source resources and target content; then calculate all proposed writes. Begin writing only after preflight succeeds. A dry run writes nothing, including bytecode caches. Preserve existing masters and surrounding root instructions. Identical reruns are no-ops.

Unsafe paths, conflicting payloads, and unresolved phase history fail before writes. The tool has no force-overwrite, automatic migration, or removal command. Each file replacement is atomic. An unexpected I/O failure can still leave a partially applied multi-file action; inspect and reconcile it before retrying.

### Input and Markdown

Capture raw UTF-8 input inside a fence long enough to contain it safely. Record source, original byte length, and SHA-256. Repeated-input comparison uses visible metadata outside the capture and recognizes equivalent literal entities. Examples cannot masquerade as provenance, and terminal-newline changes remain distinguishable.

Render project names, source metadata, phase titles, outcomes, and register cells as literal display text. Preserve their original values in source, config, and state. Shared Markdown context validation rejects a managed arrival block hidden by an unfinished fence, comment, or raw block. Existing instruction-prefix bytes remain preserved.

### Resources and archives

Reject symlinks, nonregular resources, and unreadable nested payload directories. Do not silently omit a required resource. The archive builder preloads source bytes and requires a `.zip` destination outside the payload and distribution source resources. It preserves prior output permissions and replaces the archive atomically.

Require root `LICENSE`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md`, plus both skill directories. The plugin declares MIT and its author; each skill declares MIT and carries the same notice as root. Runtime preflight checks regular files, the declaration, and five distinguishing notice fragments. It recognizes the supported format; it does not prove complete legal-text equivalence. The repository's license regression verifies the standard MIT text and selected copyright line, while the builder requires per-skill bytes to equal the root notice. Install the main skill's notice inside `.agents/skills/kavazi-method/`; leave the target repository's `LICENSE` unchanged.

### Phase transitions

Before closing a phase, validate acceptance, checks, reviews, documentation, and the current file fingerprint. Before advancing, validate predecessor completion and any required checkpoint approval. Create exactly the next numbered package; do not skip numbers or precreate later packages. The CLI uses templates beside the executing skill for both preview and application, so source checkouts can advance without installing into themselves. The helper's omitted `source_skill` still defaults to the target's installed skill. Validation failures prevent intended writes. Independent authorized work can continue inside the current phase while another task is blocked.

Generated sync commands use the selected tool's path, relative to the target when possible. External tool paths include a reminder to keep that source directory available. Shell quoting preserves argument boundaries, and adaptive code fences preserve the displayed command. Relative paths beginning with a hyphen receive `./` so Python treats them as filenames. A carriage return in the displayed script path is rejected before writes because Markdown text normalization changes its spelling; tested literal line feeds remain supported.

### Baseline comparison

`snapshot` hashes the paths and bytes of regular files in its scope. It excludes Git metadata, dependency, build, and cache directories, phase state, and phase evidence. It normalizes only the master plan's generated register, allowing closure recording without invalidating itself.

The brief, Core, masters, config, tools, project source, assets, and tests remain covered. Reject symlinks in scope. Historical phases retain their historical fingerprints; closing or advancing the current phase requires a matching current fingerprint. Record external environment and dependency observations separately.

## Dependencies and version rationale

Python 3.10+ and standard-library runtime keep local adoption independent of service accounts or network dependencies; actual platform compatibility needs execution evidence. Method `0.1.0` and record schema `1` identify the current contract. Repository payload differences require deliberate reconciliation rather than silent upgrade. Plugin metadata follows the [official portable format](https://developers.openai.com/plugins/build/plugins); repository-local skill discovery follows [official skill documentation](https://learn.chatgpt.com/docs/build-skills). Those sources support packaging choices, not proven UI import or developer outcomes. PyYAML may support development skill validation but is not a runtime dependency.

## Continuous integration and release records

The GitHub workflow declares Linux checks on Python 3.10 and 3.13, runs the suite and record validation, and builds the archive. Third-party actions use commit IDs verified from their upstream tags, with Dependabot configured to propose updates. This is configured validation; actual remote execution remains an observed release prerequisite.

The manifest and runtime identify version 0.1.0. The changelog labels it unreleased until a real publication occurs. The local archive includes all public-guide links and MIT notices; project-specific records, tests, and the builder remain source-checkout resources. `CONTRIBUTING.md` documents version reconciliation, local verification, hosting setup, and release publication as distinct steps.

### Protected branches

The update ruleset covers only `refs/heads/dev` and `refs/heads/master`, allowing the verified account to bypass that update restriction only through a pull request. Separate branch safety rulesets have no bypass actors and require PRs, resolved conversations, current successful `CI / dev` and `PR route / dev` checks on dev, and `CI / master` and `PR route / master` on master from GitHub Actions (observed app ID `15368`), and prohibit deletion and force pushes. Review count is zero to avoid preventing the owner from merging their own work; owner-only merging is enforced by the update rule. Merge commits preserve dev/master ancestry.

The target-specific `CI` aggregate job runs even after a dependency fails and succeeds only when every validation matrix job succeeds. The matrix exercises Python 3.10 and 3.13, records, and archive construction. `PR route` reads GitHub event JSON and trusted repository identity without checking out code; dev accepts contributor branches, master requires same-repository dev. Retargeting reruns both workflows. Check names bind to the Actions app, not to immutable workflow code; the owner must inspect workflow changes and effective hosting settings.

Publication uses an isolated temporary Git checkout because this authoring directory has no Git metadata and its environment-owned metadata paths must remain untouched. Export only source, tests, GitHub configuration, and project records; exclude caches, build output, and environment-owned directories. Inspect the staged tree before upload. The user additionally authorized the first release tag and uploaded archive. Publish these from verified stable source after the branch/CI acceptance conditions are met.
