# Contributing to Kavazi Method

Help make the method easier to follow, the tools safer to adopt, and the evidence more useful. A good contribution explains the problem, changes the smallest coherent part, and shows what the result establishes.

## Get a working checkout

Use a full source checkout with Python 3.10 or newer. The runtime tools and regression suite use the standard library; no package installation or external service is needed.

Base your work on `dev`, the contribution branch. Create a topic branch in your fork, or in this repository if you have write access, and open a pull request into `dev`. David Kavazi (`@Cyber-preacher`) reviews and merges contributions. `master` receives release promotions from this repository's `dev` branch only, also merged by David.

The source checkout's `docs/BRANCH_WORKFLOW.md` gives clone, pull request, promotion, and branch synchronization commands, plus the hosting configuration. That project-specific guide is outside the portable plugin archive.

From the repository root, run:

```bash
python3 -m unittest discover -s tests -v
python3 skills/kavazi-method/scripts/kavazi.py check --repo .
```

These are the required checks. A skipped test is a reported limitation, not a passing observation. If a check fails, retain its output and distinguish the existing failure from effects of your change.

## Find the right file

| Location in the source checkout | Purpose |
|---|---|
| `README.md` | First use and a concise explanation of the method |
| `skills/kavazi-method/SKILL.md` | The reusable agent entry point |
| `skills/kavazi-method/references/` | Adoption, operating rules, and record procedures |
| `skills/kavazi-method/scripts/` | The self-contained CLI, onboarding, and validation |
| `skills/kavazi-method/assets/templates/` | Documents generated in a target project |
| `skills/kavazi-setup/` and `plugin.json` | Plugin onboarding and package metadata |
| `tests/` and `scripts/build_plugin.py` | Regression checks and archive construction |
| `AGENTS.md`, `CORE_KAVAZI_METHOD.md`, `.kavazi/`, and `docs/` | This project's own development process and evidence |

Start with `AGENTS.md` and follow its reading order before changing the project. `docs/README.md` is the documentation map. The reusable [Core reference](skills/kavazi-method/references/core-method.md) belongs to adopted projects; the root Core applies the same method to this repository. Keep their shared rules consistent while preserving their different navigation.

## Make a reviewable change

For a bug, provide the smallest reproduction you can, expected and actual behavior, the Python version and platform, and the relevant command output. Remove secrets and private project content. For a feature, explain the user problem and an observable outcome before proposing new machinery. Follow [SECURITY](SECURITY.md) for vulnerabilities.

Work within the current phase shown by `.kavazi/state.json`; use its plan, methodology, and evidence. Keep future phases high-level until their predecessor closes. When a change affects completed acceptance or review, explicitly reopen or renew that work under the Core. Preserve dated evidence and append corrections. A contribution can improve part of the current phase without claiming to close it.

Keep human guidance and agent instructions readable. State the action, its purpose, and how to judge the result. Put detailed procedures in the appropriate reference instead of repeating them across entry points. Add a document when it has a distinct purpose.

For behavioral changes, add a regression that demonstrates the failure or protects an important boundary. For prose-only changes, inspect the reading route, examples, links, and generated output as appropriate. Preserve existing user files during adoption; use temporary target directories for experiments. Run the required checks above after your changes and report what actually ran.

Keep runtime dependencies in the Python standard library. Propose a new dependency only with a concrete need, a license check, and an explanation of its installation and maintenance costs. Preserve the MIT notices in distributed and installed payloads. Contributions are made under the repository's [MIT license](LICENSE).

In your pull request, describe the problem and resulting behavior, relevant checks and their outcomes, and any remaining limits. Link the current phase evidence where useful. Do not claim a host, platform, or runtime result that you did not observe.

Pull requests into `dev` and promotions into `master` run the regression suite, structural validation, and archive build on Python 3.10 and 3.13. The required `CI` result succeeds only when every validation job succeeds. A separate required `PR route` check verifies the target and source branches from pull request metadata. Keep your branch current with its target and resolve review conversations before merging. David remains the sole merger; a green check or a CODEOWNERS entry does not grant merge permission.

Workflow changes need careful review: a pull request can change the code that ordinary CI executes. Fork checks receive read-only permissions and no repository secrets. GitHub may hold a new contributor's workflow runs for maintainer approval; approval to run checks is separate from accepting the contribution.

## Prepare a release

Release preparation needs the full source checkout. First reconcile the intended version, [CHANGELOG](CHANGELOG.md), manifest, and versioned method records with any required migration notes. Then run the required checks and build the archive:

```bash
python3 scripts/build_plugin.py --output dist/kavazi-method-0.1.0.zip
```

Use the intended version in the output name. Inspect the archive, extract it into a temporary directory, and follow the [README setup](README.md#start-in-your-project) against a fresh temporary target. Confirm that both skills, their resources and licenses, the manifest, and the public guides are present; check links inside the extracted package. Preserve actual build, setup, and review evidence before closing the phase.

Promote the accepted `dev` revision to `master` through a pull request, using a merge commit. Then synchronize `master` back into `dev` through a new topic branch and another pull request; the source checkout's branch workflow explains why strict status checks need this step. Keep both long-lived branches.

Before publishing a release, verify the active hosting rules and actual CI results, and provide a private vulnerability-reporting route. The configuration files alone do not establish those observations. Tagging, uploading an archive, or publishing a release requires explicit authorization. Record the actual release version and date in the changelog when publication occurs.
