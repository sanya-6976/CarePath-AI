import React from 'react';
import { TabType } from '../types';
import { 
  BookOpen, 
  FolderTree, 
  Bot, 
  FileCode2, 
  Database, 
  ShieldCheck, 
  Activity,
  Cpu,
  Layers
} from 'lucide-react';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'blueprint' as TabType, label: '15 Architectural Topics', icon: BookOpen },
    { id: 'folder-structure' as TabType, label: 'Production Folder Tree', icon: FolderTree },
    { id: 'langgraph-visualizer' as TabType, label: '11-Agent Simulator', icon: Bot },
    { id: 'api-contracts' as TabType, label: 'API Contracts', icon: FileCode2 },
    { id: 'database-schema' as TabType, label: 'Postgres & ChromaDB', icon: Database },
    { id: 'security-phi' as TabType, label: 'Security & PHI Sandbox', icon: ShieldCheck },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-cyan-500 rounded-xl shadow-lg shadow-indigo-500/20 text-white">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                CarePath AI
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Sprint 0 Blueprint
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Autonomous Healthcare Navigation Platform &bull; FastAPI & LangGraph Architecture
            </p>
          </div>
        </div>

        {/* System Badges */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700/60 text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>FastAPI Core: <strong className="text-emerald-400 font-semibold">Ready</strong></span>
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700/60 text-slate-300">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>LangGraph: <strong className="text-indigo-400 font-semibold">11 Agents</strong></span>
          </div>
        </div>
      </div>

      {/* Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 overflow-x-auto scrollbar-none">
        <nav className="flex space-x-1 border-t border-slate-800/80 pt-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-2.5 text-xs font-semibold rounded-t-lg transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-800 text-indigo-400 border-t-2 border-indigo-500 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
