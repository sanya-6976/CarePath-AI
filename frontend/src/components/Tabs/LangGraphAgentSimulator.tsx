import React, { useState } from 'react';
import { AGENT_SPECS } from '../../data/architectureData';
import { 
  Play, 
  Bot, 
  Clock, 
  ShieldAlert, 
  CheckCircle2, 
  Image as ImageIcon, 
  FileText,
  Activity,
  Zap,
  Sparkles
} from 'lucide-react';

export const LangGraphAgentSimulator: React.FC = () => {
  const [promptInput, setPromptInput] = useState<string>(
    "I have had severe joint stiffness in both knees for 3 weeks along with morning fatigue and a reddish rash."
  );
  const [hasImage, setHasImage] = useState<boolean>(true);
  const [hasDocument, setHasDocument] = useState<boolean>(true);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [orchResult, setOrchResult] = useState<any | null>(null);
  const [activeStepIndex, setActiveStepIndex] = useState<number | null>(null);

  const presets = [
    {
      label: "Routine Autoimmune Intake",
      prompt: "I have had severe joint stiffness in both knees for 3 weeks along with morning fatigue and a reddish rash.",
      img: true,
      doc: true
    },
    {
      label: "Emergency Red-Flag Trigger",
      prompt: "I suddenly developed crushing chest pain radiating to my left arm, shortness of breath, and cold sweat.",
      img: false,
      doc: false
    },
    {
      label: "Visual Rash Triage Only",
      prompt: "I noticed a circular itchy rash on my arm that appeared after hiking.",
      img: true,
      doc: false
    },
    {
      label: "Lab Document Analysis Only",
      prompt: "I got my annual blood report back showing WBC elevated 11.2 and CRP 18.5.",
      img: false,
      doc: true
    }
  ];

  const runSimulation = async () => {
    setIsRunning(true);
    setOrchResult(null);
    setActiveStepIndex(0);

    try {
      const response = await fetch('/api/v1/agents/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: `sess_${Date.now()}`,
          patient_id: "pat_demo_01",
          raw_prompt: promptInput,
          uploaded_image_urls: hasImage ? ["https://storage.carepath.ai/demo_skin.jpg"] : [],
          uploaded_doc_urls: hasDocument ? ["https://storage.carepath.ai/demo_lab.pdf"] : []
        })
      });

      const data = await response.json();
      setOrchResult(data);

      if (data.execution_history) {
        for (let i = 0; i < data.execution_history.length; i++) {
          setActiveStepIndex(i);
          await new Promise((resolve) => setTimeout(resolve, 200));
        }
      }
    } catch (err) {
      console.error("Orchestration error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-900/40 shadow-xl text-white space-y-2">
        <div className="flex items-center space-x-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          <h2 className="text-xl font-bold">LangGraph Multi-Agent Orchestration Command Center</h2>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            Sprint 2 Live Engine
          </span>
        </div>
        <p className="text-xs text-slate-300 max-w-3xl">
          Live execution of the 11-Agent dynamic graph state machine. Test how the Supervisor routes execution, short-circuits on emergency red flags, bypasses unneeded nodes, queries ChromaDB RAG guidelines, and commits checkpoints.
        </p>
      </div>

      {/* Preset Buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-400 mr-2">Quick Scenarios:</span>
        {presets.map((p, idx) => (
          <button
            key={idx}
            onClick={() => {
              setPromptInput(p.prompt);
              setHasImage(p.img);
              setHasDocument(p.doc);
            }}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium transition-all border border-slate-700/60"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Controls & Graph Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scenario Input Configurator */}
        <div className="lg:col-span-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 text-slate-200">
          <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center justify-between">
            <span>Orchestration Input Payload</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </h3>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Patient Prompt / Symptoms</label>
            <textarea
              rows={4}
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
              placeholder="Describe patient symptoms..."
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Attached Payload Artifacts</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setHasImage(!hasImage)}
                className={`p-2.5 rounded-xl border text-xs font-medium flex items-center justify-center space-x-2 transition ${
                  hasImage
                    ? 'bg-pink-500/20 border-pink-500/50 text-pink-300'
                    : 'bg-slate-950 border-slate-800 text-slate-500'
                }`}
              >
                <ImageIcon className="w-4 h-4" />
                <span>Medical Image</span>
              </button>

              <button
                type="button"
                onClick={() => setHasDocument(!hasDocument)}
                className={`p-2.5 rounded-xl border text-xs font-medium flex items-center justify-center space-x-2 transition ${
                  hasDocument
                    ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                    : 'bg-slate-950 border-slate-800 text-slate-500'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>PDF Lab Report</span>
              </button>
            </div>
          </div>

          <button
            onClick={runSimulation}
            disabled={isRunning}
            className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/20 transition disabled:opacity-50"
          >
            {isRunning ? (
              <Activity className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            <span>{isRunning ? "Running Multi-Agent Engine..." : "Execute LangGraph Workflow"}</span>
          </button>
        </div>

        {/* 11 Agents Visual Grid */}
        <div className="lg:col-span-8 p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Zap className="w-4 h-4 text-indigo-400" />
              <span>11-Agent System Graph Topology</span>
            </h3>
            {orchResult && (
              <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                orchResult.is_emergency
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
                {orchResult.is_emergency ? "EMERGENCY BYPASS" : "WORKFLOW COMPLETED"}
              </span>
            )}
          </div>

          {/* Agent Cards Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
            {AGENT_SPECS.map((agent) => {
              const executedStep = orchResult?.execution_history?.find((s: any) => s.agent_id === agent.id);
              const isExecuting = isRunning && executedStep && executedStep.step_number === (activeStepIndex! + 1);

              return (
                <div
                  key={agent.id}
                  className={`p-3 rounded-xl border transition-all text-xs space-y-1.5 relative overflow-hidden ${
                    executedStep
                      ? executedStep.status === 'EMERGENCY_TRIGGERED'
                        ? 'bg-red-950/40 border-red-500 text-white'
                        : 'bg-slate-950 border-emerald-500/60 text-slate-200'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400'
                  } ${isExecuting ? 'ring-2 ring-indigo-500 animate-pulse' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: agent.color }}
                    />
                    {executedStep ? (
                      executedStep.status === 'EMERGENCY_TRIGGERED' ? (
                        <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      )
                    ) : (
                      <span className="text-[10px] text-slate-600 font-mono">IDLE</span>
                    )}
                  </div>

                  <h4 className="font-bold text-white leading-tight truncate">{agent.name}</h4>
                  <p className="text-[10px] text-slate-400 line-clamp-1">{agent.role}</p>

                  {executedStep && (
                    <div className="text-[10px] font-mono text-emerald-300 pt-1 border-t border-slate-800/80">
                      {executedStep.decision}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Execution Trace Timeline & Agent Outputs */}
          {orchResult && (
            <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center space-x-2">
                <Clock className="w-4 h-4 text-indigo-400" />
                <span>Live Execution History & Agent Outputs</span>
              </h4>

              <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {orchResult.execution_history?.map((step: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300">
                          Step {step.step_number}
                        </span>
                        <span className="font-bold text-white">{step.agent_name}</span>
                        <span className="text-slate-500 font-mono text-[10px]">({step.execution_time_ms}ms)</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        step.status === 'EMERGENCY_TRIGGERED'
                          ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}>
                        {step.status}
                      </span>
                    </div>
                    <p className="text-slate-300 font-mono text-[11px]">{step.decision}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
