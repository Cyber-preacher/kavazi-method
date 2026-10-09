# Phase ${number} Methodology

Choose the methods and checks for the [phase plan](IMPLEMENTATION_PLAN.md). Use [Project Brief](${brief_link}), [Master Architecture](${architecture_link}), [Master Methodology](${methodology_link}), and [Master Technical Core](${technical_core_link}) as context. Record actual results in [evidence](EVIDENCE.md).

## Methods and uncertainty

Phase outcome: ${outcome}

Explain which master methods and technical mechanisms apply here. Choose missing routine approaches yourself. Distinguish source-supported decisions, agent assumptions, observations, and unavailable execution prerequisites. This generated document still needs evidence of suitability for the actual project.

## Scenarios and checks

Before execution, define useful success and failure scenarios, required project checks, environment, inputs, and expected observations. Set meaningful numerical thresholds before measuring when applicable. An unavailable prerequisite produces a `not_run` result.

## Review procedure

Inspect the entire delivered phase, inherited dependencies, and affected integrations against the architecture and Technical Core. Track stable finding IDs across rounds. Fix actionable findings, justify refactors or explain why none is warranted, verify the result, and review the full scope afresh. Repeat until no new actionable findings appear, prior findings are resolved, coverage is accounted for, and required checks pass.

Every fifth phase also requires whole-repository coverage: earlier phases, source, assets and content, tests, configuration, tooling, documentation, and integrations. Record procedure, actual reviewer, baseline, coverage, fixes, verification, fresh-review result, and limits in [evidence](EVIDENCE.md). Structural validation cannot establish the quality of that review.

In checkpoint mode, actual human approval follows full closure. Never self-approve or substitute approval for review.
