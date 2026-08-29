import React, { useState } from 'react';
import { BLUEPRINT_TOPICS } from '../../data/architectureData';
import { CheckCircle2, ChevronRight, Layers, Shield, Database, Cpu, Terminal } from 'lucide-react';

export const ArchitectureBlueprintView: React.FC = () => {
  const [selectedTopicId, setSelectedTopicId] = useState<string>(BLUEPRINT_TOPICS[0].id);
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const categories = [
    { id: 'all', label: 'All 15 Topics' },
    { id: 'core', label: 'Core Backend' },
    { id: 'agents', label: 'LangGraph Agents' },
    { id: 'data', label: 'Database & RAG' },
    { id: 'security', label: 'Security & Auth' },
    { id: 'devops', label: 'DevOps & Integration' },
  ];

  const filteredTopics = BLUEPRINT_TOPICS.filter(
    (t) => filterCategory === 'all' || t.category === filterCategory
  );

  const selectedTopic = BLUEPRINT_TOPICS.find((t) => t.id === selectedTopicId) || BLUEPRINT_TOPICS[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Overview Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-900/40 shadow-xl text-white">
        <div className="max-w-3xl space-y-2">
          <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            Sprint 0 Architectural Deliverable
          </span>
          <h2 className="text-2xl font-bold tracking-tight">
            CarePath AI Backend Architecture Blueprint
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Production-grade software architecture for an Autonomous Healthcare Navigation Platform.
            Decoupled FastAPI gateway, LangGraph stateful multi-agent system, hybrid PostgreSQL + ChromaDB storage,
            and HIPAA-compliant security controls.
          </p>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setFilterCategory(cat.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterCategory === cat.id
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Master Detail Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Topic List (Sidebar) */}
        <div className="lg:col-span-4 space-y-2 max-h-[750px] overflow-y-auto pr-1">
          {filteredTopics.map((topic) => {
            const isSelected = topic.id === selectedTopic.id;
            return (
              <button
                key={topic.id}
                onClick={() => setSelectedTopicId(topic.id)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-start space-x-3 ${
                  isSelected
                    ? 'bg-indigo-600/10 border-indigo-500/80 text-white shadow-sm ring-1 ring-indigo-500/30'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${
                    isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {topic.number}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-semibold truncate leading-tight">{topic.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-snug">
                    {topic.summary}
                  </p>
                </div>
                <ChevronRight className={`w-4 h-4 shrink-0 mt-1 ${isSelected ? 'text-indigo-400' : 'text-slate-600'}`} />
              </button>
            );
          })}
        </div>

        {/* Selected Topic Content Panel */}
        <div className="lg:col-span-8 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 text-slate-200">
            {/* Title Header */}
            <div className="border-b border-slate-800 pb-4 space-y-2">
              <div className="flex items-center space-x-2 text-xs text-indigo-400 font-semibold uppercase tracking-wider">
                <span>Topic {selectedTopic.number}</span>
                <span>&bull;</span>
                <span className="capitalize">{selectedTopic.category} Architecture</span>
              </div>
              <h3 className="text-xl font-bold text-white">{selectedTopic.title}</h3>
              <p className="text-xs text-slate-400 italic">{selectedTopic.summary}</p>
            </div>

            {/* Key Architectural Decisions */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
              <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                <span>Principal Architect Key Decisions & Rationale</span>
              </h4>
              <ul className="space-y-2">
                {selectedTopic.keyDecisions.map((decision, idx) => (
                  <li key={idx} className="flex items-start space-x-2.5 text-xs text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                    <span>{decision}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* ASCII Diagram if available */}
            {selectedTopic.diagramAscii && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2">
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  <span>System Architecture Topology Diagram</span>
                </div>
                <pre className="text-[11px] font-mono text-emerald-300 leading-tight overflow-x-auto p-2 bg-slate-900/80 rounded-lg">
                  {selectedTopic.diagramAscii}
                </pre>
              </div>
            )}

            {/* Text Content */}
            <div className="prose prose-invert prose-xs max-w-none space-y-3 text-slate-300 leading-relaxed">
              {selectedTopic.content.split('\n\n').map((paragraph, idx) => {
                if (paragraph.startsWith('### ')) {
                  return (
                    <h4 key={idx} className="text-sm font-bold text-white mt-4 border-b border-slate-800 pb-1">
                      {paragraph.replace('### ', '')}
                    </h4>
                  );
                }
                return <p key={idx} className="text-xs text-slate-300">{paragraph}</p>;
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
