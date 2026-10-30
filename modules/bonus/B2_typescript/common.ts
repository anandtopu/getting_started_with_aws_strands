/** Nimbus provider boundary. Mock uses real SDK events; live Bedrock uses the normal credential chain. */
import { Agent, BedrockModel, Model, tool, type BaseModelConfig, type ModelStreamEvent, type Message } from '@strands-agents/sdk';
import { z } from 'zod';

export const quoteInput = z.object({travelers: z.number().int().min(1).max(6)}).strict();
export function quote(input: unknown) {
  const {travelers} = quoteInput.parse(input);
  return {flight: 'FLT-0001', totalCents: 17800 * travelers, booked: false};
}
export const quoteTool = tool({name: 'flight_quote', description: 'Read a synthetic Porto quote. Cannot book or pay.', inputSchema: quoteInput, callback: quote});

export class ScriptedModel extends Model {
  private config: BaseModelConfig = {modelId: 'scripted-nimbus'};
  public calls = 0;
  constructor(private readonly withTool = true) { super(); }
  updateConfig(config: BaseModelConfig) { this.config = {...this.config, ...config}; }
  getConfig() { return {...this.config}; }
  async *stream(_messages: Message[]): AsyncIterable<ModelStreamEvent> {
    this.calls++;
    if (this.calls > (this.withTool ? 2 : 1)) throw new Error('ScriptedModel exhausted');
    const call = this.withTool && this.calls === 1;
    yield {type: 'modelMessageStartEvent', role: 'assistant'};
    yield call ? {type: 'modelContentBlockStartEvent', start: {type: 'toolUseStart', name: 'flight_quote', toolUseId: 'quote-1'}} : {type: 'modelContentBlockStartEvent'};
    yield {type: 'modelContentBlockDeltaEvent', delta: call ? {type: 'toolUseInputDelta', input: '{"travelers":2}'} : {type: 'textDelta', text: this.withTool ? 'Two travelers: USD 356.00. Quote only.' : 'Welcome to Nimbus.'}};
    yield {type: 'modelContentBlockStopEvent'};
    yield {type: 'modelMessageStopEvent', stopReason: call ? 'toolUse' : 'endTurn'};
    yield {type: 'modelMetadataEvent', usage: {inputTokens: 100, outputTokens: 20, totalTokens: 120}};
  }
}

export function getModel(mock: boolean, withTool = true): Model {
  if (mock) return new ScriptedModel(withTool);
  if ((process.env.MODEL_PROVIDER ?? 'bedrock') !== 'bedrock' || !process.env.MODEL_ID) {
    throw new Error('Set MODEL_PROVIDER=bedrock and MODEL_ID, or use --mock. See scripts/check_env.py.');
  }
  return new BedrockModel({modelId: process.env.MODEL_ID, region: process.env.AWS_REGION ?? 'us-east-1', temperature: 0, maxTokens: 256});
}

export async function run(mock: boolean, withTool = true) {
  const agent = new Agent({model: getModel(mock, withTool), tools: withTool ? [quoteTool] : [], printer: false, systemPrompt: 'Use the quote tool. Never claim a purchase.'});
  // KEY IDEA: invoke is asynchronous; tools and the model share the actual SDK loop.
  const result = await agent.invoke(withTool ? 'Quote two travelers to Porto.' : 'Say hello to Nimbus.', {limits: {turns: 2}});
  return {answer: result.toString(), metrics: agent.metrics, mock};
}
