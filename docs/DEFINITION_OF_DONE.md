# Definition of done and verification gaps

This checklist distinguishes delivered course content from live service evidence.
Checked 2026-10-29. See [the verification record](VERIFICATION_NOTES.md) and the
[local-service follow-up](LOCAL_SERVICES_CHECKS.md) for exact
commands, package versions and results. A mock score is not a model-quality claim.

- [x] Default offline pytest passes: the validation-repair follow-up passed 484 tests
  with 34 optional/live skips on both Python 3.12 and 3.13.
- [x] Ruff lint and formatting pass across all delivered sources and notebooks.
- [x] [All seven GitHub CI jobs passed](https://github.com/anandtopu/getting_started_with_aws_strands/actions/runs/40981632341): Ubuntu/Windows core checks
  on Python 3.12 and 3.13, macOS core on 3.12, and full optional checks on Ubuntu/Windows.
  This historical run verified `0832d3e`; later local-service fixes are checked separately.
- [x] All ten CDK apps synthesize locally without lookups. Synthesis does not deploy.
- [x] Strands deprecation warnings fail pytest. Upstream AgentCore's separate
  Python datetime warning is recorded, not hidden as a Strands success.
- [x] Repository contracts reject wildcard IAM actions and credentials or consent
  bypass in .env.example. Scope-specific resource wildcards have explanatory comments.
- [x] All 26 modules have guides, at least three examples, a use case, three
  exercises/solutions, quizzes, tests and cleared notebooks. TypeScript checks use Node.
- [x] Feature-map paths, local links and public links pass: 1,567 links in the
  final sweep, including the published repository and successful CI run.
- [ ] All Tiers 1-4 run on a live Ollama model: the local-service sweep and targeted
  reruns completed 94 commands and excluded 20 branches. All seven prior validation
  failures passed two targeted repeats. Natural-language accuracy problems remain,
  and the original successful commands were not all repeated after the latest fixes.
- [x] Every delivered AWS lab has tagged resource code, costs and teardown instructions.
- [ ] Actual AWS deployment, teardown and empty-leftover verification: intentionally
  unperformed because the user prohibited deploying resources during authoring.
- [ ] Measured onboarding under 10 minutes locally and 20 minutes on AWS: not timed
  with a new learner. A prepared-machine rehearsal with cached packages, a fresh
  environment and downloaded local models took 18.32 seconds. AWS timing remains untested.
- [x] Reference solutions are runnable code. Exercise and capstone starters are
  explicitly unfinished learning tasks, with tests and complete solutions.
- [x] All 173 Python scripts, four TypeScript scripts and 26 notebooks execute.
  The optional sweep has zero skips; TypeScript also passes five tests and type-checking.
- [x] Five printable one-page PDFs, 90 glossary terms and a troubleshooting guide
  are delivered. PDFs are rendered and visually inspected.
- [x] Native AMD64 container builds and actual HTTP requests pass for all three
  adapters, including Lambda's emulator, Fargate authentication and Runtime streaming.
  The application containers ran with external networking disabled and scripted models.
- [x] A real local Jaeger collector stored six Strands spans; readback verified
  the numeric-metrics projection excludes private prompt content.

## Scope limits that remain after offline verification

- Live Nova Sonic speech, device playback and microphone barge-in are untested.
  B1 tests recorded silent PCM through the real BidiAgent. The live adapter has its
  own lockfile because its AWS CRT requirement conflicts with the root toolkit.
- The archived agent-builder is replaced by current structured source proposals,
  explicit review and exact-template tool replacement. Arbitrary generated code
  is not automatically executed. AgentConfig remains experimental in B4 only.
- The flagship Runtime handler composes policy RAG, Memory, Gateway and Guardrails;
  local ASGI/MCP/AWS contract tests verify the integration. Live IAM, managed model
  behavior and deployment remain untested. Human approval uses a durable synthetic
  local ledger; production payments and a hosted supervisor UI are outside scope.
- Document fixture extraction is not an OCR accuracy benchmark. Trip prices and
  inventory are synthetic; partner quotes cannot purchase travel.
- Runtime's required ARM64 build failed on the local engine with `Exec format error`.
  Native AMD64 checks do not validate ARM64 execution. The user's bridge network
  also has an existing netavark/nftables failure; engine settings were not changed.
- The optional full Windows regression run hit a native access violation during
  the Mem0 import path. Three subsequent full runs passed, including the original
  diagnostic setup and a final cold-cache run with 517 passing tests. The crash
  has not reproduced; its root cause remains unconfirmed.

Do not turn these open boxes into passing claims without running the named checks.
