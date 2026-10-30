import test from 'node:test';
import assert from 'node:assert/strict';
import {quote, run} from '../common.js';
test('exact integer pricing and no purchase authority', () => {
  assert.deepEqual(quote({travelers: 2}), {flight: 'FLT-0001', totalCents: 35600, booked: false});
  for (const travelers of [0, 7, true, 1.5, '2']) assert.throws(() => quote({travelers}));
  assert.throws(() => quote({travelers: 2, approve: true}));
});
test('real SDK loop invokes the quote tool without external calls', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => {throw new Error('External network forbidden in mock test');};
  try { assert.match((await run(true)).answer, /356.00/); }
  finally { globalThis.fetch = original; }
});
