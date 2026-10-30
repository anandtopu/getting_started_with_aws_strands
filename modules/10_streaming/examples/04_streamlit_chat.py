"""Streamlit chat: Nimbus Tier 3 lesson.

Run: uv run --group apps python modules/10_streaming/examples/04_streamlit_chat.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
from contextlib import aclosing

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.streaming import planner, sync_chunks


async def text_chunks(agent, prompt):
    # A finite fixture must be renewed for each UI turn; retain this session's history.
    from common.testing import ScriptedModel, text_message

    if isinstance(agent.model, ScriptedModel) and agent.model.index == len(agent.model.responses):
        agent.model.responses.append(text_message("Explore Boston on foot; confirm your dates."))
    async with aclosing(agent.stream_async(prompt, limits={"turns": 3})) as events:
        async for event in events:
            if "data" in event:
                yield event["data"]


def render(cfg):
    import streamlit as st

    st.title("Nimbus trip planner")
    if "nimbus_agent" not in st.session_state:
        st.session_state.nimbus_agent = planner(cfg)
        st.session_state.nimbus_chat = []
    for role, message in st.session_state.nimbus_chat:
        with st.chat_message(role):
            st.write(message)
    prompt = st.chat_input("Plan a short trip")
    if prompt:
        st.session_state.nimbus_chat.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            text = st.write_stream(sync_chunks(text_chunks(st.session_state.nimbus_agent, prompt)))
        st.session_state.nimbus_chat.append(("assistant", text))
    if st.button("Clear this session"):
        del st.session_state.nimbus_agent
        st.session_state.nimbus_chat = []
        st.rerun()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true")
    args, cfg = lesson_settings(parser)
    if args.ui:
        render(cfg)
    else:
        import asyncio

        async def replay():
            return [
                t
                async for t in text_chunks(
                    planner(cfg), "Suggest a Boston trip in under 100 words."
                )
            ]

        print(asyncio.run(replay()))
        complete()


if __name__ == "__main__":
    import sys

    if "--ui" in sys.argv:
        main()  # Streamlit owns the runner; SystemExit would abort its session bookkeeping.
    else:
        run_cli(main)
