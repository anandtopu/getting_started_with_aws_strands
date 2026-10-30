/** Stretch: accept a quote only when booked is exactly false and totalCents is a nonnegative integer.
 * Run with npm exec --prefix modules/bonus/B2_typescript -- tsx modules/bonus/B2_typescript/exercises/03_authority.ts
 * Cost: $0; no model calls or AWS resources.
 */
import { pathToFileURL } from "node:url";

export function solve(value: unknown): unknown {
  // YOUR CODE HERE: implement the contract above.
  return null;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(solve({"booked": false, "totalCents": 35600}));
}
