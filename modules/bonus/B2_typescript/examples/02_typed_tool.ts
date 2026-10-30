/** Validated tool. Run: npx tsx examples/02_typed_tool.ts --mock. Expected totalCents 35600; $0, no AWS. */
import {quoteTool} from '../common.js';
console.log(await quoteTool.invoke({travelers: 2}));
