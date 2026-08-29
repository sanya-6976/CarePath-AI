import React, { useState } from 'react';
import { API_ENDPOINTS } from '../../data/architectureData';
import { ApiEndpointSpec } from '../../types';
import { FileCode2, Send, Check, Copy, Activity } from 'lucide-react';

export const ApiContractExplorer: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpointSpec>(API_ENDPOINTS[0]);
  const [copied, setCopied] = useState(false);

  const handleCopy = (data: any) => {
    navigator.clipboard.writeText(typeof data === 'string' ? data : JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getMethodBadge = (method: string) => {
    switch (method) {
      case 'POST':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'GET':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'PUT':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'DELETE':
        return 'bg-red-500/20 text-red-300 border-red-500/40';
      default:
        return 'bg-slate-500/20 text-slate-300';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Overview Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl text-white space-y-2">
        <div className="flex items-center space-x-2">
          <FileCode2 className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-bold">FastAPI REST & SSE API Contract Explorer</h2>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          OpenAPI 3.1 specification contracts for CarePath AI endpoints. Includes payload schemas for sync REST calls, real-time Server-Sent Events (SSE), and PHI sanitization endpoints.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Endpoint List Sidebar */}
        <div className="lg:col-span-4 space-y-2 max-h-[700px] overflow-y-auto">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 mb-2">
            API Routes
          </div>
          {API_ENDPOINTS.map((endpoint, idx) => {
            const isSelected = selectedEndpoint.path === endpoint.path;
            return (
              <button
                key={idx}
                onClick={() => setSelectedEndpoint(endpoint)}
                className={`w-full text-left p-3 rounded-xl border transition-all flex items-center space-x-3 ${
                  isSelected
                    ? 'bg-indigo-600/15 border-indigo-500/80 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
                }`}
              >
                <span className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded border ${getMethodBadge(endpoint.method)}`}>
                  {endpoint.method}
                </span>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-mono font-semibold truncate">{endpoint.path}</h4>
                  <p className="text-[11px] text-slate-400 truncate">{endpoint.summary}</p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected Endpoint Contract Inspector */}
        <div className="lg:col-span-8 space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 text-slate-200">
            {/* Header */}
            <div className="border-b border-slate-800 pb-4 space-y-2">
              <div className="flex items-center space-x-3">
                <span className={`px-2.5 py-1 text-xs font-mono font-bold rounded border ${getMethodBadge(selectedEndpoint.method)}`}>
                  {selectedEndpoint.method}
                </span>
                <span className="text-sm font-mono font-bold text-white">{selectedEndpoint.path}</span>
                {selectedEndpoint.isStream && (
                  <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    SSE Event Stream
                  </span>
                )}
              </div>
              <h3 className="text-lg font-bold text-white">{selectedEndpoint.summary}</h3>
              <p className="text-xs text-slate-400">{selectedEndpoint.description}</p>
            </div>

            {/* Request Body if applicable */}
            {selectedEndpoint.requestBody && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Request JSON Body Schema
                  </span>
                  <button
                    onClick={() => handleCopy(selectedEndpoint.requestBody)}
                    className="flex items-center space-x-1 text-xs text-slate-400 hover:text-white"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>Copy</span>
                  </button>
                </div>
                <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto">
                  {JSON.stringify(selectedEndpoint.requestBody, null, 2)}
                </pre>
              </div>
            )}

            {/* Responses Matrix */}
            <div className="space-y-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Response Codes & Payload Contracts
              </span>
              <div className="space-y-2">
                {Object.entries(selectedEndpoint.responses).map(([code, payload]) => (
                  <div key={code} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-xs">
                      <span className={`font-mono font-bold px-2 py-0.5 rounded ${
                        code.startsWith('2') ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
                      }`}>
                        HTTP {code}
                      </span>
                    </div>
                    <pre className="p-2 rounded bg-slate-900 text-[11px] font-mono text-emerald-300 overflow-x-auto mt-2">
                      {typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
