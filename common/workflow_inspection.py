"""Inspect the current workflow tool in a disposable directory; never start its workers."""

import os
import sys
from tempfile import TemporaryDirectory


def inspect_workflow():
    # Import-time directory selection must happen before importing this vended module.
    if "strands_tools.workflow" in sys.modules:
        raise RuntimeError("Run this lesson in a fresh process to isolate workflow state")
    previous = os.environ.get("STRANDS_WORKFLOW_DIR")
    with TemporaryDirectory() as directory:
        os.environ["STRANDS_WORKFLOW_DIR"] = directory
        from strands_tools import workflow

        try:
            created = workflow.workflow(
                action="create",
                workflow_id="nimbus-demo",
                tasks=[
                    {
                        "task_id": "draft",
                        "description": "Draft a synthetic itinerary; no side effects",
                    }
                ],
            )
            status = workflow.workflow(action="status", workflow_id="nimbus-demo")
            deleted = workflow.workflow(action="delete", workflow_id="nimbus-demo")
            if any(r["status"] != "success" for r in (created, status, deleted)):
                raise RuntimeError("Workflow metadata lifecycle failed")
            return {
                "created": created["status"],
                "inspected": status["status"],
                "deleted": deleted["status"],
                "execution": "Not started: compare its persistent worker model with Graph",
            }
        finally:
            if workflow._manager is not None:
                workflow._manager.cleanup()
            if previous is None:
                os.environ.pop("STRANDS_WORKFLOW_DIR", None)
            else:
                os.environ["STRANDS_WORKFLOW_DIR"] = previous
