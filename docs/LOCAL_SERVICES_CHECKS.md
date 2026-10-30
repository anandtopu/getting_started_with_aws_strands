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
| Tier 1–4 commands | 87 completed, seven failed, 20 excluded. Some commands inspect local contracts without invoking a model; completion is not a semantic quality score. |
| Real local models | Ollama 0.40.13 on an RTX 4070 Ti SUPER with 16 GiB VRAM; `qwen3:4b-instruct`, `qwen3-vl:4b`, and `embeddinggemma`. |
| Vision | Read the synthetic receipt total correctly: USD 160.60. |
| Retrieval and memory | Real embeddings, persistent Chroma indexing, Mem0 scoped storage/deletion, and preference examples completed. Strict cited-answer validation still has a failing case. |
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

## Remaining failures

These commands remain unsuccessful on the tested 4B model with the documented
budgets. Validation was not weakened and a failed response was not replaced by a fixture.

| Command | Observed result |
| --- | --- |
| `modules/07_rag/examples/04_cited_search.py` | Structured answer/citation validation did not complete successfully. |
| `modules/12_interrupts/examples/04_approval_web.py` | The live ASGI demonstration did not satisfy its expected completion/approval assertions. |
| `modules/15_agents_as_tools/examples/01_specialist_tools.py` | Did not obtain all required validated specialist answers. |
| `modules/15_agents_as_tools/examples/03_delegation_cost.py` | Delegated comparison failed validation. |
| `modules/15_agents_as_tools/use_case/nimbus_concierge.py` | Concierge failed validation. |
| `modules/18_a2a/examples/02_remote_agent.py` | Partner response failed the typed quote contract. |
| `modules/18_a2a/examples/03_authenticated_client.py` | Authenticated partner response failed the typed quote contract. |

Other A2A commands, including framework interoperability and the partner-upgrade use
case, completed. This mixed evidence is insufficient to declare the local model
reliable across all lessons. A larger compatible model is a possible follow-up,
not a verified fix.

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
suite summary. The isolated memory checks subsequently passed, so the cause is
unresolved; do not treat the earlier public CI success as verification of this run.
Both default Python versions subsequently passed 477 tests with 34 optional/live
skips each. The final default-installation result and cleanup are recorded in the main
[verification notes](VERIFICATION_NOTES.md).

AWS deployment/teardown, managed voice and microphone/playback behavior, ARM64
execution, and a genuine new-learner onboarding study remain unverified.
