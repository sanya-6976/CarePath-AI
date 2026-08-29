import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Network, ClipboardPlus, FileText, ScanEye, CalendarClock, 
    BookOpen, Brain, Stethoscope, ShieldAlert, ClipboardCheck, 
    Bell, CheckCircle2, Circle, Loader2, AlertCircle, XCircle,
    ChevronRight, ChevronDown, Activity, SkipForward, X, ArrowRight
} from 'lucide-react';

export type AgentStatus = 'Waiting' | 'Running' | 'Completed' | 'Warning' | 'Failed' | 'Skipped';

export interface AgentInfo {
    id: string;
    name: string;
    description: string;
    icon: React.ReactNode;
    status: AgentStatus;
    role: string;
    inputs: string[];
    outputs: string;
    context: string[];
    reason_for_execution?: string;
    user_action_required?: string;
}

const AGENTS: AgentInfo[] = [
    { 
        id: 'supervisor', name: 'Supervisor Agent', description: 'Orchestrates the multi-agent workflow.', icon: <Network size={20} />, status: 'Waiting',
        role: 'Manages execution flow and delegates tasks to specialized agents.',
        inputs: ['Patient ID', 'Session Context'],
        outputs: 'Execution Plan',
        context: ['Graph state definitions'],
        reason_for_execution: 'Initializes and coordinates the overall clinical pipeline.',
        user_action_required: 'Wait for orchestration to finish.',
        actionLabel: 'View Dashboard',
        actionRoute: '/dashboard'
    },
    { 
        id: 'intake', name: 'Intake Agent', description: 'Gathers initial patient symptoms.', icon: <ClipboardPlus size={20} />, status: 'Waiting',
        role: 'Extracts chief complaints and basic demographic vectors.',
        inputs: ['Raw patient prompt'],
        outputs: 'Structured symptoms list',
        context: ['Symptom ontologies'],
        reason_for_execution: 'Standardized patient chief complaint and symptoms required for downstream analysis.',
        user_action_required: 'Review extracted symptoms in your Care Journey.',
        actionLabel: 'Update Condition',
        actionRoute: '/dashboard'
    },
    { 
        id: 'vision', name: 'Vision Agent', description: 'Analyzes medical images.', icon: <ScanEye size={20} />, status: 'Waiting',
        role: 'Processes radiological scans and dermatological images.',
        inputs: ['Uploaded image URLs'],
        outputs: 'Visual findings summary',
        context: ['Image recognition models'],
        reason_for_execution: 'Medical images detected that require vision analysis.',
        user_action_required: 'Check the image findings summary.',
        actionLabel: 'Upload / Capture Image',
        actionRoute: '/upload'
    },
    { 
        id: 'docs', name: 'Medical Docs Agent', description: 'Extracts data from medical documents.', icon: <FileText size={20} />, status: 'Waiting',
        role: 'Parses unstructured PDFs and lab reports into structured data.',
        inputs: ['Uploaded document URLs'],
        outputs: 'Parsed clinical facts',
        context: ['OCR', 'Medical NLP'],
        reason_for_execution: 'Clinical documents detected requiring data extraction.',
        user_action_required: 'Verify extracted lab results.',
        actionLabel: 'Upload Clinical Document',
        actionRoute: '/upload'
    },
    { 
        id: 'timeline', name: 'Timeline Agent', description: 'Maintains longitudinal patient chronology.', icon: <CalendarClock size={20} />, status: 'Waiting',
        role: 'Constructs a historical timeline of patient health events.',
        inputs: ['Structured symptoms', 'Parsed facts'],
        outputs: 'Chronological timeline',
        context: ['Historical patient records'],
        reason_for_execution: 'Historical context required to determine symptom progression.',
        user_action_required: 'None.',
        actionLabel: 'View Care Journey Timeline',
        actionRoute: '/journey'
    },
    { 
        id: 'evidence', name: 'Evidence Agent', description: 'Retrieves relevant medical evidence.', icon: <BookOpen size={20} />, status: 'Waiting',
        role: 'Queries clinical guidelines matching the patient state.',
        inputs: ['Timeline', 'Symptoms'],
        outputs: 'Retrieved medical evidence',
        context: ['Medical literature', 'RAG database'],
        reason_for_execution: 'Symptom complexity requires evidence-based literature retrieval.',
        user_action_required: 'Review attached clinical guidelines.',
        actionLabel: 'View Recommendations',
        actionRoute: '/analysis'
    },
    { 
        id: 'clinical_reasoning', name: 'Clinical Reasoning', description: 'Formulates differential hypotheses.', icon: <Brain size={20} />, status: 'Waiting',
        role: 'Synthesizes available evidence and longitudinal context.',
        inputs: ['Current symptoms', 'Medical document findings', 'Timeline/history', 'Retrieved evidence'],
        outputs: 'Concise explanation of the reasoning result.',
        context: ['Historical patient updates', 'Retrieved medical evidence'],
        reason_for_execution: 'Aggregates all findings into a structured differential assessment.',
        user_action_required: 'Consult with physician regarding the reasoning.',
        actionLabel: 'View Full Analysis',
        actionRoute: '/analysis'
    },
    { 
        id: 'safety', name: 'Risk & Safety Agent', description: 'Monitors for emergencies and alerts.', icon: <ShieldAlert size={20} />, status: 'Waiting',
        role: 'Acts as a critical safeguard to identify urgent medical conditions.',
        inputs: ['Clinical reasoning hypotheses'],
        outputs: 'Safety clearance or escalation alert',
        context: ['Emergency triage protocols'],
        reason_for_execution: 'Mandatory safety check to ensure no life-threatening emergencies exist.',
        user_action_required: 'Immediately follow any urgent safety alerts.',
        actionLabel: 'View Safety Protocols',
        actionRoute: '/dashboard'
    },
    { 
        id: 'referral', name: 'Referral Agent', description: 'Recommends specialist pathways.', icon: <Stethoscope size={20} />, status: 'Waiting',
        role: 'Routes the patient to the most appropriate clinical specialty.',
        inputs: ['Differential hypotheses', 'Safety clearance'],
        outputs: 'Specialist recommendation',
        context: ['Provider directories'],
        reason_for_execution: 'Severity of assessment requires specialist routing.',
        user_action_required: 'Use the Specialist Finder to book an appointment.',
        actionLabel: 'Find Specialists',
        actionRoute: '/dashboard'
    },
    { 
        id: 'care_plan', name: 'Care Plan Agent', description: 'Generates non-medical action items.', icon: <ClipboardCheck size={20} />, status: 'Waiting',
        role: 'Drafts patient-facing next steps and visit preparations.',
        inputs: ['Referral recommendation'],
        outputs: 'Actionable care plan',
        context: ['Standard care protocols'],
        reason_for_execution: 'Generates actionable next steps based on the final analysis.',
        user_action_required: 'Prepare questions and follow your customized care plan.',
        actionLabel: 'View Care Plan Checklist',
        actionRoute: '/dashboard'
    },
    { 
        id: 'follow_up', name: 'Follow-up Agent', description: 'Schedules subsequent check-ins.', icon: <Bell size={20} />, status: 'Waiting',
        role: 'Determines the timeline for patient re-evaluation.',
        inputs: ['Care plan'],
        outputs: 'Follow-up schedule',
        context: ['Outcome tracking guidelines'],
        reason_for_execution: 'Ensures continuous tracking of patient health journey.',
        user_action_required: 'Note your upcoming follow-up schedule.',
        actionLabel: 'View Reminders',
        actionRoute: '/medications'
    },
];

const StatusIcon = ({ status, size = 16 }: { status: AgentStatus, size?: number }) => {
    switch (status) {
        case 'Completed': return <CheckCircle2 size={size} className="text-brand-sage-text" />;
        case 'Running': return <Loader2 size={size} className="text-brand-lavender animate-spin" />;
        case 'Warning': return <AlertCircle size={size} className="text-brand-amber-text" />;
        case 'Failed': return <XCircle size={size} className="text-brand-rose-text" />;
        case 'Skipped': return <SkipForward size={size} className="text-brand-slate/50" />;
        case 'Waiting':
        default:
            return <Circle size={size} className="text-brand-slate/30" />;
    }
};

export const AgentVisualization: React.FC<{ activeAgents?: Record<string, any>, isExpandedByDefault?: boolean }> = ({ activeAgents = {}, isExpandedByDefault = false }) => {
    const navigate = useNavigate();
    const [isExpanded, setIsExpanded] = useState(isExpandedByDefault);
    const [selectedAgent, setSelectedAgent] = useState<AgentInfo & { actionLabel?: string, actionRoute?: string } | null>(null);

    const mergedAgents = AGENTS.map(agent => {
        const remoteState = activeAgents[agent.id];
        let dynamicInputs = agent.inputs;
        if (remoteState?.input) {
            dynamicInputs = Array.isArray(remoteState.input) ? remoteState.input : [String(remoteState.input)];
        } else if (remoteState?.inputs) {
            dynamicInputs = Array.isArray(remoteState.inputs) ? remoteState.inputs : [String(remoteState.inputs)];
        }

        let dynamicOutputs = agent.outputs;
        if (remoteState?.output) dynamicOutputs = String(remoteState.output);
        else if (remoteState?.outputs) dynamicOutputs = String(remoteState.outputs);
        else if (remoteState?.details) dynamicOutputs = String(remoteState.details);

        return {
            ...agent,
            status: remoteState?.status === 'completed' ? 'Completed' : (remoteState?.status === 'skipped' ? 'Skipped' : (remoteState?.status === 'failed' ? 'Failed' : (remoteState?.status === 'running' ? 'Running' : agent.status))),
            reason_for_execution: remoteState?.reason_for_execution || agent.reason_for_execution,
            user_action_required: remoteState?.user_action_required || agent.user_action_required,
            inputs: dynamicInputs,
            outputs: dynamicOutputs
        };
    });

    const counts = {
        completed: mergedAgents.filter(a => a.status === 'Completed').length,
        running: mergedAgents.filter(a => a.status === 'Running').length,
        waiting: mergedAgents.filter(a => a.status === 'Waiting').length,
        failed: mergedAgents.filter(a => a.status === 'Failed').length,
    };

    if (!isExpanded) {
        return (
            <div className="bg-brand-card rounded-2xl shadow-sm border border-brand-slate/10 p-5 font-sans hover:border-brand-lavender/30 transition-colors">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-brand-lavender-light text-brand-lavender rounded-xl flex items-center justify-center shrink-0">
                        <Activity className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-brand-plum">CarePath AI Agents</h3>
                        <p className="text-xs text-brand-slate">11 Specialized Agents</p>
                    </div>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-brand-slate mb-4 bg-brand-bg p-3 rounded-xl border border-brand-slate/10">
                    <span className="font-semibold text-brand-plum">{counts.completed} completed</span> <span className="opacity-50">·</span>
                    <span className="font-semibold text-brand-plum">{counts.running} running</span> <span className="opacity-50">·</span>
                    <span className="font-semibold text-brand-plum">{counts.waiting} waiting</span>
                </div>

                <button 
                    onClick={() => setIsExpanded(true)}
                    className="w-full py-2.5 px-4 bg-white border border-brand-slate/15 hover:bg-brand-bg text-brand-plum text-xs font-semibold rounded-xl flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xxs"
                >
                    View Agent Activity
                    <ChevronRight size={14} />
                </button>
            </div>
        );
    }

    return (
        <div className="bg-brand-card rounded-3xl shadow-sm border border-brand-slate/10 p-6 font-sans animate-in fade-in duration-300 relative overflow-hidden h-full flex flex-col">
            <div className="flex items-center justify-between mb-6 relative z-10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-brand-lavender-light text-brand-lavender rounded-xl flex items-center justify-center shrink-0 shadow-xxs">
                        <Network className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-brand-plum">CarePath AI Agents</h3>
                        <p className="text-xs text-brand-slate">11 Agents Orchestrated</p>
                    </div>
                </div>
                <button 
                    onClick={() => setIsExpanded(false)}
                    className="p-2 hover:bg-brand-bg rounded-lg text-brand-slate transition-colors cursor-pointer"
                >
                    <ChevronDown size={18} />
                </button>
            </div>
            
            {/* SVG Pathway Background */}
            <div className="absolute inset-0 pointer-events-none z-0 opacity-20 hidden md:block">
                <svg width="100%" height="100%" className="absolute top-0 left-0">
                    <path d="M 50,150 L 50,300 C 50,400 200,300 200,450" stroke="url(#lavender-gradient)" strokeWidth="2" fill="none" strokeDasharray="5,5" className={counts.running > 0 ? "animate-[dash_20s_linear_infinite]" : ""} />
                    <defs>
                        <linearGradient id="lavender-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#7E69AB" />
                            <stop offset="100%" stopColor="#A894C2" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 relative z-10 flex-1 content-start">
                {mergedAgents.map((agent) => {
                    const isRunning = agent.status === 'Running';
                    const isFailed = agent.status === 'Failed';
                    const isCompleted = agent.status === 'Completed';

                    let cardClasses = "flex flex-col p-4 rounded-2xl border transition-all group cursor-pointer shadow-xxs relative overflow-hidden bg-white ";
                    if (isRunning) cardClasses += "border-brand-lavender ring-2 ring-brand-lavender/20 scale-102 shadow-sm";
                    else if (isFailed) cardClasses += "border-brand-rose-text/30 bg-brand-rose-bg/10";
                    else if (isCompleted) cardClasses += "border-brand-sage-text/30 hover:border-brand-lavender/50";
                    else cardClasses += "border-brand-slate/10 hover:border-brand-lavender/30 opacity-70";

                    return (
                        <div 
                            key={agent.id} 
                            className={cardClasses}
                            onClick={() => setSelectedAgent(agent)}
                        >
                            {isRunning && (
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-brand-lavender/5 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
                            )}
                            <div className="flex justify-between items-start mb-3 relative z-10">
                                <div className={`p-2.5 rounded-xl ${isRunning ? 'bg-brand-lavender text-white shadow-sm' : isFailed ? 'bg-brand-rose-bg text-brand-rose-text' : isCompleted ? 'bg-brand-sage-bg text-brand-sage-text' : 'bg-brand-bg text-brand-slate'}`}>
                                    {agent.icon}
                                </div>
                                <StatusIcon status={agent.status} size={20} />
                            </div>
                            <span className="text-xs font-bold text-brand-plum block mb-1.5 relative z-10">{agent.name}</span>
                            <span className="text-[10px] text-brand-slate leading-snug line-clamp-2 font-light relative z-10">{agent.description}</span>
                            
                            <div className="absolute top-0 left-0 w-1 h-full bg-transparent group-hover:bg-brand-lavender transition-colors z-10" />
                        </div>
                    )
                })}
            </div>

            {/* Agent Inspection Drawer / Modal */}
            {selectedAgent && (
                <div className="absolute inset-0 z-50 bg-brand-plum/40 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4 animate-in fade-in duration-200">
                    <div className="bg-white w-full h-4/5 sm:h-auto sm:max-h-[90%] sm:max-w-md rounded-t-3xl sm:rounded-3xl border border-brand-slate/10 shadow-xl flex flex-col animate-in slide-in-from-bottom-10 sm:zoom-in-95 duration-200 overflow-hidden">
                        <div className="flex items-center justify-between border-b border-brand-slate/10 p-5 bg-brand-bg/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-white rounded-lg shadow-xxs border border-brand-slate/5 text-brand-lavender">
                                    {selectedAgent.icon}
                                </div>
                                <div>
                                    <h3 className="font-display font-bold text-sm text-brand-plum uppercase tracking-wider">{selectedAgent.name}</h3>
                                    <div className="flex items-center gap-1.5 mt-1">
                                        <StatusIcon status={selectedAgent.status} size={14} />
                                        <span className="text-[10px] font-bold text-brand-slate uppercase">{selectedAgent.status}</span>
                                    </div>
                                </div>
                            </div>
                            <button 
                                onClick={() => setSelectedAgent(null)}
                                className="p-1.5 rounded-lg hover:bg-brand-card text-brand-slate transition-all border border-transparent hover:border-brand-slate/10 shadow-xxs"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto flex flex-col gap-5 text-sm font-sans">
                            <div>
                                <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-1.5">Role</span>
                                <p className="text-xs text-brand-plum font-medium leading-relaxed">{selectedAgent.role}</p>
                            </div>
                            
                            {selectedAgent.reason_for_execution && (
                                <div className="bg-brand-bg rounded-2xl p-4 border border-brand-slate/5">
                                    <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-2">Why was this agent run?</span>
                                    <p className="text-xs text-brand-plum font-semibold">{selectedAgent.reason_for_execution}</p>
                                </div>
                            )}

                            {selectedAgent.status === 'Skipped' && (
                                <div className="bg-brand-slate/5 rounded-2xl p-4 border border-brand-slate/10">
                                    <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-2">Execution Skipped</span>
                                    <p className="text-xs text-brand-slate font-medium">This agent was bypassed. Necessary conditions or inputs were not met.</p>
                                </div>
                            )}

                            {selectedAgent.user_action_required && selectedAgent.status !== 'Skipped' && (
                                <div className="bg-brand-sage-bg/30 rounded-2xl p-4 border border-brand-sage-text/20">
                                    <span className="text-[10px] font-bold text-brand-sage-text uppercase tracking-wider block mb-2">Action for you</span>
                                    <p className="text-xs text-brand-sage-text font-bold">{selectedAgent.user_action_required}</p>
                                </div>
                            )}

                            {selectedAgent.status !== 'Skipped' && (
                                <>
                                    <div className="bg-brand-bg rounded-2xl p-4 border border-brand-slate/5">
                                        <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-2">Inputs</span>
                                        <ul className="flex flex-col gap-1.5">
                                            {(selectedAgent.inputs).map((input, idx) => (
                                                <li key={idx} className="text-xs text-brand-plum flex items-start gap-2 font-medium">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-brand-lavender/50 mt-1.5 shrink-0" />
                                                    {input}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="bg-brand-lavender-light/30 rounded-2xl p-4 border border-brand-lavender/10">
                                        <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider block mb-2">Output</span>
                                        <p className="text-xs text-brand-plum font-semibold">{selectedAgent.outputs}</p>
                                    </div>
                                </>
                            )}

                            <div>
                                <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-2">Context Used</span>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAgent.context.map((ctx, idx) => (
                                        <span key={idx} className="text-[10px] font-semibold text-brand-slate bg-brand-card border border-brand-slate/10 px-2.5 py-1 rounded-full">
                                            {ctx}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {selectedAgent.status === 'Failed' && (
                                <div className="bg-brand-rose-bg rounded-2xl p-4 border border-brand-rose-text/20 mt-2">
                                    <span className="text-[10px] font-bold text-brand-rose-text uppercase tracking-wider block mb-1 flex items-center gap-1.5">
                                        <AlertCircle size={14} /> Execution Error
                                    </span>
                                    <p className="text-xs text-brand-rose-text font-medium">
                                        Agent execution failed. A safe fallback was triggered to preserve system stability.
                                    </p>
                                </div>
                            )}

                            {selectedAgent.actionLabel && selectedAgent.actionRoute && (
                                <div className="mt-4 pt-4 border-t border-brand-slate/10 flex justify-end">
                                    <button
                                        onClick={() => navigate(selectedAgent.actionRoute!)}
                                        className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-sm transition-all flex items-center gap-2"
                                    >
                                        {selectedAgent.actionLabel}
                                        <ArrowRight size={14} />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
