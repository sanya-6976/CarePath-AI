export type TabType = 
  | 'blueprint' 
  | 'folder-structure' 
  | 'langgraph-visualizer' 
  | 'api-contracts' 
  | 'database-schema' 
  | 'security-phi' 
  | 'lifecycle-flow';

export interface AgentSpec {
  id: string;
  name: string;
  role: string;
  color: string;
  description: string;
  input_keys: string[];
  output_keys: string[];
  model_tier?: string;
  fallback_strategy?: string;
  rag_enabled?: boolean;
}

export interface FolderNode {
  name: string;
  path: string;
  type: 'folder' | 'file';
  description?: string;
  layer?: 'api' | 'agents' | 'core' | 'db' | 'schemas' | 'services' | 'tests' | 'config';
  codeSnippet?: string;
  children?: FolderNode[];
}

export interface ApiEndpointSpec {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  summary: string;
  description: string;
  tags: string[];
  headers?: Record<string, string>;
  requestBody?: any;
  responses: Record<number, any>;
  isStream?: boolean;
}

export interface SimulationStep {
  step: number;
  agent_id: string;
  agent_name: string;
  status: 'PENDING' | 'SUCCESS' | 'EMERGENCY_TRIGGERED' | 'FAILED' | 'SKIPPED';
  decision: string;
  confidence: number;
  timestamp_ms: number;
  state_delta: Record<string, any>;
}

export interface SimulationResult {
  session_id: string;
  workflow_status: string;
  total_time_ms: number;
  steps: SimulationStep[];
  summary: {
    triage_urgency: string;
    recommended_specialist?: string;
    recommendation?: string;
    confidence?: number;
    rag_evidence_sources?: number;
  };
}

export interface BlueprintTopic {
  id: string;
  number: number;
  title: string;
  category: 'core' | 'agents' | 'data' | 'security' | 'devops';
  summary?: string;
  content?: string;
  diagramAscii?: string;
  keyDecisions: string[];
}

export * from './types/index';


