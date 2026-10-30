"""Local streaming trip UI. Run: uv run --group apps streamlit run this file.

Mock-only UI costs $0 and creates no AWS resources; use the CLI for deliberate live runs."""

import asyncio

import streamlit as st

from common.capstone_trip import plan_events
from common.config import load_settings
from common.trip_planning import TripRequest

st.title("Nimbus Trip Planner Crew")
st.caption("Synthetic quotes. No booking or payment will be made.")
budget = st.number_input("Budget in USD", min_value=1, max_value=100000, value=1000)
if st.button("Compare a Porto trip"):
    st.session_state.pop("trip", None)
    progress = st.status("Checking flight, hotel and weather evidence", expanded=True)

    async def run():
        async for event in plan_events(
            load_settings(provider="mock"), TripRequest(budget_cents=int(budget * 100))
        ):
            if "progress" in event:
                progress.write(f"{event['node']}: {event['progress']}")
            if "result" in event:
                st.session_state.trip = event

    try:
        asyncio.run(run())
        progress.update(label="Comparison ready", state="complete")
    except Exception:
        progress.update(label="Comparison failed; no booking made", state="error")
if "trip" in st.session_state:
    result = st.session_state.trip
    if not result["result"]["budget"]["within_budget"]:
        st.warning("This quote exceeds your budget.")
    st.json(result)
