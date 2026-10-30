import test from "node:test";
import assert from "node:assert/strict";
const folder = process.env.NIMBUS_TS_STARTERS === "1" ? "exercises" : "solutions";
test("Practice: return 17800 cents per traveler; reject non-integers and quantities outside 1..6.", async () => {
  const {solve} = await import(`../${folder}/01_quote.ts`);
  assert.deepEqual(solve(2), 35600);
  assert.deepEqual(solve(6), 106800);
  assert.deepEqual(solve(0), null);
  assert.deepEqual(solve(1.5), null);
});
test("Apply: accept mock or bedrock, and reject other provider names.", async () => {
  const {solve} = await import(`../${folder}/02_provider.ts`);
  assert.deepEqual(solve("mock"), true);
  assert.deepEqual(solve("bedrock"), true);
  assert.deepEqual(solve("unknown"), false);
});
test("Stretch: accept a quote only when booked is exactly false and totalCents is a nonnegative integer.", async () => {
  const {solve} = await import(`../${folder}/03_authority.ts`);
  assert.deepEqual(solve({"booked": false, "totalCents": 35600}), true);
  assert.deepEqual(solve({"booked": true, "totalCents": 35600}), false);
  assert.deepEqual(solve({"booked": false, "totalCents": -1}), false);
  assert.deepEqual(solve({}), false);
});
