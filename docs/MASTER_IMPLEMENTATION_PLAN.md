# Master Implementation Plan

This document sequences development. It follows [Master Technical Core](MASTER_TECHNICAL_CORE.md) under the [Core](../CORE_KAVAZI_METHOD.md). The [Project Brief](PROJECT_BRIEF.md) records the user direction behind the plan.

Phase 01 delivered the local plug-and-play package and the human/agent editorial pass. Phase 02 prepared the source and archive for open-source use: MIT licensing, a focused layout, contributor guidance, release checks, and a fix for source-checkout phase creation. Phase 03 delivered the public repository, protected branch routes, required CI, and first v0.1.0 release. Additional hosts and external pilots remain future directions requiring execution evidence.

The [initial proposal](history/initial-proposal.md) remains historical research. The user-authorized release preparation replaces the earlier agent-derived Phase 02 host-expansion candidate; stable numbers and accepted Phase 01 history are preserved.

<!-- kavazi:register:start -->
| Phase | Title | Status | Next action |
|---|---|---|---|
| 01 | Plug-and-play local MVP | complete | Derive only the immediately next phase from accepted evidence. |
| 02 | Open-source release preparation | complete | Derive only the immediately next phase from accepted evidence. |
| 03 | Protected branch workflow and first release | complete | Derive only the immediately next phase from accepted evidence. |
<!-- kavazi:register:end -->

## Current package and progression

[Phase 01](phases/phase-01/IMPLEMENTATION_PLAN.md) is retained as completed history. [Phase 02](phases/phase-02/IMPLEMENTATION_PLAN.md) retains completed release-preparation history. [Phase 03](phases/phase-03/IMPLEMENTATION_PLAN.md) is the current package. `.kavazi/state.json` owns status and next action; `sync` regenerates the register above.

Complete accepted implementation, required checks, full-scope reviews, and affected documentation before closing a phase. Create only its immediate successor after closure. Every fifth stable phase adds the whole-repository review gate.

In `autonomous` mode, continue toward the authorized outcome. In `phase_checkpoint`, actual human approval after closure also gates the next package. Both modes honor user steering and real execution limits.
