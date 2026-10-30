/** First TypeScript Agent. Run: npx tsx examples/01_first_agent.ts --mock. Expected Welcome to Nimbus. Mock cost $0; no resources. */
import {run} from '../common.js';
console.log(await run(process.argv.includes('--mock'), false));
