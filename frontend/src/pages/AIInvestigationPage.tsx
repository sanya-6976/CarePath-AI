import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { analysisService } from '../services/analysisService';
import { 
  Sparkles, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Loader2, 
  ArrowRight,
  Database,
  Brain,
  Award
} from 'lucide-react';
import type { AgentName, AgentState } from '../types';

export default function AIInvestigationPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const analysisId = searchParams.get('patient_id') || searchParams.get('id');
  const isDemo = searchParams.get('demo') === 'true';

  const [agentStates, setAgentStates] = useState<Record<AgentName, AgentState> | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<AgentName | null>(null);
  const [logs, setLogs] = useState<{time: string, agent: string, status: string}[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dots, setDots] = useState('');

  // Sequence of agent execution
  const pipeline: AgentName[] = [
    'Supervisor',
    'Intake',
    'Vision',
    'Docs',
    'Timeline',
    'Evidence',
    'Clinical Reasoning',
    'Safety',
    'Referral',
    'Care Plan',
    'Follow-up'
  ];

  // Logic groups for flowchart visualization
  const intakeGroup: AgentName[] = ['Supervisor', 'Intake', 'Vision', 'Docs'];
  const reasoningGroup: AgentName[] = ['Timeline', 'Evidence', 'Clinical Reasoning'];
  const advisoryGroup: AgentName[] = ['Safety', 'Referral', 'Care Plan', 'Follow-up'];

  // Dot typing loader effect
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 600);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const initialStates: Record<AgentName, AgentState> = pipeline.reduce((acc, name) => {
      acc[name] = { status: 'idle' };
      return acc;
    }, {} as Record<AgentName, AgentState>);
    
    setAgentStates(initialStates);

    if (isDemo || !analysisId) {
      // Keep a fast fallback for demo mode
      let step = 0;
      const pipelineTimer = setInterval(() => {
        step++;
        setAgentStates((prev) => {
          if (!prev) return null;
          const next = { ...prev };
          const activeAgent = pipeline[step];
          
          if (step > 0 && pipeline[step - 1]) {
            next[pipeline[step - 1]] = { status: 'completed', message: 'Task finalized.' };
          }
          if (activeAgent) {
            next[activeAgent] = { status: 'running', message: `Correlating context...` };
          }
          return next;
        });

        if (step >= pipeline.length) {
          clearInterval(pipelineTimer);
          setTimeout(() => { navigate('/analysis'); }, 700);
        }
      }, 750);
      return () => clearInterval(pipelineTimer);
    }

    // Real SSE streaming execution
    let isMounted = true;
    
    const startStream = async () => {
      try {
        const token = localStorage.getItem('carepath_token');
        const BASE_URL = import.meta.env.VITE_API_URL || 'https://carepath-ai-production-508e.up.railway.app';
        
        const storedDocsRaw = localStorage.getItem('carepath_uploaded_docs');
        const storedDocs = storedDocsRaw ? JSON.parse(storedDocsRaw) : [];
        const imageFiles = storedDocs.filter((d: any) => d.type?.startsWith('image/')).map((d: any) => d.name);
        const pdfFiles = storedDocs.filter((d: any) => d.type === 'application/pdf').map((d: any) => d.name);
        
        const response = await fetch(`${BASE_URL}/api/v1/agents/orchestrate/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify({
            session_id: `sess_${Date.now()}`,
            patient_id: analysisId,
            raw_prompt: "Process uploaded clinical documents and patient context",
            uploaded_image_urls: imageFiles,
            uploaded_doc_urls: pdfFiles
          })
        });

        if (!response.ok || !response.body) {
          throw new Error('Failed to connect to orchestration stream.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n\n');
          buffer = parts.pop() || '';

          for (const part of parts) {
            if (part.startsWith('data: ')) {
              try {
                const data = JSON.parse(part.slice(6));
                
                if (data.status === 'started' || data.status === 'completed') {
                  if (!isMounted) return;
                  
                  const nameMap: Record<string, AgentName> = {
                    'supervisor': 'Supervisor',
                    'intake': 'Intake',
                    'vision': 'Vision',
                    'docs': 'Docs',
                    'timeline': 'Timeline',
                    'evidence': 'Evidence',
                    'clinical_reasoning': 'Clinical Reasoning',
                    'safety': 'Safety',
                    'referral': 'Referral',
                    'care_plan': 'Care Plan',
                    'follow_up': 'Follow-up'
                  };
                  
                  const mappedName = nameMap[data.agent];
                  if (mappedName) {
                    setAgentStates(prev => {
                      if (!prev) return null;
                      const next = { ...prev };
                      
                      const currentIndex = pipeline.indexOf(mappedName);
                      if (currentIndex > 0) {
                        for(let i=0; i<currentIndex; i++) {
                           next[pipeline[i]] = { status: 'completed', message: 'Task finalized.' };
                        }
                      }
                      
                      const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
                      let nextStatus = data.status === 'completed' ? 'completed' : 'running';
                      if (data.state_status === 'SKIPPED') nextStatus = 'skipped';
                      if (data.state_status === 'FAILED') nextStatus = 'failed';

                      setLogs(prev => [...prev, { 
                        time: now, 
                        agent: mappedName, 
                        status: nextStatus 
                      }]);

                      next[mappedName] = { 
                        status: nextStatus, 
                        message: nextStatus === 'completed' ? 'Task finalized.' : (nextStatus === 'skipped' ? 'Skipped.' : 'Processing data...'),
                        reason_for_execution: data.reason_for_execution,
                        user_action_required: data.user_action_required
                      };
                      
                      if (currentIndex >= 0 && currentIndex < pipeline.length - 1) {
                         const nextAgentName = pipeline[currentIndex + 1];
                         next[nextAgentName] = {
                            status: 'running',
                            message: 'Processing data...'
                         };
                      }

                      localStorage.setItem('final_agent_states', JSON.stringify(next));
                      return next;
                    });
                  }
                } else if (data.status === 'done') {
                  if (isMounted) {
                    setTimeout(() => { navigate(`/analysis`); }, 1000);
                  }
                  return;
                } else if (data.status === 'error') {
                  if (isMounted) setError(data.message || 'Stream error occurred.');
                  return;
                }
              } catch (e) {
                console.warn('Failed to parse SSE JSON', e);
              }
            }
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Error executing clinical pipeline.');
      }
    };

    startStream();

    return () => { isMounted = false; };
  }, [analysisId, isDemo, navigate]);

  const renderAgentNode = (agentName: AgentName) => {
    if (!agentStates) return null;
    const state = agentStates[agentName] || { status: 'idle' };
    
    let statusStyles = 'bg-white/80 border-brand-slate/10 text-brand-slate/60';
    let StatusIcon = Clock;

    if (state.status === 'running') {
      statusStyles = 'bg-white border-brand-lavender ring-2 ring-brand-lavender/20 text-brand-plum shadow-md scale-[1.02] z-10 relative';
      StatusIcon = Loader2;
    } else if (state.status === 'completed') {
      statusStyles = 'bg-brand-sage-bg/30 text-brand-sage-text border-brand-sage-text/20 shadow-sm';
      StatusIcon = CheckCircle;
    } else if (state.status === 'failed') {
      statusStyles = 'bg-brand-rose-bg/30 text-brand-rose-text border-brand-rose-text/20 shadow-sm';
      StatusIcon = AlertCircle;
    }

    return (
      <div 
        key={agentName}
        onClick={() => setSelectedAgent(selectedAgent === agentName ? null : agentName)}
        className={`border p-3.5 rounded-xl flex flex-col transition-all duration-300 shadow-xxs cursor-pointer hover:opacity-80 ${statusStyles}`}
      >
        <div className="flex items-start gap-3 w-full">
          <StatusIcon className={`w-4 h-4 mt-0.5 shrink-0 ${state.status === 'running' ? 'animate-spin' : ''}`} />
          <div className="min-w-0 flex-1">
            <h4 className="text-xs font-semibold truncate">{agentName} Agent</h4>
            <p className="text-[10px] opacity-80 mt-0.5 truncate font-light">
              {state.message || (state.status === 'idle' ? 'In queue' : 'Standby')}
            </p>
          </div>
        </div>
        
        {selectedAgent === agentName && state.status !== 'idle' && (
          <div className="mt-3 pt-3 border-t border-current/10 flex flex-col gap-2 text-[10px] animate-in slide-in-from-top-2 duration-200">
            <div className="flex justify-between">
              <span className="font-bold opacity-70">STATUS</span>
              <span className="uppercase tracking-wider">{state.status}</span>
            </div>
            
            <div className="flex flex-col gap-0.5">
              <span className="font-bold opacity-70">WHY RUN?</span>
              <span className="font-light">{state.reason_for_execution || 'Standard execution pipeline'}</span>
            </div>
            
            {state.status === 'failed' && (
              <div className="flex flex-col gap-0.5 text-brand-rose-text mt-1">
                <span className="font-bold">ERROR</span>
                <span className="font-light">{state.message}</span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col items-center justify-center text-center mt-6 mb-8">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-lavender to-brand-plum text-white flex items-center justify-center mb-4 animate-pulse shadow-lg ring-4 ring-brand-lavender/20">
          <Sparkles className="w-8 h-8 fill-current" />
        </div>
        <h2 className="font-display text-2xl font-extrabold text-brand-plum tracking-tight">AI Clinical Mapping Underway</h2>
        <p className="text-sm text-brand-slate font-light mt-2 max-w-lg mx-auto">
          Our multi-agent supervisors are orchestrating document extractions and guidelines checks in real-time.
        </p>
      </div>

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-2xl text-xs flex items-center gap-2.5 max-w-2xl mx-auto w-full">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {agentStates ? (
        <div className="flex flex-col md:flex-row gap-6 items-stretch relative">
          
          <div className="flex-1 bg-white/60 backdrop-blur-xl border border-white/40 p-6 rounded-3xl shadow-xl shadow-brand-slate/5 flex flex-col gap-4">
            <div className="flex items-center gap-3 pb-3 border-b border-brand-slate/10">
              <div className="p-2 rounded-xl bg-white shadow-sm text-brand-slate border border-brand-slate/10">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="font-display text-sm font-bold text-brand-plum uppercase tracking-wider">1. Intake & Diagnostics</h3>
            </div>
            <div className="flex flex-col gap-3">
              {intakeGroup.map(renderAgentNode)}
            </div>
          </div>

          <div className="hidden md:flex items-center justify-center text-brand-lavender/30 self-center">
            <ArrowRight className="w-8 h-8" />
          </div>

          <div className="flex-1 bg-white/60 backdrop-blur-xl border border-white/40 p-6 rounded-3xl shadow-xl shadow-brand-lavender/5 flex flex-col gap-4">
            <div className="flex items-center gap-3 pb-3 border-b border-brand-slate/10">
              <div className="p-2 rounded-xl bg-gradient-to-br from-brand-lavender to-brand-plum text-white shadow-sm">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="font-display text-sm font-bold text-brand-plum uppercase tracking-wider">2. Evidence Reasoning</h3>
            </div>
            <div className="flex flex-col gap-3">
              {reasoningGroup.map(renderAgentNode)}
            </div>
          </div>

          <div className="hidden md:flex items-center justify-center text-brand-lavender/30 self-center">
            <ArrowRight className="w-8 h-8" />
          </div>

          <div className="flex-1 bg-white/60 backdrop-blur-xl border border-white/40 p-6 rounded-3xl shadow-xl shadow-brand-sage-text/5 flex flex-col gap-4">
            <div className="flex items-center gap-3 pb-3 border-b border-brand-slate/10">
              <div className="p-2 rounded-xl bg-brand-sage-bg text-brand-sage-text border border-brand-sage-text/20 shadow-sm">
                <Award className="w-5 h-5" />
              </div>
              <h3 className="font-display text-sm font-bold text-brand-plum uppercase tracking-wider">3. Referral Guidance</h3>
            </div>
            <div className="flex flex-col gap-3">
              {advisoryGroup.map(renderAgentNode)}
            </div>
          </div>

        </div>
      ) : (
        <div className="bg-brand-card border border-brand-slate/10 p-12 rounded-2xl text-center shadow-sm flex flex-col items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-brand-lavender animate-spin mb-3" />
          <p className="text-xs text-brand-slate font-light">Contacting Clinical Supervisors{dots}</p>
        </div>
      )}

      {logs.length > 0 && (
        <div className="bg-brand-plum rounded-2xl p-5 shadow-sm flex flex-col gap-3 font-mono text-[10px] sm:text-xs text-brand-bg mt-2 overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-2 border-b border-brand-slate/20 pb-3 mb-1 text-brand-lavender-light">
            <Clock className="w-4 h-4" />
            <h3 className="font-semibold tracking-wider">AGENT EXECUTION LOG</h3>
          </div>
          <div className="flex flex-col gap-2 max-h-[200px] overflow-y-auto pr-2 custom-scrollbar">
            {logs.map((log, idx) => (
              <div key={idx} className="flex items-center gap-4 border-l-2 border-brand-slate/20 pl-3 py-0.5">
                <span className="text-brand-slate opacity-70 w-16 shrink-0">{log.time}</span>
                <span className="font-semibold w-32 shrink-0">{log.agent}</span>
                <span className={`px-2 py-0.5 rounded-sm uppercase tracking-wider text-[9px] ${
                  log.status === 'completed' ? 'bg-brand-sage-primary/20 text-brand-sage-primary' : 
                  log.status === 'skipped' ? 'bg-brand-slate/20 text-brand-slate' :
                  log.status === 'failed' ? 'bg-brand-rose-bg text-brand-rose-text' :
                  'bg-brand-lavender/20 text-brand-lavender'
                }`}>
                  {log.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
