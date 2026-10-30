/** Provider boundary and usage. Run: npx tsx examples/03_provider_and_result.ts --mock. Mock $0; live model token charges. */
import {run} from '../common.js';
console.log(await run(process.argv.includes('--mock')));
