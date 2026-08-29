import React, { useState } from 'react';
import { ShieldCheck, Lock, Eye, AlertCircle, CheckCircle2, Shield } from 'lucide-react';

export const SecurityPhiSandbox: React.FC = () => {
  const [inputText, setInputText] = useState<string>(
    "Patient Jane Smith (SSN: 987-65-4321, DOB: 03/15/1985) called from 555-867-5309 or jane.smith@hospital.org reporting severe rash. MRN: MRN884920."
  );
  const [redactedOutput, setRedactedOutput] = useState<any | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const testRedaction = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/security/redact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      });
      const data = await response.json();
      setRedactedOutput(data);
    } catch (err) {
      console.error("Redaction error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl text-white space-y-2">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          <h2 className="text-xl font-bold">Security & PHI Redaction Sandbox Laboratory</h2>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          HIPAA compliance test environment. Test how the backend PHIRedactor filter automatically strips SSNs, MRNs, phone numbers, email addresses, and dates of birth before prompts reach LangGraph agents or external Gemini models.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Panel */}
        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 text-slate-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Eye className="w-4 h-4 text-amber-400" />
              <span>Raw Unsanitized Patient Input (Pre-Filter)</span>
            </h3>
            <span className="text-[10px] uppercase font-bold text-amber-400 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30">
              Unsafe PHI
            </span>
          </div>

          <textarea
            rows={6}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:border-emerald-500 focus:outline-none"
            placeholder="Type raw text containing SSN, phone numbers, MRN..."
          />

          <button
            onClick={testRedaction}
            disabled={isProcessing}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/20 transition"
          >
            <Shield className="w-4 h-4" />
            <span>{isProcessing ? "Redacting PHI..." : "Execute PHI Sanitization Pipeline"}</span>
          </button>
        </div>

        {/* Output Panel */}
        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 text-slate-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span>Sanitized Output (Safe for LangGraph & Gemini API)</span>
            </h3>
            {redactedOutput && (
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${
                redactedOutput.phi_detected
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-800 text-slate-400'
              }`}>
                {redactedOutput.phi_detected ? "PHI Scrubbed" : "No PHI Found"}
              </span>
            )}
          </div>

          {redactedOutput ? (
            <div className="space-y-4">
              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                {redactedOutput.redacted_text}
              </pre>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="text-slate-400 block font-medium">Audit Cryptographic Hash</span>
                  <span className="font-mono text-cyan-400 font-bold block truncate">{redactedOutput.audit_hash}</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="text-slate-400 block font-medium">Sanitization Status</span>
                  <span className="font-bold text-emerald-400 flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Safe for Agent Execution</span>
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center rounded-xl bg-slate-950/60 border border-slate-800 text-slate-500 space-y-2">
              <ShieldCheck className="w-8 h-8 text-slate-700 mx-auto" />
              <p className="text-xs">Click "Execute PHI Sanitization Pipeline" to test the redactor filter.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
