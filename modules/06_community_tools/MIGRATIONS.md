# Supported replacements for older tool tutorials

Checked October 29, 2026 against installed `strands-agents==1.62.0` and
`strands-agents-tools==0.8.10`. The community package emits several deprecations
through logging, so warning filters alone do not establish compatibility.
The table records the inspected source and the actual course choice.

| Requested name | Status in the pin | Supported course path |
|---|---|---|
| `calculator` | Deprecated community tool | [Decimal conversion](../../common/tools/travel_day.py) implements one bounded operation. The upstream shell recommendation would grant unnecessary capability for this lesson. |
| `current_time` | Deprecated | Application `datetime`/`ZoneInfo` injects an explicit clock in [example 01](examples/01_calculator_time_weather.py). |
| `http_request` | Deprecated community tool | `strands.vended_tools.http_request.make_http_request(client=...)`, using an exact-endpoint client in [example 01](examples/01_calculator_time_weather.py). |
| `shell` | Deprecated community tool; Unix PTY dependency also limits Windows | `strands.vended_tools.shell.make_shell(sandbox=...)` in [example 02](examples/02_files_and_consent.py). |
| `editor` | Deprecated | `strands.vended_tools.file_editor.make_file_editor(sandbox=...)` in [example 02](examples/02_files_and_consent.py). |
| `python_repl` | Deprecated community tool | `strands.vended_tools.python_repl.make_python_repl(sandbox=...)` in [example 03](examples/03_python_with_consent.py). |
| `think` | Deprecated | Model-native reasoning; [Module 02](../02_model_providers/examples/06_reasoning.py) shows capability-checked Nova reasoning. No fabricated universal reasoning tool. |
| `journal` | Deprecated | `strands.vended_tools.notebook.notebook` for session notes in [example 04](examples/04_tool_catalog.py). |
| `use_llm` | Deprecated | Supported community `use_agent`, inheriting the parent model, in [example 04](examples/04_tool_catalog.py). |
| `retrieve`, `memory` | Deprecated Knowledge Base wrappers | Current guidance points to `MemoryManager` with `BedrockKnowledgeBaseStore`. This tier explains the transition; local retrieval and persistent memory are implemented in Tier 2. No Knowledge Base is created here. |
| `file_read`, `file_write` | Supported in this pin | [Example 02](examples/02_files_and_consent.py) directly reads a disposable file and exercises the writer's refusal path. They are not granted to a model-driven unrestricted file agent. |
| `image_reader`, `handoff_to_user` | Supported in this pin | [Example 04](examples/04_tool_catalog.py); image bytes and a scripted human response in offline mode. |
| `use_aws` | Supported; broad capability needs restrictions | [Example 05](examples/05_read_only_aws.py) permits only `ec2.describe_regions`; a requested write is rejected before AWS. Live use requires a scoped read-only role. |

The shared [reviewed workspace](../../common/reviewed_workspace.py) implements the
current `Sandbox` interface, but it is **not general-purpose code isolation**.
It accepts only one exact Python calculation and one fixed status command. File
paths map into a disposable directory. Consent is requested after validation;
declining produces an error without the side effect. A production execution
backend needs its own operating-system boundary and resource controls.

`BYPASS_TOOL_CONSENT` tells some community tools to skip their human prompt. It
stays false. Scripted yes/no callbacks simulate a decision in offline lessons;
they do not authorize arbitrary operations or change the process consent setting.
The notebook tool holds session notes; it is not the durable memory taught later.

The weather exercise uses Open-Meteo's documented `current` parameters for
temperature and precipitation at Lisbon coordinates. Offline output is synthetic.
Live educational use must follow the [Open-Meteo documentation](https://open-meteo.com/en/docs)
and [terms](https://open-meteo.com/en/terms). Business use needs its own service
plan and attribution review. The exchange rate is a stated teaching assumption.

## Source evidence

- [Official vended-tool guide](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/).
- [Community package source](https://github.com/strands-agents/tools/tree/v0.8.10/src/strands_tools): inspect the named modules' deprecation decorators and logger messages.
- [Pinned SDK source](https://github.com/strands-agents/harness-sdk/tree/python/v1.62.0/strands-py): `strands/vended_tools`, `strands/sandbox`, and tool execution interfaces.
- [Course verification notes](../../docs/VERIFICATION_NOTES.md) distinguish source inspection, executed contracts and untested hosted behavior.
