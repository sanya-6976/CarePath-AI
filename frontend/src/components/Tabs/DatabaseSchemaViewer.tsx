import React, { useState } from 'react';
import { Database, Layers, Key, Table, Cpu, FileText } from 'lucide-react';

export const DatabaseSchemaViewer: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'postgres' | 'chroma'>('postgres');

  const postgresTables = [
    {
      name: "patients",
      description: "Encrypted patient identity records, consent flags, and demographic hashes.",
      columns: [
        { name: "id", type: "VARCHAR(64)", key: "PK", desc: "SHA-256 Hashed Patient ID" },
        { name: "created_at", type: "TIMESTAMP", key: "", desc: "Registration Timestamp" },
        { name: "consent_given", type: "BOOLEAN", key: "", desc: "HIPAA Consent Flag" },
        { name: "encrypted_demographics", type: "BYTEA", key: "", desc: "AES-256 Encrypted Payload" }
      ]
    },
    {
      name: "patient_encounters",
      description: "CarePath AI navigation sessions tracking symptoms, triage urgency, and final specialist recommendation.",
      columns: [
        { name: "id", type: "VARCHAR(64)", key: "PK", desc: "Session UUID" },
        { name: "patient_id", type: "VARCHAR(64)", key: "FK", desc: "References patients(id)" },
        { name: "status", type: "VARCHAR(32)", key: "", desc: "PROCESSING, COMPLETED, EMERGENCY" },
        { name: "chief_complaint", type: "TEXT", key: "", desc: "Sanitized Symptom Description" },
        { name: "recommended_specialist", type: "VARCHAR(128)", key: "", desc: "Selected Medical Specialty" },
        { name: "triage_urgency", type: "VARCHAR(32)", key: "", desc: "EMERGENCY, URGENT, ROUTINE" },
        { name: "state_json", type: "JSONB", key: "", desc: "Final LangGraph State Snapshot" }
      ]
    },
    {
      name: "agent_checkpoints",
      description: "LangGraph state checkpointer for workflow fault tolerance and state resumption.",
      columns: [
        { name: "id", type: "VARCHAR(64)", key: "PK", desc: "Checkpoint ID" },
        { name: "encounter_id", type: "VARCHAR(64)", key: "FK", desc: "References patient_encounters(id)" },
        { name: "agent_id", type: "VARCHAR(64)", key: "", desc: "Agent Node Identifier" },
        { name: "state_delta", type: "JSONB", key: "", desc: "Incremental State Change" },
        { name: "created_at", type: "TIMESTAMP", key: "", desc: "Checkpoint Timestamp" }
      ]
    },
    {
      name: "audit_logs",
      description: "Immutable PHI access and decision audit trail for compliance verification.",
      columns: [
        { name: "id", type: "VARCHAR(64)", key: "PK", desc: "Audit Log UUID" },
        { name: "actor_id", type: "VARCHAR(64)", key: "", desc: "Patient or Agent ID" },
        { name: "action", type: "VARCHAR(64)", key: "", desc: "READ_PHI, AGENT_EXECUTE, EXPORT" },
        { name: "resource_id", type: "VARCHAR(64)", key: "", desc: "Target Record Identifier" },
        { name: "created_at", type: "TIMESTAMP", key: "", desc: "Event Time" }
      ]
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl text-white space-y-2">
        <div className="flex items-center space-x-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-bold">Hybrid Storage Schema: PostgreSQL 16 & ChromaDB Vector Store</h2>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          Relational entity relational model (ERD) for persistent clinical state and LangGraph state checkpoints, paired with ChromaDB vector collections for medical practice guidelines RAG retrieval.
        </p>
      </div>

      {/* Subtabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab('postgres')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeSubTab === 'postgres'
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Table className="w-4 h-4" />
          <span>PostgreSQL Relational Schema (4 Tables)</span>
        </button>

        <button
          onClick={() => setActiveSubTab('chroma')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeSubTab === 'chroma'
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>ChromaDB Vector Store Collection Layout</span>
        </button>
      </div>

      {/* PostgreSQL Tab Content */}
      {activeSubTab === 'postgres' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {postgresTables.map((tbl) => (
            <div key={tbl.name} className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-2">
                  <Table className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white font-mono">{tbl.name}</h3>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">{tbl.description}</p>
              </div>

              <div className="space-y-1.5">
                {tbl.columns.map((col) => (
                  <div key={col.name} className="p-2 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      {col.key && (
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          col.key === 'PK' ? 'bg-amber-500/20 text-amber-300' : 'bg-indigo-500/20 text-indigo-300'
                        }`}>
                          {col.key}
                        </span>
                      )}
                      <span className="font-bold text-slate-200">{col.name}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-cyan-400 text-[11px] block">{col.type}</span>
                      <span className="text-slate-500 text-[10px] block font-sans">{col.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* ChromaDB Vector Tab Content */
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 text-slate-200">
          <div className="border-b border-slate-800 pb-4 space-y-1">
            <h3 className="text-lg font-bold text-white">Collection Name: carepath_evidence_v1</h3>
            <p className="text-xs text-slate-400">
              ChromaDB vector collection indexed with 768-dimensional medical embeddings (Gemini text-embedding-004) for RAG guidelines retrieval.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 font-semibold block">Embedding Dimensions</span>
              <span className="text-lg font-bold text-indigo-400 font-mono">768 Float32</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 font-semibold block">Similarity Metric</span>
              <span className="text-lg font-bold text-cyan-400 font-mono">Cosine Distance</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 font-semibold block">Indexed Documents</span>
              <span className="text-lg font-bold text-emerald-400 font-mono">24,500 Guidelines</span>
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Vector Document Metadata Schema</span>
            <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300">
{`{
  "doc_id": "guideline_acr_2024_rheum_001",
  "text": "Patients presenting with symmetric polyarthritis, morning stiffness > 60 mins, and positive ANA warrant prompt Rheumatology referral within 2 weeks.",
  "metadata": {
    "specialty": "Rheumatology",
    "guideline_source": "American College of Rheumatology 2024",
    "evidence_grade": "Class I (Level A)",
    "publication_year": 2024,
    "icd10_codes": ["M06.9", "M35.9"]
  }
}`}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
