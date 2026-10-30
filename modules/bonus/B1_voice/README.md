# Module B1_voice: Voice sessions and barge-in
> After this module you can keep a bidirectional voice session bounded and stop queued audio on interruption.

**Time:** ~120 min · **Level:** Advanced · **Cost:** mock $0; live provider usage varies.
**AWS required:** Optional; recorded/local alternative available. **AWS resources created:** None.
**Assistant version 11:** optional extension, outside the core path.

## Prerequisites
Complete [Module 19](../../19_observability/README.md) and [Module 13](../../13_guardrails/README.md). Commands run from the repository root. Use `uv sync --all-groups` for the notebook and optional Evals tools.

## Learning objectives
- Start and close a BidiAgent session.
- Distinguish audio events from a speech-recognition benchmark.
- Clear queued audio after a barge-in event.
- Keep spoken booking requests behind human review.

## The big idea
A voice connection resembles a telephone call: both sides can speak before the other has finished. The host must stop queued playback when the traveler interrupts. A transcript is input, not authorization. Stable BidiAgent runs the connection and tool loop; recorded silent PCM events let you test that contract without a microphone or account. Live speech quality is a separate test.

## How it works
```mermaid
flowchart LR
  Input[Traveler request] --> Host[Trusted host boundary]
  Host --> SDK[Strands SDK]
  SDK --> Evidence[Checked result]
  Evidence --> Review[Review and cleanup]
```
Under the hood, the SDK transports model events and executes registered tools. The application validates the result and owns the authority to continue. A fluent answer cannot grant that authority.

The pinned `strands.bidi` API is stable; the older experimental import is not used. Experimental voice providers remain excluded. The default path exercises real BidiAgent lifecycle and tool dispatch with silent recorded PCM. It does not recognize or synthesize speech. Set `MODEL_PROVIDER=bedrock` and an explicit region-supported `BIDI_MODEL_ID`, install the isolated voice project, and omit `--mock` for a finite live text-to-voice session. This lesson receives audio but does not open a microphone or play it through speakers. See the official guide for device I/O; microphone permissions and real barge-in need a live device check. A voice session may generate several billable responses. It closes after the response or a 30-second deadline. No cloud resources are provisioned.

## Key APIs at a glance
| API | What it does | When to use it |
|---|---|---|
| `BidiAgent` | Owns a bidirectional connection and tool loop | Overlapping input and output |
| `BedrockNovaSonicModel` | Connects to the configured Sonic model | Explicit live Bedrock voice |
| `BidiBargeInEvent` | Signals interruption of a response | Discard pending playback |
| `asyncio.timeout` | Bounds the whole session | Avoid an open-ended connection |

## Walkthrough
### 01_voice_session

A bounded BidiAgent connection.

```text
uv run --all-groups python modules/bonus/B1_voice/examples/01_voice_session.py --mock
```

Expected: `stopped: True`, `booked: False`, and `Lesson complete.`

### 02_barge_in

Discard queued audio after barge-in.

```text
uv run --all-groups python modules/bonus/B1_voice/examples/02_barge_in.py --mock
```

Expected: `barge_in: True`, `queued_audio_chunks: 0`, then `Lesson complete.`

### 03_voice_approval

Speech requests review but cannot purchase.

```text
uv run --all-groups python modules/bonus/B1_voice/examples/03_voice_approval.py --mock
```

Expected: a `pending_human_review` request, `booked: False`, and `stopped: True`.

## Real-world use case
Nimbus wants travelers to ask for booking help by voice. The mini-app receives streamed events, discards queued audio after interruption and records only a pending review request. A real deployment would add microphone/speaker I/O and an authenticated approval interface; spoken consent alone never purchases a flight. Run the [mini-app](use_case/voice_booking.py):
```text
uv run --all-groups python modules/bonus/B1_voice/use_case/voice_booking.py --mock
```
Expected: the checked report and `Lesson complete.`. The [notebook](notebook.ipynb) mirrors the scripts with mock execution. Do not describe fixture output as a live quality benchmark.

## Common mistakes
| Error or observation | Fix |
|---|---|
| `Voice needs Bedrock and an explicit BIDI_MODEL_ID; use --mock first.` | Select Bedrock and a supported Sonic model, or use recorded events. |
| `Install the isolated modules/bonus/B1_voice project; see its README.` | Run the isolated project sync below, not a conflicting root extra. |
| `TimeoutError` | The session exceeded its 30-second deadline; inspect the connection and close device streams. |
| `AccessDeniedException` | Check SSO, the selected model and regional streaming permissions before a live call. |

## Exercises
- **Practice:** [01_playback.py](exercises/01_playback.py) — Discard queued audio after an interruption. [Solution](solutions/01_playback.py).
- **Apply:** [02_approval.py](exercises/02_approval.py) — Spoken approval must still require trusted review. [Solution](solutions/02_approval.py).
- **Stretch:** [03_duration.py](exercises/03_duration.py) — Reject sessions outside a one-to-thirty second budget. [Solution](solutions/03_duration.py).
```text
uv run pytest modules/bonus/B1_voice/tests
uv run pytest modules/bonus/B1_voice/tests --exercise-starters
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
- [Official feature reference](https://strandsagents.com/docs/user-guide/sdk/bidi/agent/)
- [SDK releases](https://github.com/strands-agents/harness-sdk/releases)

## Next: Capstones
Apply the boundary in [the capstone index](../../../capstones/README.md).

## Optional live voice installation

The current voice adapter and AgentCore starter toolkit require incompatible AWS CRT versions. Keep voice in its own locked environment; do not force incompatible versions into the root environment. Mock BidiAgent events work with the default root install. For the live adapter, from the repository root:

```text
uv sync --frozen --project modules/bonus/B1_voice
uv run --project modules/bonus/B1_voice python modules/bonus/B1_voice/examples/01_voice_session.py --mock
```

After configuring SSO, a budget, `MODEL_PROVIDER=bedrock` and a supported `BIDI_MODEL_ID`, omit `--mock`. This receives audio events without microphone capture or speaker playback. Audio quality and live barge-in remain device tests.
