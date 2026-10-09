# Master Methodology — ${project}

Explain how to develop and verify the behavior defined in [Master Architecture](${architecture_link}). Start with the [Project Brief](${brief_link}) and follow [Core](${core_link}). Established ${date}; the methods below need project-specific decisions and source verification.

## Sources and project application

Choose approaches suited to the actual project. Verify primary sources, explain the claim they support, and record the adaptation and limits. Make routine missing choices yourself and record consequential alternatives.

| Method | Primary source and supported claim | Application here | Limits and verification |
|---|---|---|---|
| Replace with the chosen approach | Link and verify the relevant source | Explain the actual use | State what still needs checking in this project |

## Execution and verification strategy

Match each important claim to the smallest check that can distinguish success from failure. Source inspection, compilation, tests, runtime observation, measurements, and release checks support different claims.

[Master Technical Core](${technical_core_link}) specifies concrete mechanisms and checks. Define suitable project check IDs and command arrays in `.kavazi/config.json`; reference required IDs in the phase ledger and run the commands separately from Kavazi inspection commands.

## Measurement and decision rules

Before measuring, define the environment, inputs, samples or seeds where relevant, and meaningful numerical thresholds. State success, failure, and reconsideration criteria. Preserve actual failures and unavailable prerequisites in current-phase evidence. A design assumption remains a choice to test.

## Review and reconciliation

Use Core's review cycle: inspect the full required scope, fix findings, justify any refactors, verify, and review the full scope afresh until clean. Every fifth phase adds whole-repository coverage. Update methods when contracts or observations change. Checkpoint approval follows full closure and cannot substitute for review.

[Master Implementation Plan](${master_plan_link}) sequences this approach. Find the current phase in [the ledger](${state_link}) or with `status`; the [initial adoption package](${current_phase_link}) records starting context.
