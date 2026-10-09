# Master Methodology

This document defines how Kavazi is developed and how its claims are checked. It follows [Master Architecture](MASTER_ARCHITECTURE.md) and informs [Master Technical Core](MASTER_TECHNICAL_CORE.md), under the [Core](../CORE_KAVAZI_METHOD.md).

## Develop from requirements and evidence

Preserve actual user input. Separate user requirements, agent assumptions, and observed facts. Use repository evidence and relevant primary sources to make routine design choices. Record significant alternatives, reasons, limits, and conditions for reconsideration in the current phase's evidence.

Before checking a behavior, state what should happen and how the check could expose a failure. Use temporary repositories to observe adoption without changing real projects. Compare file bytes, directory contents, exit results, and phase records before and after each action. Preserve failed observations and their repairs.

## Verification methods

| Claim | Useful check |
|---|---|
| Setup preserves existing work | Compare original bytes; try explicit mappings and conflicting files |
| Preview is read-only and repeat setup is safe | Compare the entire target tree after dry runs and identical reruns |
| Installed tools are self-contained | Run them from a target repository without relying on the source checkout |
| Intake preserves short and detailed briefs | Round-trip raw prompt and UTF-8 file input, including multiline and special characters |
| Phase transitions respect the method | Try missing, failed, stale, and malformed records; verify checkpoint approval guards |
| Instructions help an agent develop a project | Observe an independent realistic request through design, implementation, and verification |
| Guidance is usable by people and agents | Follow the published setup steps, inspect generated documents, and review both reading routes |
| Licensing survives distribution | Compare root and per-skill notices; inspect the ZIP and installed payload; verify a target project's license remains untouched |
| Repository cleanup preserves useful history | Read all documents, classify their role, repair links, and record moved/removed paths and prior hashes |

Required checks for this checkout are the regression suite and repository structural validation:

```bash
python3 -m unittest discover -s tests -v
python3 skills/kavazi-method/scripts/kavazi.py check --repo .
```

Also verify package contents, skill metadata, and local links when they change. A development environment may supply the YAML dependency for the skill validator; production tools use only Python's standard library. Configured project commands describe required checks. Kavazi's inspection and transition commands do not execute them.

## Sources and their limits

Python's [unittest documentation](https://docs.python.org/3/library/unittest.html) supports the regression harness. OpenAI's [skill documentation](https://learn.chatgpt.com/docs/build-skills) informs repository-local discovery, invocation, and progressive loading; its [plugin format](https://developers.openai.com/plugins/build/plugins) informs package metadata.

The [Open Source Initiative MIT text](https://opensource.org/license/mit) supplies the selected standard license. [GitHub's licensing guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) informs its root placement and discoverability. The [Agent Plugins manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) defines the supported `license` and `author` fields.

These sources explain the chosen mechanisms. They do not establish compatibility with untested platforms, successful plugin UI import, project quality, or improved developer outcomes. Those claims need their own observations.

## Evaluate behavior independently

Give an evaluator a realistic brief and the raw artifacts needed to act on it. Do not supply the intended answer. Observe whether the agent derives coherent requirements, labels assumptions, connects project logic to implementation, and stays within the current phase. In checkpoint mode, verify that it stops after closure and does not self-approve. Keep evaluations isolated and preserve actual outcomes and failures.

Review the full delivered phase: tooling, templates, skills, instructions, tests, docs, CI, and their interactions. Fix actionable findings, verify the fixes, and review the resulting full scope again. Repeat until clean, with no arbitrary round limit. Every fifth phase also requires whole-repository coverage. Human approval controls advancement after closure; it does not replace checks or reviews.

## Keep claims tied to observations

Source inspection, valid records, tests, runtime observations, measurements, and human attestations support different claims. A passing structural check does not establish working software. Later substantive edits invalidate affected acceptance and reviews.

Recover through the Core's reading order and the actual checkout. Record platform, host, and execution limits explicitly; local Linux checks do not establish Windows, macOS, external-host, or public-release support.

For release preparation, compare every distributed resource with source, rebuild twice to check reproducibility, and use the extracted bundle to follow the README. Verify license presence before and after copying the standalone skill, and exercise missing or conflicting notice failures before any writes. Inspect configured CI separately from actually executed local checks; configured jobs are not remote results.

## Hosted branches and CI

Inspect the authenticated account, destination, existing refs, and settings before mutation. Validate concrete ruleset payloads against the current [GitHub rules API](https://docs.github.com/en/rest/repos/rules). Keep the owner update exception separate from the no-bypass PR and CI requirements. Verify the resulting settings through read-back, rather than treating checked-in JSON as enforcement.

Test route decisions with actual-shaped event fixtures: fork feature to dev and same-repository dev to master pass; fork dev or another branch to master fails; missing identity metadata fails closed. Test the actual embedded workflow program. Run the regression/structure/build checks locally and observe real GitHub runs on both PR routes after publication. Inspect failed checks and mergeability for an invalid route. Do not claim a second user's merge rejection without executing it as that user.

Use [GitHub's required-check guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks) for check identity and skipped-job behavior. The [target-event security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) governs the metadata-only route job: no checkout, PR execution, secrets, caches, or write token. Keep runtime CI on `pull_request` with read-only permissions.

For the first release, compare manifest/runtime version, release notes, tag target, and archive name. Build from the accepted release checkout, verify member bytes and reproducibility, publish the tag and asset under the user's explicit direction, then read back release metadata and download the public asset to compare its hash. A draft, upload request, or local ZIP alone does not establish publication.
