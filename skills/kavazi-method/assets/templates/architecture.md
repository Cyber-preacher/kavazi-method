# Master Architecture — ${project}

Define what the project should do and the rules that govern it. Start from [Project Brief](${brief_link}); [Core](${core_link}) governs the method. Created ${date}. This generated document needs project-specific design before it can support acceptance.

## Project vision and provenance

Describe the complete, achievable product implied by the user's request: its users, purpose, key workflows, and intended outcome. Make routine missing choices yourself. Separate explicit requirements, repository observations, and agent assumptions; give reasons and reconsideration triggers for consequential assumptions.

## Project logic, behaviors, and contracts

Define product rules, user actions, boundaries, and visible consequences. Give requirements stable IDs and cite their source. Keep implemented behavior distinct from target design.

| Requirement and source | Required behavior | Contract and acceptance condition | Assumption or missing execution prerequisite |
|---|---|---|---|
| Replace with an actual requirement ID and source | State what must happen | State how success differs from failure | Label any inferred choice or prerequisite |

## Whole-system behavior and tradeoffs

Describe important user flows, state meanings, lifecycle, failures, recovery, and external interactions. Explain wider consequences and meaningful tradeoffs. Link consequential decisions to current-phase evidence.

## Scope and execution

Define what the finished project includes and the boundaries of that scope. Describe dependencies that affect delivery. [Master Methodology](${methodology_link}) selects development and verification approaches; [Master Technical Core](${technical_core_link}) connects these rules to mechanisms; [Master Implementation Plan](${master_plan_link}) sequences the work.

Find the current phase in [the ledger](${state_link}) or with `status`. The [initial adoption package](${current_phase_link}) records starting context.
