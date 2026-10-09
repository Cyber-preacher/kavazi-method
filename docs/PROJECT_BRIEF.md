# Project Brief — Kavazi Method

User direction captured on 2026-10-09. The quotations preserve the user's wording; this manual transcription normalizes trailing whitespace and surrounding blank lines. CLI intake has a separate byte-preservation contract.

This brief records requirements and their origin. The [Core](../CORE_KAVAZI_METHOD.md) governs how to interpret them; [Master Architecture](MASTER_ARCHITECTURE.md) turns them into project behavior.

## Original user input

```text
this is directory where we are going to create a plug in AI sklii called KAvazi Method

it should work as in plug and develop service tht allows you to put it into any repo and makle your agents follwo it it religiously

go learn what iti is

and then prepare a plan on how to make this useful to other devs
```

```text
we have to now make this repo so that when a person uses us (and how he uses us most efficiently also a question)

we have to make this repo plug and play

Also i hope you understand the process now and what folders and files sgould be created
```

## Technical Core and autonomy request

```text
we should also add a MAster Technical Core

this is the documents where the logic of the project is directly connected to its technical realisation

This doc should be created after architecture and methodologoy

in reality the sequnce is like this

user input -> Master Architecture -> MAster Methodology -> MAster Technical core - > Implmentation Master -> All other docs - > Phases

Also the user input can vary it can be very detailed something like several pages or it can be very brief like (create this game fully"

kavazi method must allow to just promt and forget

The model must be able to answer all quetions itself without aksing the user and it shoudl be able to fill up all the logic the create a rchitecture master and then the rest is done

but at the same time there should be flexibility with keeping the human in the loop like the mode would stop afte every phase or something so yeah

Lets modify the repo based on what I've laid out here
```

## Human and agent readability request

```text
okay once again and make sure the repo is as ready fo AI agents to read it as huns it shoudl be balanced and undertandable and easy to plug in for both

Reread the text make them less sloppy more haracter to them
```

The user then asked: “please continue”.

## Open-source preparation request

```text
ok lets add a proper liscence and prepare the repo for open-source (proper one)

reread all docs delete the usless stuff redo the logic of folders and files if needed
```

The user selected **MIT** and supplied **David Kavazi** as the copyright holder. Apply that choice to this repository and its distributed method materials. Prepare the local source and package for publication; no remote destination or instruction to publish was supplied.

## Protected contribution workflow request

```text
now lets prepare the branch protection so there is dev and we can merge to master only from dev (only I)

Also other can create branches to dev but only i can merge the branches to dev

also make proper ci on dev to master and on branch to dev
```

When asked for the GitHub repository URL, the user replied: “you have to create it yes”. This authorizes creating the public open-source repository and configuring the requested hosting workflow. The connected and CLI-authenticated GitHub account is `Cyber-preacher` (user ID `72062250`); use that verified account as the sole merger. The agent selected `Cyber-preacher/kavazi-method`, matching the project name, and `dev` as the default contribution branch.

## First release request

The user then requested: “then make sure it is realeased and give me a link”. Publish the first `0.1.0` release with a downloadable, verified package and provide its actual public URL. This extends the current hosting phase to include a release tag and asset publication; it does not waive the preceding branch or CI requirements.

## Requirement interpretation

| ID | User requirement | Intended outcome |
|---|---|---|
| R01 | Plug-and-play AI skill/plugin, useful to other developers | A portable package and repeatable repository-local adoption preserving established work |
| R02 | User input → Architecture → Methodology → Technical Core → Implementation Master → supporting docs → phases | Explicit canonical ownership, ordered agent discovery, and matching onboarding files |
| R03 | Technical Core directly connects project logic to technical realization | Traceable requirement/behavior → components, interfaces, data, algorithms, runtime, failures, invariants, and verification |
| R04 | Input ranges from detailed specifications to a brief request | Capture raw supplied input and derive a complete project within a stated scope without requiring a lengthy specification |
| R05 | Prompt and forget; model fills logic and answers design questions itself | Default autonomous decisions and sequential execution with evidence-backed assumptions and no routine design questions |
| R06 | Flexible human involvement, stopping after each phase | Optional `phase_checkpoint` mode requiring actual human approval after full phase closure before advancement |
| R07 | Clear, balanced writing for humans and agents; easy setup and a more deliberate voice | A direct human guide, precise agent instructions, focused templates, and one current reading route |
| R08 | A proper open-source license; MIT selected, David Kavazi named as copyright holder | Standard MIT notice and metadata retained in the source, archive, and standalone skill installation |
| R09 | Reread the documentation, delete useless material, and improve file organization where needed | One active skill entry, a clear source layout, preserved dated history, and useful contribution and release guidance |
| R10 | Create the repository; contributor branches merge to dev, only dev merges to master, and only the owner merges either route | Public GitHub repository, exact protected branch rules, verified owner identity, and required CI for both PR targets |
| R11 | Publish the release and provide its link | Verified public v0.1.0 release from the stable branch with a source-matching downloadable archive |

The prior shorter canonical chain and initial research proposal remain historical provenance. The latest explicit chain and execution modes govern current changes. Existing Kavazi sequential phases, evidence, mandatory phase reviews, and every-fifth-phase whole-repository review continue to apply.

## Agent decisions and boundaries

The agent chose the following implementation: keep the local Python 3.10+ standard-library tool and repository-local skill as the initial portable implementation; store the brief and Technical Core as configured canonical paths; use `autonomous` and `phase_checkpoint` as execution-mode names; preserve user input and separately label derived assumptions. Rationale and observed results belong to current-phase evidence.

Autonomy chooses missing design details and continues authorized work. It cannot manufacture credentials, external observations, human approval, permissions, or unlimited host execution. Preserve later user steering and pauses. Phase 02 completed local open-source preparation. Phase 03 creates the public source repository, branch protections, CI, and the first public release; platform expansion and external pilots remain outside this request.
