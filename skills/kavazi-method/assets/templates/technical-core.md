# Master Technical Core — ${project}

Connect project logic directly to technical realization. [Master Architecture](${architecture_link}) defines required behavior; [Master Methodology](${methodology_link}) defines the approach; this document identifies the concrete mechanisms. Start from [Project Brief](${brief_link}) and follow [Core](${core_link}). Established ${date}; fill this generated document with actual technical decisions.

## Logic-to-mechanism traceability

Map each requirement or rule to its actual implementation. Make routine missing choices yourself and label assumptions. Link relevant source, code, and evidence. Distinguish mechanisms already implemented from target design.

| Requirement or rule | Component and owner | Interface, data, algorithm, and flow | Invariant and failure handling | Check and expected result |
|---|---|---|---|---|
| Replace with an architecture requirement ID | Identify the responsible component | Describe the concrete mechanism | State what must hold and how failure is handled | Define how success differs from failure |

## Components, APIs, and data

Define component boundaries, inputs, outputs, state ownership and lifetime, data representation, persistence, migration, and integration contracts as relevant. Connect each mechanism to the requirement it serves.

## Algorithms, invariants, and failure modes

Describe rule evaluation, transitions, ordering or concurrency, error handling, recovery, and preserved invariants. Explain significant technical choices and alternatives. Select technologies for this project's needs.

## Runtime flows and checks

Trace important paths from input through rule evaluation to consequence and presentation. Identify owners, environment, dependencies, executable or manual checks, expected results, and the claim each check supports. Record actual observations and unavailable prerequisites in current-phase evidence.

## Dependency and version decisions

Record chosen technologies, dependencies, versions, compatibility requirements, sources, alternatives, limitations, and reconsideration triggers. A design choice does not establish that a dependency has executed successfully.

[Master Implementation Plan](${master_plan_link}) sequences this design. Find the current phase in [the ledger](${state_link}) or with `status`; the [initial adoption package](${current_phase_link}) records starting context.
