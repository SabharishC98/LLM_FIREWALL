import { Request, Response, NextFunction } from 'express';

export interface LLMFirewallOptions {
  apiKey: string;
  baseUrl?: string;
  threshold?: number;
  mode?: 'check' | 'proxy';
  provider?: 'openai' | 'gemini' | 'anthropic' | 'groq';
  llmApiKey?: string;
  timeout?: number;
  onBlocked?: (report: any) => void;
  onError?: (error: Error) => void;
}

export interface MiddlewareOptions {
  extractPrompt?: (req: Request) => string | undefined;
  failOnMissingPrompt?: boolean;
  failOnError?: boolean;
}

export interface CheckResult {
  request_id: string;
  timestamp: string;
  safe: boolean;
  risk_score: number;
  attack_type: string | null;
  confidence: number;
  flagged_layer: string | null;
  flagged_pattern: string | null;
  threshold_used: number;
  layers: {
    rule_based: {
      triggered: boolean;
      matched_pattern: string | null;
      attack_category: string | null;
      score: number;
      latency_ms: number;
    };
    heuristic: {
      ran: boolean;
      triggered?: boolean;
      reason?: string;
      score?: number;
      signals?: Record<string, number>;
      latency_ms?: number;
    };
    ml_classifier: {
      ran: boolean;
      triggered?: boolean;
      reason?: string;
      attack_class?: string;
      confidence?: number;
      all_scores?: Record<string, number>;
      latency_ms?: number;
    };
  };
  processing_time_ms: number;
  model_version: string;
  metadata: Record<string, any>;
  warnings: string[];
}

export interface BatchCheckResult {
  results: CheckResult[];
  batch_id: string;
}

export class FirewallBlockedError extends Error {
  name: 'FirewallBlockedError';
  report: any;
  constructor(message: string, report: any);
}

export class LLMFirewall {
  options: LLMFirewallOptions;
  openai?: any;
  gemini?: any;
  anthropic?: any;
  groq?: any;

  constructor(options: LLMFirewallOptions);
  check(prompt: string, meta?: Record<string, any>): Promise<CheckResult>;
  checkBatch(prompts: string[]): Promise<BatchCheckResult>;
  middleware(options?: MiddlewareOptions): (req: Request, res: Response, next: NextFunction) => void;
}
