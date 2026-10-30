# Definition of done and verification gaps

This checklist distinguishes delivered course content from live service evidence.
Checked 2026-10-29. See [the verification record](VERIFICATION_NOTES.md) for exact
commands, package versions and results. A mock score is not a model-quality claim.

- [x] Default Python 3.12 and 3.13 installations pass offline pytest: 473 tests
  pass with 34 explicit optional/live skips on each version.
- [x] Ruff lint and formatting pass across all delivered sources and notebooks.
- [ ] GitHub CI passes on Ubuntu/Windows for both supported Python versions:
  workflow delivered; publication and remote results pending. macOS core job is also defined.
- [x] All ten CDK apps synthesize locally without lookups. Synthesis does not deploy.
- [x] Strands deprecation warnings fail pytest. Upstream AgentCore's separate
  Python datetime warning is recorded, not hidden as a Strands success.
- [x] Repository contracts reject wildcard IAM actions and credentials or consent
  bypass in .env.example. Scope-specific resource wildcards have explanatory comments.
- [x] All 26 modules have guides, at least three examples, a use case, three
  exercises/solutions, quizzes, tests and cleared notebooks. TypeScript checks use Node.
- [x] Feature-map paths, local links and public links pass: 1,564 links in the
  final content sweep. The newly created repository URL is verified separately.
- [ ] All Tiers 1-4 run on a live Ollama model: local adapters and offline contracts
  are tested; model downloads and live inference were not performed. Tool and vision
  capability requirements are explicit in the affected lessons.
- [x] Every delivered AWS lab has tagged resource code, costs and teardown instructions.
- [ ] Actual AWS deployment, teardown and empty-leftover verification: intentionally
  unperformed because the user prohibited deploying resources during authoring.
- [ ] Measured onboarding under 10 minutes locally and 20 minutes on AWS: not timed
  with a new learner. Downloads, hardware, SSO provisioning and model access vary.
- [x] Reference solutions are runnable code. Exercise and capstone starters are
  explicitly unfinished learning tasks, with tests and complete solutions.
- [x] All 173 Python scripts, four TypeScript scripts and 26 notebooks execute.
  The optional sweep has zero skips; TypeScript also passes five tests and type-checking.
- [x] Five printable one-page PDFs, 90 glossary terms and a troubleshooting guide
  are delivered. PDFs are rendered and visually inspected.

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
- Docker is installed but its engine was unavailable during authoring. Image
  builds and a running Jaeger collector require a separate local check.

Do not turn these open boxes into passing claims without running the named checks.
