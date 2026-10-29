"""Ask a bounded Lambda cost question; optionally connect pinned AWS MCP servers.

Run: uv run python modules/14_mcp/examples/04_aws_servers.py --mock
Expected: illustrative $1.87 estimate, Lesson complete. Offline cost $0.
Live inference uses configured rates. AWS resources created: none.
"""

import argparse
import json

from common.aws_mcp import aws_server
from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.pricing_agent import lambda_cost_question


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--connect", choices=["documentation", "pricing"])
    args, cfg = lesson_settings(parser)
    config = json.loads((ROOT / "modules/14_mcp/aws_servers.json").read_text())
    print("Reviewed launch definitions:", config)
    if args.connect and not args.mock:
        with aws_server(cfg, args.connect) as client:
            print("Discovered:", [t.tool_name for t in client.list_tools_sync()])
            if args.connect == "pricing":
                complete(lambda_cost_question(cfg, client=client), cfg)
            else:
                print(
                    client.call_tool_sync(
                        "lambda-docs",
                        "read_documentation",
                        {
                            "url": "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
                            "max_length": 5000,
                        },
                    )
                )
                complete()
    else:
        complete(lambda_cost_question(cfg), cfg)


if __name__ == "__main__":
    run_cli(main)
