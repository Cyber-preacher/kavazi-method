# Branches, reviews, and CI

Contributions enter `dev`; accepted work reaches `master` through a promotion from the same repository's `dev`. David Kavazi (`@Cyber-preacher`) is the sole merger for both branches. `dev` is the default branch, and `master` is the stable branch.

| Change | Pull request target | Who merges |
|---|---|---|
| Contributor topic branch, including a fork | `dev` | David |
| Same-repository `dev` promotion | `master` | David |
| Synchronization branch containing the latest `master` | `dev` | David |

The public contribution conventions are in [CONTRIBUTING](../CONTRIBUTING.md). This guide explains this repository's hosting configuration; installing the Kavazi skill does not apply these settings to another project.

## Contribute through dev

Fork `Cyber-preacher/kavazi-method` on GitHub. Replace `YOUR-ACCOUNT` and the example topic name below:

```bash
git clone https://github.com/YOUR-ACCOUNT/kavazi-method.git
cd kavazi-method
git remote add upstream https://github.com/Cyber-preacher/kavazi-method.git
git fetch upstream
git switch -c improve-onboarding upstream/dev
```

Make the change, run the checks in CONTRIBUTING, then commit and push the topic branch to your fork. Open a pull request with base repository `Cyber-preacher/kavazi-method` and base branch `dev`. Contributors with write access can create the topic branch from `origin/dev` and push it to this repository instead.

Keep the topic branch current when `dev` advances. For the fork setup above:

```bash
git fetch upstream
git merge upstream/dev
git push origin HEAD
```

Resolve conflicts and rerun affected checks before pushing. Strict required checks evaluate a branch that includes the latest target history. New contributor workflow runs may first need David's approval to run. That approval permits CI execution; the contribution still needs review and David's merge.

## Promote dev to master

David opens the promotion from the upstream repository, with base `master` and head `dev`. A fork branch named `dev` is not an eligible promotion source.

```bash
gh pr create --repo Cyber-preacher/kavazi-method --base master --head dev
```

Review the complete change since the last promotion, including workflow and ruleset changes. Wait for the required checks, resolve review conversations, and merge using **Create a merge commit**. Keep `dev` and `master`; neither is a disposable pull request branch. Automatic merging is disabled so David makes the merge decision.

A promotion adds a merge commit to `master`. Before the next promotion, bring that history into `dev` through a new synchronization branch. Start from the latest `dev`, so the synchronization request satisfies the `dev` routing policy:

```bash
git fetch origin
git switch -c sync-master-after-promotion origin/dev
git merge --no-ff origin/master
git push -u origin sync-master-after-promotion
gh pr create --repo Cyber-preacher/kavazi-method --base dev --head sync-master-after-promotion
```

Use a new branch name for each synchronization. Resolve any conflicts, wait for CI, and let David merge the synchronization request with a merge commit. This retains the `master` ancestry that strict checks require. Do not squash or rebase the synchronization merge, because that discards the ancestry being transferred. If `dev` advances during review, merge the latest `origin/dev` into the synchronization branch and check it again.

## What enforces the route

Three rulesets separate merge authority from required safeguards:

| Configuration | Target | Effect |
|---|---|---|
| [owner-merges.json](../.github/rulesets/owner-merges.json) | `dev`, `master` | Restrict updates; only user ID `72062250` (`Cyber-preacher`) has a pull-request-only exception |
| [dev.json](../.github/rulesets/dev.json) | `dev` | Require a pull request, merge commit, resolved conversations, and current passing `CI` and `PR route`; block deletion and force pushes |
| [master.json](../.github/rulesets/master.json) | `master` | Require the same safeguards for promotions |

The two safeguard rulesets have no bypass actors. The owner exception allows David to complete an update through a pull request while retaining those safeguards.

Formal approving-review count is zero. David cannot approve his own pull requests, so a mandatory self-approval would block owner-authored changes. The restricted update rule controls who merges; David still reviews the change before deciding. [CODEOWNERS](../.github/CODEOWNERS) requests his review and communicates responsibility. It does not grant or restrict write access by itself.

The `CI` aggregate succeeds only after Linux jobs on Python 3.10 and 3.13 pass the regression suite, Kavazi structure check, and plugin archive build. It fails if a required job fails, is cancelled, or is skipped. Both pull request routes receive these checks; pushes to `dev` and `master` also validate the resulting branch revisions.

`PR route` runs in the target workflow context and reads pull request metadata without checking out or running contributor code. It allows contributor branches into `dev`, and only this repository's `dev` into `master`. The ordinary test workflow runs proposed code with read-only permissions and no repository secrets. Every action is pinned to a commit; Dependabot opens action updates against `dev`.

The [Actions event policy](../.github/actions-policy.json) permits `push`, `pull_request`, and `pull_request_target`. New workflow event types need a deliberate policy change and live verification. When maintaining the policy, compare the existing server record with this file and update that record; avoid creating duplicate policies. An allowed event alone does not make a workflow safe. Keep `pull_request_target` limited to trusted metadata handling, with no checkout or execution of contributor code.

Required checks identify GitHub Actions as their source (integration ID `15368`). They still depend on the workflow code and GitHub settings maintained here: David must inspect changes to `.github/`, tests, and the validation tools. An administrator can change the repository's rules. These controls govern the normal contribution path; they are not a guarantee against the account owner deliberately reconfiguring it.

## Apply and verify hosting settings

The ruleset JSON files under `.github/rulesets/` are reviewed configuration. They have no effect until applied through GitHub. Use a source checkout and GitHub CLI authenticated to `github.com` as `Cyber-preacher`; do not apply these owner-specific files to someone else's repository. The commands below use GitHub's `2026-03-10` REST API version for the current ruleset and Actions policy schema.

First verify the account and repository, inspect existing rules, and save the responses before changing anything:

```bash
gh api user --jq '{login, id}'
gh api repos/Cyber-preacher/kavazi-method --jq '{full_name, default_branch, visibility, permissions}'
gh api -H 'X-GitHub-Api-Version: 2026-03-10' repos/Cyber-preacher/kavazi-method/rulesets
```

The account must be `Cyber-preacher` (ID `72062250`) with administrative access to this personal repository. Confirm both branches exist, the default is `dev`, merge commits are enabled, and automatic branch deletion and automatic merging are disabled. The required checks must have produced actual results before treating their configuration as verified.

Compare each local ruleset's name and content with the live rulesets. For an existing matching rule, fetch its complete record, review the difference, and update that rule by ID. Create a rule only when no matching rule exists. Leave unrelated rules in place; do not delete rules or apply duplicates to resolve a conflict. GitHub combines applicable rules, so inspect the effective requirements when diagnosing a blocked merge.

For a new reviewed JSON file:

```bash
gh api -H 'X-GitHub-Api-Version: 2026-03-10' --method POST \
  repos/Cyber-preacher/kavazi-method/rulesets --input PATH
```

For an existing matching rule:

```bash
gh api -H 'X-GitHub-Api-Version: 2026-03-10' --method PUT \
  repos/Cyber-preacher/kavazi-method/rulesets/ID --input PATH
```

Replace `PATH` with the exact file and `ID` with the observed rule ID. Read the server response and fetch the rule again to confirm active enforcement, target refs, bypass identity and mode, and required checks.

Finally inspect the effective rules for both branches:

```bash
gh api -H 'X-GitHub-Api-Version: 2026-03-10' repos/Cyber-preacher/kavazi-method/rules/branches/dev
gh api -H 'X-GitHub-Api-Version: 2026-03-10' repos/Cyber-preacher/kavazi-method/rules/branches/master
```

Maintain the Actions event policy separately. Read the existing policy, compare its reviewed contents with `.github/actions-policy.json`, and update the observed ID when needed:

```bash
gh api -H 'X-GitHub-Api-Version: 2026-03-10' repos/Cyber-preacher/kavazi-method/actions/policies
gh api -H 'X-GitHub-Api-Version: 2026-03-10' repos/Cyber-preacher/kavazi-method/actions/policies/6998
gh api -H 'X-GitHub-Api-Version: 2026-03-10' --method PUT \
  repos/Cyber-preacher/kavazi-method/actions/policies/6998 --input .github/actions-policy.json
```

Read it back after the update. If rebuilding the repository from scratch, create the reviewed policy with `POST` to the collection endpoint and record the returned ID. The explicit active policy supplies the permitted events; do not rely on changing public-repository defaults.

Observe a topic-to-`dev` request and a same-repository `dev`-to-`master` promotion. Verify that a different source into `master` fails `PR route`. Record actual run URLs, branch revisions, rule IDs, and any untested permission scenario in the current phase evidence. Do not infer another account's denied merge from the owner's successful merge alone.

## Hosting observations

The public [Cyber-preacher/kavazi-method](https://github.com/Cyber-preacher/kavazi-method) repository was created on 2026-10-09 (ID `1412079071`). Both `dev` and `master` are published, with `dev` as the default branch. Rules `24799639` (owner updates), `24799646` (dev safeguards), and `24799648` (master safeguards) are active. GitHub accepted the exact owner User ID and PR-only bypass. Actions event policy `6998` is active, workflow tokens default to read, and private vulnerability reporting is enabled.

Initial push validation passed on both branches. Actual PR-route acceptance and the release publication are recorded as they occur in [Phase 03 evidence](phases/phase-03/EVIDENCE.md). This setup does not demonstrate a merge attempt made with another person's credentials.

## GitHub references

[Ruleset creation and bypass modes](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository) explain activation and pull-request-only exceptions. The [rules REST API](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset) defines individual user bypass actors. [Available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) document update restrictions, required checks, and how strict checks depend on target history. The [Actions policy API](https://docs.github.com/en/rest/actions/policies#create-a-repository-actions-policy) defines event restrictions. [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) documents review routing. [Dependabot options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#target-branch) describe the update target.
