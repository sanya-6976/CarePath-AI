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
  const analysisId = searchParams.get('id');
  const isDemo = searchParams.get('demo') === 'true';

  const [agentStates, setAgentStates] = useState<Record<AgentName, AgentState> | null>(null);
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
    if (isDemo) {
      // Hackathon demo loop simulator
      const demoStates: Record<AgentName, AgentState> = pipeline.reduce((acc, name) => {
        acc[name] = { status: 'idle' };
        return acc;
      }, {} as Record<AgentName, AgentState>);
      setAgentStates(demoStates);

      let step = 0;
      const demoTimer = setInterval(() => {
        setAgentStates((prev) => {
          if (!prev) return null;
          const next = { ...prev };
          const activeAgent = pipeline[step];
          
          if (step > 0) {
            next[pipeline[step - 1]] = { status: 'completed', message: 'Task finalized.' };
          }
          if (activeAgent) {
            next[activeAgent] = { status: 'running', message: `Correlating context${dots}` };
          }
          return next;
        });

        step++;
        if (step > pipeline.length) {
          clearInterval(demoTimer);
          navigate('/analysis');
        }
      }, 1000);

      return () => clearInterval(demoTimer);
    }

    if (!analysisId) {
      setError('Missing active Analysis ID parameter.');
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const result = await analysisService.getAnalysis(analysisId);
        if (result.agent_states) {
          setAgentStates(result.agent_states as Record<AgentName, AgentState>);
        }
        if (result.status === 'completed') {
          clearInterval(pollInterval);
          navigate('/analysis');
        } else if (result.status === 'failed') {
          clearInterval(pollInterval);
          setError('The clinical mapping process encountered an unexpected failure.');
        }
      } catch (err: any) {
        console.error('Error polling analysis:', err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [analysisId, isDemo, navigate, dots]);

  const renderAgentNode = (agentName: AgentName) => {
    if (!agentStates) return null;
    const state = agentStates[agentName] || { status: 'idle' };
    
    let statusStyles = 'bg-brand-bg text-brand-slate/40 border-brand-slate/10';
    let StatusIcon = Clock;

    if (state.status === 'running') {
      statusStyles = 'bg-brand-lavender-light text-brand-lavender border-brand-lavender/35 ring-4 ring-brand-lavender/10 font-medium scale-102';
      StatusIcon = Loader2;
    } else if (state.status === 'completed') {
      statusStyles = 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/10 font-medium';
      StatusIcon = CheckCircle;
    } else if (state.status === 'failed') {
      statusStyles = 'bg-brand-rose-bg text-brand-rose-text border-brand-rose-text/15';
      StatusIcon = AlertCircle;
    }

    return (
      <div 
        key={agentName}
        className={`border p-3.5 rounded-xl flex items-start gap-3 transition-all duration-300 shadow-xxs ${statusStyles}`}
      >
        <StatusIcon className={`w-4 h-4 mt-0.5 shrink-0 ${state.status === 'running' ? 'animate-spin' : ''}`} />
        <div className="min-w-0">
          <h4 className="text-xs font-semibold truncate">{agentName} Agent</h4>
          <p className="text-[10px] opacity-80 mt-0.5 truncate max-w-[170px] font-light">
            {state.message || (state.status === 'idle' ? 'In queue' : 'Standby')}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      {/* Pulse Status */}
      <div className="flex flex-col items-center justify-center text-center mt-2 mb-4">
        <div className="w-12 h-12 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center mb-3 animate-pulse shadow-xs">
          <Sparkles className="w-6 h-6 fill-current" />
        </div>
        <h2 className="font-display text-lg font-bold text-brand-plum">AI Clinical Mapping Underway</h2>
        <p className="text-xs text-brand-slate font-light mt-1">
          Our multi-agent supervisors are orchestrating document extractions and guidelines checks.
        </p>
      </div>

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-2xl text-xs flex items-center gap-2.5 max-w-2xl mx-auto w-full">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Orchestration Flowchart Grid */}
      {agentStates ? (
        <div className="flex flex-col md:flex-row gap-6 items-stretch relative">
          
          {/* Group 1: Intake */}
          <div className="flex-1 bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-2 border-b border-brand-slate/5">
              <div className="p-1.5 rounded-lg bg-brand-bg text-brand-slate">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="font-display text-sm font-semibold text-brand-plum">1. Intake & Diagnostics</h3>
            </div>
            <div className="flex flex-col gap-3">
              {intakeGroup.map(renderAgentNode)}
            </div>
          </div>

          {/* Flow Connector Arrow Desktop 1 */}
          <div className="hidden md:flex items-center justify-center text-brand-slate/30 self-center">
            <ArrowRight className="w-6 h-6" />
          </div>

          {/* Group 2: Reasoning */}
          <div className="flex-1 bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-2 border-b border-brand-slate/5">
              <div className="p-1.5 rounded-lg bg-brand-lavender-light text-brand-lavender">
                <Brain className="w-4 h-4" />
              </div>
              <h3 className="font-display text-sm font-semibold text-brand-plum">2. Evidence Reasoning</h3>
            </div>
            <div className="flex flex-col gap-3">
              {reasoningGroup.map(renderAgentNode)}
            </div>
          </div>

          {/* Flow Connector Arrow Desktop 2 */}
          <div className="hidden md:flex items-center justify-center text-brand-slate/30 self-center">
            <ArrowRight className="w-6 h-6" />
          </div>

          {/* Group 3: Advisory */}
          <div className="flex-1 bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-2 border-b border-brand-slate/5">
              <div className="p-1.5 rounded-lg bg-brand-sage-bg text-brand-sage-text">
                <Award className="w-4 h-4" />
              </div>
              <h3 className="font-display text-sm font-semibold text-brand-plum">3. Referral Guidance</h3>
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
    </div>
  );
}
