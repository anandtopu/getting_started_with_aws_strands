# Local service verification — 2026-10-29

No AWS resources were deployed, and no hosted model inference was performed.
The [per-command record](verification/local_services_checks.json) retains initial
outcomes, exclusions and successful rechecks. The earlier CI record remains
historical evidence for commit `0832d3e`, not a claim about these new changes.
Counts combine the initial sweep and targeted reruns; a second complete live sweep
was not performed after every prompt change.

## Results

| Check | Result and scope |
| --- | --- |
| Tier 1–4 commands | 94 completed, zero remaining command failures, 20 excluded, combining earlier results with two successful repeats of each of the seven repaired commands. Some commands inspect local contracts without invoking a model; completion is not a semantic quality score. |
| Real local models | Ollama 0.40.13 on an RTX 4070 Ti SUPER with 16 GiB VRAM; `qwen3:4b-instruct`, `qwen3-vl:4b`, and `embeddinggemma`. |
| Vision | Read the synthetic receipt total correctly: USD 160.60. |
| Retrieval and memory | Real embeddings, persistent Chroma indexing, Mem0 scoped storage/deletion, and preference examples completed. The cited-answer command now passes strict source/quote validation; that does not validate the meaning of its answer. |
| Ticket triage | 17/20 exact category-and-urgency matches after prompt clarification, versus 4/20 in the first completed run. This is a development rerun, not an untouched holdout benchmark. |
| Jaeger | Six real Strands spans exported through OTLP/HTTP, stored in Jaeger 2.22.0 and read back through `/api/v3/traces`. No private marker, prompt text or span events survived the projection. Model responses in this collector check were scripted. |
| Container images | All three native Linux/AMD64 images built; Lambda's Runtime Interface Emulator and both HTTP/SSE adapters returned the grounded policy answer with external networking disabled. Fargate rejected missing authentication. Runtime/Fargate ran as UID 10001. |
| Runtime ARM64 | Build attempted and failed with `Exec format error`: this engine has no usable ARM64 emulation. The AMD64 adapter check does not validate its deployment architecture. |
| Onboarding rehearsal | Fresh virtual environment: 12.93 seconds to install, 15.47 through mock, 18.32 through real local inference. Packages were cached, the clone existed, and Ollama/model downloads were already complete. This does not establish new-learner setup time. |

The container engine is Podman 6.0.2, accessible with `docker --context default`.
The user's selected `desktop-linux` connection was unavailable. Its bridge network
also failed with a netavark/nftables error. Builds used the native builder
(`DOCKER_BUILDKIT=0`) and host networking; application containers used
`--network none`, with HTTP clients executed inside each container. No global
container settings were changed. Native Windows Jaeger used an explicit configuration
with loopback-only ports after the container/port conflicts were diagnosed.

## Fixes found by live execution

The moving `qwen3:4b` tag reported thinking-only support from `/api/show`; its
reasoning exhausted the 512-token lesson budget. The course now selects the
explicit [instruction-tuned variant](https://ollama.com/library/qwen3:4b-instruct)
and exposes `OLLAMA_THINK=false`. A thinking-only model cannot honor that setting;
see [Ollama's model-specific thinking controls](https://docs.ollama.com/capabilities/thinking).
The real policy tool loop completed after changing the model.

Short-answer instructions now match the bounded token budget in the affected
introductory, booking, session, streaming and graph lessons. Structured tasks
explicitly request their output tools, retain strict validation, and report missing
structured answers. The classification prompt separates imminent departure from
cancellation windows. Redirected Windows output tolerates model-generated Unicode.
The five affected notebooks mirror the updated lesson sources.

## Original failures and verified repairs

These seven commands originally failed on the tested 4B model. Each now completes
twice with real local inference, exit code zero and its completion marker. The
table preserves the original observations. Validation was not weakened and no
live inference was replaced by a scripted response.

| Command | Observed result |
| --- | --- |
| `modules/07_rag/examples/04_cited_search.py` | Structured answer/citation validation did not complete successfully. |
| `modules/12_interrupts/examples/04_approval_web.py` | The live ASGI demonstration did not satisfy its expected completion/approval assertions. |
| `modules/15_agents_as_tools/examples/01_specialist_tools.py` | Did not obtain all required validated specialist answers. |
| `modules/15_agents_as_tools/examples/03_delegation_cost.py` | Delegated comparison failed validation. |
| `modules/15_agents_as_tools/use_case/nimbus_concierge.py` | Concierge failed validation. |
| `modules/18_a2a/examples/02_remote_agent.py` | Partner response failed the typed quote contract. |
| `modules/18_a2a/examples/03_authenticated_client.py` | Authenticated partner response failed the typed quote contract. |

The repairs address four distinct boundaries:

- Ollama ignores Strands' forced output-tool selection. On that specific final
  retry, the course adapter uses Ollama's native JSON schema mode. Ordinary tools
  still run through the model, and Strands/Pydantic plus exact citation checks
  still reject invalid results. Token limits and usage reporting remain active.
  See [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).
- The approval action now uses the request bound by the application. The model
  no longer transcribes a UUID. Extra tool arguments are rejected; durable
  supervisor authorization, ownership, expiry and atomic application still apply.
- The concierge gets one bounded follow-up to request any omitted specialists.
  Failed or already attempted specialists cannot be retried; all three validated
  results remain mandatory. Follow-up model usage is included in the total.
- The A2A server publishes the validated result of the actual quote tool after
  model completion. It does not ask the model to transcribe authoritative terms.
  Its artifact is buffered until validation, while A2A still streams task events.
  The client joins artifact fragments without injecting newlines and requires a
  completed task before independently validating exact quote terms. Explicit
  offline mode also propagates to the child server.

These are execution and contract fixes, not a model-quality certification. Manual
inspection still found incorrect prose: the concierge called a $528 total over a
$1,000 budget and changed currency symbols; a RAG answer confused the hotel
cancellation boundary and did not answer refund-processing timing. Exact citations
and validated child prices do not guarantee a correct natural-language synthesis.
The original 87 successful commands were not all repeated after these changes.

Cloud branches, live weather and interactive consent/handoff examples are excluded.
Two mixed local/cloud scripts reached their cloud-readiness branches before being
classified as excluded; no AWS service call succeeded. The tool-catalog script
returned zero despite an unavailable interactive console, so it is explicitly
excluded rather than counted as passing.

## Repeat the local command checks

Install the locked optional groups and pull the three model IDs above. In PowerShell,
point `OLLAMA_HOST` at your already running local service and run from the repository root:

```powershell
$env:MODEL_PROVIDER = 'ollama'
$env:MODEL_ID = ''
$env:OLLAMA_MODEL_ID = 'qwen3:4b-instruct'
$env:OLLAMA_THINK = 'false'
$env:OLLAMA_HOST = 'http://127.0.0.1:11434'
$env:PYTHONUTF8 = '1'
$env:AWS_EC2_METADATA_DISABLED = 'true'
$env:OTEL_SDK_DISABLED = 'true'
$env:MEM0_TELEMETRY = 'false'
$env:ANONYMIZED_TELEMETRY = 'False'
uv sync --frozen --all-groups
$record = Get-Content docs/verification/local_services_checks.json -Raw | ConvertFrom-Json
foreach ($check in $record.lessons | Where-Object status -ne 'excluded') {
    & .venv/Scripts/python.exe scripts/offline_run.py $check.path
    Write-Output "$($check.path): exit $LASTEXITCODE"
}
```

`offline_run.py` permits loopback for Ollama and local protocols but blocks external
Python DNS/TCP/UDP. It is a test guard, not operating-system isolation. The supplied
MCP/A2A process managers own their local children. Do not substitute the whole-course
`run_all_examples.py --live` sweep: that also includes AWS branches.

## Regression checks and environment limits

The affected configuration/repository/lesson checks passed 201 tests; a later
isolated run covering model/output, retrieval, memory, UI and graph changes passed
69 tests. All five updated notebooks executed successfully with offline responses.

The full optional Windows suite encountered a native access violation after more
than 70% progress, while importing the Mem0 dependency path. It produced no passing
suite summary, and its process exit code was not retained. The isolated memory
checks subsequently passed. The repair follow-up ran the entire optional suite
three times with process exit codes captured: the unchanged baseline passed 510
tests, the original 45-second traceback diagnostic setup passed 510 tests, and the
final code with a fresh bytecode cache passed **517 tests**. Each skipped only the
explicit live-service test, emitted two upstream AgentCore datetime warnings and
exited zero. None emitted an access violation. The cold-cache run exercised the
Mem0/Qdrant import path as part of the full suite. The native failure is **not
reproduced; its root cause remains unconfirmed**, rather than claimed fixed.

To retain a reliable local failure status on Windows after optional dependencies
have finished installing:

```powershell
& .venv/Scripts/python.exe -X faulthandler -m pytest -q *> .nimbus/windows-pytest.log
$testExit = $LASTEXITCODE
Get-Content .nimbus/windows-pytest.log -Tail 30
exit $testExit
```

Do not install/remove packages while that interpreter is testing. If it fails
again, preserve the exit code and fault trace before trying isolated imports.
The four affected RAG, approval, specialist and A2A notebooks also executed
successfully with scripted models after these fixes.

Both default Python versions subsequently passed 484 tests with 34 optional/live
skips each. The final default-installation result and cleanup are recorded in the main
[verification notes](VERIFICATION_NOTES.md).

AWS deployment/teardown, managed voice and microphone/playback behavior, ARM64
execution, and a genuine new-learner onboarding study remain unverified.
