/** Nimbus quote workflow. Run: npm run demo. Expected quote only; mock cost $0; creates no resources. */
import {run} from '../common.js';
try { console.log(await run(process.argv.includes('--mock'))); }
catch (error) { console.error('Check provider settings and scripts/check_env.py:', error instanceof Error ? error.message : 'Invocation failed'); process.exitCode = 1; }
