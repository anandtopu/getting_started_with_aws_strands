# Module B3_self_extending: Reviewing and replacing generated tools
> After this module you can generate a tool proposal, review its exact bytes and explicitly replace an approved tool.

**Time:** ~120 min · **Level:** Advanced · **Cost:** mock $0; live provider usage varies.
**AWS required:** Optional; recorded/local alternative available. **AWS resources created:** None.
**Assistant version 11:** optional extension, outside the core path.

## Prerequisites
Complete [Module 19](../../19_observability/README.md) and [Module 13](../../13_guardrails/README.md). Commands run from the repository root. Use `uv sync --all-groups` for the notebook and optional Evals tools.

## Learning objectives
- Generate a structured ToolProposal using Agent.
- Bind approval to a SHA-256 digest.
- Reject changed or unknown source even when its digest matches.
- Replace a registered tool and verify its next actual SDK result.

## The big idea
Treat generated code like a contractor’s proposed change. Read the proposal, compare it with a reviewed design, run a contract check, and bind approval to the exact bytes. The agent-builder repository is archived; this lesson uses the current Agent structured-output API to propose source. Only two exact reviewed templates may execute. This is deliberately restrictive and is not a general Python sandbox. A changed file loses its approval.

## How it works
```mermaid
flowchart LR
  Input[Traveler request] --> Host[Trusted host boundary]
  Host --> SDK[Strands SDK]
  SDK --> Evidence[Checked result]
  Evidence --> Review[Review and cleanup]
```
Under the hood, the SDK transports model events and executes registered tools. The application validates the result and owns the authority to continue. A fluent answer cannot grant that authority.

No current standalone tool-builder API was found in the pinned SDK. The verified replacement is `Agent(..., structured_output_model=ToolProposal)`. A generated proposal cannot change its own allow-list. The host recognizes exact source templates and binds approval to SHA-256. Only after review does `tool_registry.process_tools` replace the tool. The audit records each digest and price. There is no automatic file watcher or unrestricted execution. The finite demo acts as the reviewer for two committed templates; arbitrary live proposals are rejected. Real organizations also need isolated testing, code review, provenance and a rollback process.

## Key APIs at a glance
| API | What it does | When to use it |
|---|---|---|
| `Agent + structured_output_model` | Produces a typed source proposal | Keep generated source as data |
| `review(source, digest)` | Checks exact template and approved bytes | Before compiling any generated tool |
| `tool_registry.process_tools` | Registers the reviewed replacement | Explicit reload after tests |
| `SHA-256` | Identifies the reviewed source bytes | Detect edits after approval |

## Walkthrough
### 01_builder

Generate a typed source proposal.

```text
uv run --all-groups python modules/bonus/B3_self_extending/examples/01_builder.py --mock
```

Expected: the reviewed `baggage_fee` source proposal and `Lesson complete.`

### 02_review_generated_tool

Bind approval to reviewed bytes.

```text
uv run --all-groups python modules/bonus/B3_self_extending/examples/02_review_generated_tool.py --mock
```

Expected: `two_bags_cents: 5000` and `Lesson complete.`

### 03_trusted_reload

Explicitly replace a reviewed tool.

```text
uv run --all-groups python modules/bonus/B3_self_extending/examples/03_trusted_reload.py --mock
```

Expected: reviewed versions of 5000 and 6000 cents, with 6000 in the updated tool result.

## Real-world use case
Nimbus proposes a baggage-fee tool and reviews it before registration. The reference app runs a USD 25-per-bag version, replaces it with the reviewed USD 30 version, then calls the replacement through the actual Agent loop. The audit records both source hashes and amounts. A company would put human review and version-controlled tests before this same boundary. Run the [mini-app](use_case/reviewed_tool_builder.py):
```text
uv run --all-groups python modules/bonus/B3_self_extending/use_case/reviewed_tool_builder.py --mock
```
Expected: the checked report and `Lesson complete.`. The [notebook](notebook.ipynb) mirrors the scripts with mock execution. Do not describe fixture output as a live quality benchmark.

## Common mistakes
| Error or observation | Fix |
|---|---|
| `Source is unreviewed or changed after approval` | Review the source and compare the exact approved digest; do not weaken the check. |
| `Only the two reviewed fee templates are allowed` | Use 2500 or 3000 cents in this lesson; a new template needs its own review and tests. |
| `Choose 0 to 4 bags` | Pass an integer in the reviewed tool range. |
| `ScriptedModel exhausted` | Create a fresh fixture for the next invocation, as the reload example does. |

## Exercises
- **Practice:** [01_digest.py](exercises/01_digest.py) — Approve only matching nonempty reviewed digests. [Solution](solutions/01_digest.py).
- **Apply:** [02_inventory.py](exercises/02_inventory.py) — Keep generation within the reviewed quote inventory. [Solution](solutions/02_inventory.py).
- **Stretch:** [03_reload.py](exercises/03_reload.py) — Reload only after review and a passing contract. [Solution](solutions/03_reload.py).
```text
uv run pytest modules/bonus/B3_self_extending/tests
uv run pytest modules/bonus/B3_self_extending/tests --exercise-starters
```
The second command deliberately checks your edited starter; its baseline is incomplete.

## Quiz
Answer the [six questions](quiz.md) before opening the answers.

## Key takeaways
- Use the verified import path for the pinned version.
- Keep model output separate from authority.
- Validate behavior, not just successful imports.
- Treat mocks as contract evidence.
- Close resources and preserve useful failure signals.

## Clean up
These examples create no AWS resources. They close local sessions and write only under `.nimbus/`. Remove the generated lab output when no longer needed. Stop notebook kernels after use.

## Go deeper
- [Official feature reference](https://github.com/strands-agents/agent-builder)
- [SDK releases](https://github.com/strands-agents/harness-sdk/releases)

## Next: Capstones
Apply the boundary in [the capstone index](../../../capstones/README.md).
