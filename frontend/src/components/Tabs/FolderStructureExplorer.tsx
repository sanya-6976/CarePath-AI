import React, { useState } from 'react';
import { PRODUCTION_FOLDER_TREE } from '../../data/architectureData';
import { FolderNode } from '../../types';
import { Folder, FileCode, ChevronRight, ChevronDown, Terminal, Code2, Copy, Check } from 'lucide-react';

export const FolderStructureExplorer: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<FolderNode>(
    PRODUCTION_FOLDER_TREE.children?.[0]?.children?.[0]?.children?.[0]?.children?.[0] || PRODUCTION_FOLDER_TREE
  );
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(
    new Set(['carepath-backend', 'app', 'app/api', 'app/api/v1', 'app/api/v1/endpoints', 'app/agents', 'app/core', 'app/db'])
  );
  const [copied, setCopied] = useState(false);

  const toggleExpand = (path: string) => {
    const next = new Set(expandedPaths);
    if (next.has(path)) {
      next.delete(path);
    } else {
      next.add(path);
    }
    setExpandedPaths(next);
  };

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderTree = (node: FolderNode, level: number = 0) => {
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedNode.path === node.path;
    const isFolder = node.type === 'folder';

    return (
      <div key={node.path} className="select-none">
        <div
          onClick={() => {
            if (isFolder) {
              toggleExpand(node.path);
            }
            setSelectedNode(node);
          }}
          style={{ paddingLeft: `${level * 16 + 12}px` }}
          className={`flex items-center space-x-2 py-1.5 pr-3 text-xs font-mono rounded-lg cursor-pointer transition-colors ${
            isSelected
              ? 'bg-indigo-600/20 text-indigo-300 font-semibold border-l-2 border-indigo-500'
              : 'text-slate-300 hover:bg-slate-800/60'
          }`}
        >
          {isFolder ? (
            <>
              {isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              )}
              <Folder className="w-4 h-4 text-indigo-400 shrink-0" />
            </>
          ) : (
            <>
              <span className="w-3.5 h-3.5 shrink-0" />
              <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
            </>
          )}
          <span className="truncate">{node.name}</span>
          {node.layer && (
            <span className="ml-auto text-[10px] uppercase font-sans font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {node.layer}
            </span>
          )}
        </div>

        {isFolder && isExpanded && node.children && (
          <div>{node.children.map((child) => renderTree(child, level + 1))}</div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Overview Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl text-white space-y-2">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-bold">Production Folder Directory Structure</h2>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          Clean Architecture layout for the FastAPI & LangGraph backend. Navigating through nodes displays clean code blueprints, layer metadata, and responsibility explanations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Tree Sidebar */}
        <div className="lg:col-span-5 p-4 rounded-2xl bg-slate-900 border border-slate-800 max-h-[700px] overflow-y-auto">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-2">
            Backend Repository Tree
          </div>
          {renderTree(PRODUCTION_FOLDER_TREE)}
        </div>

        {/* File Inspector Panel */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 text-slate-200">
            {/* Header Details */}
            <div className="flex items-start justify-between border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-indigo-400">
                    {selectedNode.path}
                  </span>
                  {selectedNode.layer && (
                    <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      Layer: {selectedNode.layer}
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-white mt-1">{selectedNode.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{selectedNode.description || 'Module component'}</p>
              </div>

              {selectedNode.codeSnippet && (
                <button
                  onClick={() => handleCopy(selectedNode.codeSnippet!)}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Code'}</span>
                </button>
              )}
            </div>

            {/* Code Snippet View */}
            {selectedNode.codeSnippet ? (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
                  <Code2 className="w-4 h-4 text-cyan-400" />
                  <span>Draft Python / FastAPI Implementation Template</span>
                </div>
                <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto max-h-[480px] leading-relaxed">
                  {selectedNode.codeSnippet}
                </pre>
              </div>
            ) : (
              <div className="p-8 text-center rounded-xl bg-slate-950/60 border border-slate-800/80 text-slate-400 space-y-2">
                <Folder className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs">Directory containing child submodules and architectural files.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
