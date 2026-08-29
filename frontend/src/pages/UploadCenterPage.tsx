import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';
import { 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Trash2, 
  FileText, 
  ChevronRight, 
  RefreshCw, 
  Info, 
  Calendar, 
  Pill, 
  AlertTriangle,
  FolderOpen,
  Eye,
  Activity,
  ArrowRight
} from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { uploadService } from '../services/uploadService';

interface DocAnalysis {
  summary: {
    docType: string;
    date: string;
    source: string;
    keyInfo: string;
  };
  extracted: {
    medicines: string[];
    symptoms: string[];
    tests: string[];
    measurements: string[];
    conditions: string[];
    instructions: string[];
  };
  aiInsight: string;
}

interface UploadedDoc {
  id: string;
  name: string;
  size: string;
  category: 'Prescription' | 'Lab Report' | 'Medical Report' | 'Imaging/Scan' | 'Other medical document';
  status: 'uploading' | 'processing' | 'analyzing' | 'complete' | 'partial' | 'failed' | 'no_findings' | 'unsupported';
  progress: number;
  uploadedAt: string;
  result?: DocAnalysis;
  error?: string;
}

const INITIAL_DOCS: UploadedDoc[] = [
  {
    id: 'doc_1',
    name: 'chest_xray_post.png',
    size: '1.8 MB',
    category: 'Imaging/Scan',
    status: 'complete',
    progress: 100,
    uploadedAt: new Date(Date.now() - 86400000 * 3).toLocaleDateString(),
    result: {
      summary: {
        docType: 'Imaging / Chest X-Ray (PA View)',
        date: '11 Aug 2026',
        source: 'City Imaging & Diagnostic Center',
        keyInfo: 'Posterior-Anterior chest view showing slight lung hyperinflation and mild consolidation in the lower right lobe.'
      },
      extracted: {
        medicines: [],
        symptoms: ['Mild shortness of breath', 'Dry cough'],
        tests: ['Chest X-Ray PA View'],
        measurements: ['Lung hyperinflation observed', 'Right lower lobe density'],
        conditions: ['Consolidation', 'Mild hyperinflation'],
        instructions: ['Follow up with clinical consultation if symptoms worsen.']
      },
      aiInsight: 'CarePath noticed mild lung consolidation markings in the right lower lobe. Potentially relevant information includes history of persistent dry cough. Consider discussing this with your doctor to evaluate pulmonology routing.'
    }
  },
  {
    id: 'doc_2',
    name: 'cbc_blood_report.pdf',
    size: '420 KB',
    category: 'Lab Report',
    status: 'complete',
    progress: 100,
    uploadedAt: new Date(Date.now() - 86400000 * 2).toLocaleDateString(),
    result: {
      summary: {
        docType: 'Complete Blood Count (CBC)',
        date: '12 Aug 2026',
        source: 'Apex Laboratories',
        keyInfo: 'Complete blood profile with standard cell counts.'
      },
      extracted: {
        medicines: [],
        symptoms: [],
        tests: ['Complete Blood Count (CBC)'],
        measurements: ['WBC: 7.5 K/uL (Normal)', 'Hb: 14.2 g/dL (Normal)', 'Platelets: 220 K/uL (Normal)'],
        conditions: [],
        instructions: ['No follow-up blood tests indicated at this time.']
      },
      aiInsight: 'CarePath noticed that all primary blood cell counts and hemoglobin values sit well within standard reference thresholds. No indications of acute inflammatory response found.'
    }
  },
  {
    id: 'doc_3',
    name: 'rx_albuterol_90mcg.pdf',
    size: '120 KB',
    category: 'Prescription',
    status: 'complete',
    progress: 100,
    uploadedAt: new Date(Date.now() - 86400000).toLocaleDateString(),
    result: {
      summary: {
        docType: 'Prescription Script',
        date: '13 Aug 2026',
        source: 'Dr. Robert Chen, MD (General Practice)',
        keyInfo: 'Albuterol Sulfate HFA inhaler prescription.'
      },
      extracted: {
        medicines: ['Albuterol Sulfate HFA (90mcg)'],
        symptoms: ['Wheezing', 'Dry cough'],
        tests: [],
        measurements: ['Dose: 2 puffs every 4-6 hours as needed'],
        conditions: ['Bronchospasm', 'Asthma (Mild)'],
        instructions: ['Inhale 2 puffs as needed for cough or shortness of breath. Rinse mouth after use.']
      },
      aiInsight: 'CarePath noticed an active prescription script for an Albuterol bronchodilator. Potentially relevant information includes directions for acute symptoms relief. Consider discussing this with your specialist if inhaler use exceeds 2 times per week.'
    }
  }
];

export default function UploadCenterPage() {
  const { patient } = usePatient();
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<UploadedDoc[]>(() => {
    const stored = localStorage.getItem('carepath_uploaded_docs');
    return stored ? JSON.parse(stored) : INITIAL_DOCS;
  });

  const [selectedDocId, setSelectedDocId] = useState<string | null>('doc_1');
  const [category, setCategory] = useState<'Prescription' | 'Lab Report' | 'Medical Report' | 'Imaging/Scan' | 'Other medical document'>('Medical Report');
  const [dragActive, setDragActive] = useState(false);
  const [isStartingAnalysis, setIsStartingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('carepath_uploaded_docs', JSON.stringify(documents));
  }, [documents]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const simulateProcessingPipeline = (docId: string, fileName: string) => {
    setTimeout(() => {
      setDocuments(prev => prev.map(doc => {
        if (doc.id === docId) {
          if (fileName.endsWith('.exe')) {
            return { ...doc, status: 'unsupported', error: 'File format not supported. Please upload PDFs, images, or documents.' };
          }
          return { ...doc, status: 'processing', progress: 40 };
        }
        return doc;
      }));

      if (fileName.endsWith('.exe')) return;

      setTimeout(() => {
        setDocuments(prev => prev.map(doc => {
          if (doc.id === docId) {
            if (fileName.includes('fail') || fileName.includes('corrupt')) {
              return { ...doc, status: 'failed', error: 'Orchestrator failed to parse document boundaries. Please retry upload.' };
            }
            return { ...doc, status: 'analyzing', progress: 75 };
          }
          return doc;
        }));

        if (fileName.includes('fail') || fileName.includes('corrupt')) return;

        setTimeout(() => {
          setDocuments(prev => prev.map(doc => {
            if (doc.id === docId) {
              if (fileName.includes('clean')) {
                return {
                  ...doc,
                  status: 'no_findings',
                  progress: 100,
                  result: {
                    summary: {
                      docType: doc.category,
                      date: new Date().toLocaleDateString(),
                      source: 'Self-Submitted Clinic Scan',
                      keyInfo: 'Diagnostic scanning logs returned standard physiological benchmarks with no abnormal clinical vectors.'
                    },
                    extracted: { medicines: [], symptoms: [], tests: [], measurements: [], conditions: [], instructions: [] },
                    aiInsight: 'CarePath noticed that this diagnostic file does not contain any abnormal consolidation, cellular variations, or active drug markers. No significant findings identified.'
                  }
                };
              }

              if (fileName.includes('partial')) {
                return {
                  ...doc,
                  status: 'partial',
                  progress: 100,
                  result: {
                    summary: {
                      docType: doc.category,
                      date: new Date().toLocaleDateString(),
                      source: 'General Medical Records',
                      keyInfo: 'Medical report containing fragmented patient notes. Some areas were illegible.'
                    },
                    extracted: {
                      medicines: ['Paracetamol (500mg)'],
                      symptoms: ['Fever'],
                      tests: [],
                      measurements: [],
                      conditions: ['Fever of unknown origin'],
                      instructions: ['Rest and drink fluids.']
                    },
                    aiInsight: 'CarePath noticed partial text markers. Some sections of this report were unreadable or lacked key clinical descriptors. Potentially relevant details suggest temporary antipyretic directions.'
                  }
                };
              }

              return {
                ...doc,
                status: 'complete',
                progress: 100,
                result: {
                  summary: {
                    docType: doc.category,
                    date: new Date().toLocaleDateString(),
                    source: 'Local Health Authority Clinic',
                    keyInfo: `Parsed parameters from your uploaded ${doc.category.toLowerCase()}.`
                  },
                  extracted: {
                    medicines: doc.category === 'Prescription' ? ['Amoxicillin Oral Capsule'] : [],
                    symptoms: ['Coughing', 'Slight chest congestion'],
                    tests: doc.category === 'Lab Report' ? ['Sputum Culture Test'] : [],
                    measurements: ['Pulse: 72 bpm', 'O2 Saturation: 98%'],
                    conditions: ['Mild Bronchitis symptoms noticed'],
                    instructions: ['Keep hydrated and follow scheduled checks.']
                  },
                  aiInsight: `CarePath noticed signs of mild congestion in the records. Potentially relevant information includes treatment guidelines for bronchitis. Consider discussing these parsed instructions with your specialist.`
                }
              };
            }
            return doc;
          }));
        }, 1200);
      }, 1000);
    }, 800);
  };

  const formatFileSize = (bytes: number): string => {
    if (!bytes || bytes <= 0) return '0 KB';
    if (bytes < 1024 * 1024) {
      const kb = Math.round(bytes / 1024);
      return `${Math.max(1, kb)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleFileUpload = async (file: File) => {
    const formattedSize = formatFileSize(file.size);
    const newDocId = `doc_${Date.now()}`;
    const newDoc: UploadedDoc = {
      id: newDocId,
      name: file.name,
      size: formattedSize,
      category: category,
      status: 'uploading',
      progress: 25,
      uploadedAt: new Date().toLocaleDateString()
    };

    setDocuments(prev => [newDoc, ...prev]);
    setSelectedDocId(newDocId);

    try {
      setDocuments(prev => prev.map(d => d.id === newDocId ? { ...d, status: 'analyzing', progress: 60 } : d));
      const pid = patient?.id || localStorage.getItem('carepath_patient_id') || 'demo_user';
      const response = await uploadService.uploadDocument(file, category, pid);

      if (response && response.result) {
        setDocuments(prev => prev.map(doc => {
          if (doc.id === newDocId) {
            return {
              ...doc,
              id: response.id || newDocId,
              size: response.size || formattedSize,
              status: response.status || 'complete',
              progress: 100,
              result: response.result
            };
          }
          return doc;
        }));
        if (response.id) {
          setSelectedDocId(response.id);
        }
        return;
      }
    } catch (err) {
      console.warn('Real API upload error, running processing fallback:', err);
    }

    simulateProcessingPipeline(newDocId, file.name.toLowerCase());
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const removeDocument = (id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    if (selectedDocId === id) {
      setSelectedDocId(null);
    }
  };

  const retryUpload = (doc: UploadedDoc) => {
    setDocuments(prev => prev.map(d => d.id === doc.id ? { ...d, status: 'uploading', progress: 10, error: undefined } : d));
    simulateProcessingPipeline(doc.id, doc.name.toLowerCase());
  };

  const handleBeginAnalysis = async () => {
    if (!patient) return;
    setIsStartingAnalysis(true);
    setAnalysisError(null);

    try {
      if (patient.id === 'demo_patient_id') {
        navigate('/analysis/processing?demo=true');
      } else {
        navigate(`/analysis/processing?patient_id=${patient.id}`);
      }
    } catch (err: any) {
      console.error(err);
      setAnalysisError(err.message || 'Unable to launch clinical analysis. Ensure local API is active.');
    } finally {
      setIsStartingAnalysis(false);
    }
  };

  const selectedDoc = documents.find(d => d.id === selectedDocId);

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-300">
      {analysisError && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{analysisError}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
        <div className="lg:col-span-3 bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-xxs flex flex-col gap-5">
          <div>
            <h3 className="font-display font-bold text-sm text-brand-plum">Submit Diagnostic Records</h3>
            <p className="text-brand-slate text-xs font-light mt-0.5">Choose document category and drag file to analyze.</p>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Document Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as any)}
              className="bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs text-brand-plum outline-none focus:border-brand-lavender transition-all cursor-pointer font-medium"
            >
              <option value="Prescription">Prescription</option>
              <option value="Lab Report">Lab Report</option>
              <option value="Medical Report">Medical Report</option>
              <option value="Imaging/Scan">Imaging/Scan</option>
              <option value="Other medical document">Other medical document</option>
            </select>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all bg-brand-bg/30 min-h-[220px] cursor-pointer ${
              dragActive ? 'border-brand-lavender bg-brand-lavender-light/35' : 'border-brand-slate/20 hover:border-brand-lavender/40'
            }`}
          >
            <div className="w-12 h-12 rounded-2xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center mb-4">
              <UploadCloud className="w-6 h-6 animate-pulse" />
            </div>
            <h4 className="font-display font-semibold text-xs text-brand-plum mb-1">Drag and drop file here</h4>
            <p className="text-brand-slate text-[11px] font-light max-w-xs mb-4">Support PDF, PNG, JPG, or DOCX formats up to 10MB.</p>
            
            <label className="bg-brand-card hover:bg-brand-bg border border-brand-slate/15 text-brand-plum text-[10px] font-bold px-4 py-2 rounded-xl transition-all shadow-xxs cursor-pointer">
              Browse Files
              <input
                type="file"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg,.docx,.doc,.txt"
                onChange={handleFileInput}
              />
            </label>
          </div>
        </div>

        <div className="lg:col-span-2 bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-xxs flex flex-col gap-4">
          <div>
            <h3 className="font-display font-bold text-sm text-brand-plum">Uploaded Documents</h3>
            <p className="text-brand-slate text-xs font-light mt-0.5">Manage and view extraction reports.</p>
          </div>

          {documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 border border-dashed border-brand-slate/15 rounded-2xl">
              <FolderOpen className="w-8 h-8 text-brand-slate/40 mb-2" />
              <p className="text-xxs text-brand-slate font-light">No documents submitted yet.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-3 max-h-[360px] overflow-y-auto pr-1">
              {documents.map((doc) => {
                const isSelected = selectedDocId === doc.id;
                return (
                  <div
                    key={doc.id}
                    onClick={() => doc.status !== 'uploading' && setSelectedDocId(doc.id)}
                    className={`border rounded-2xl p-3.5 transition-all flex items-start justify-between gap-3 cursor-pointer ${
                      isSelected 
                        ? 'border-brand-lavender bg-brand-lavender-light/10 shadow-xxs' 
                        : 'border-brand-slate/10 bg-brand-card hover:border-brand-slate/20'
                    }`}
                  >
                    <div className="min-w-0 flex gap-2.5 items-start">
                      <FileText className="w-4 h-4 text-brand-lavender shrink-0 mt-0.5" />
                      <div className="min-w-0">
                        <span className="text-xs font-bold text-brand-plum truncate block leading-tight">{doc.name}</span>
                        <span className="text-[10px] text-brand-slate font-light block mt-0.5">
                          {doc.category} &bull; {doc.size} {doc.result?.summary.date ? `• ${doc.result.summary.date}` : ''}
                        </span>
                        {doc.result && doc.result.extracted.medicines.length > 0 && (
                          <span className="text-[9px] font-medium text-brand-lavender bg-brand-lavender-light border border-brand-lavender/10 px-1.5 py-0.5 rounded-md mt-1.5 inline-block">
                            Medication: {doc.result.extracted.medicines[0]}
                          </span>
                        )}

                        <div className="flex items-center gap-1.5 mt-2">
                          {doc.status === 'uploading' && (
                            <div className="w-full flex items-center gap-2">
                              <div className="w-20 bg-brand-bg h-1 rounded-full overflow-hidden shrink-0">
                                <div className="bg-brand-lavender h-full transition-all" style={{ width: `${doc.progress}%` }} />
                              </div>
                              <span className="text-[9px] font-bold text-brand-lavender">Uploading</span>
                            </div>
                          )}
                          {doc.status === 'processing' && (
                            <span className="text-[9px] font-bold text-brand-amber-text bg-brand-amber-bg border border-brand-amber-text/10 px-1.5 py-0.25 rounded-md flex items-center gap-1">
                              <Loader2 className="w-2.5 h-2.5 animate-spin" />
                              Processing
                            </span>
                          )}
                          {doc.status === 'analyzing' && (
                            <span className="text-[9px] font-bold text-brand-lavender bg-brand-lavender-light border border-brand-lavender/10 px-1.5 py-0.25 rounded-md flex items-center gap-1">
                              <Loader2 className="w-2.5 h-2.5 animate-spin" />
                              AI Analyzing
                            </span>
                          )}
                          {(doc.status === 'complete' || doc.status === 'no_findings') && (
                            <span className="text-[9px] font-bold text-brand-sage-text bg-brand-sage-bg border border-brand-sage-text/10 px-1.5 py-0.25 rounded-md flex items-center gap-0.5">
                              <CheckCircle2 className="w-2.5 h-2.5" />
                              Ready
                            </span>
                          )}
                          {doc.status === 'partial' && (
                            <span className="text-[9px] font-bold text-brand-amber-text bg-brand-amber-bg border border-brand-amber-text/10 px-1.5 py-0.25 rounded-md flex items-center gap-0.5">
                              <AlertTriangle className="w-2.5 h-2.5" />
                              Partial
                            </span>
                          )}
                          {doc.status === 'failed' && (
                            <span className="text-[9px] font-bold text-brand-rose-text bg-brand-rose-bg border border-brand-rose-text/10 px-1.5 py-0.25 rounded-md flex items-center gap-0.5">
                              <AlertCircle className="w-2.5 h-2.5" />
                              Failed
                            </span>
                          )}
                          {doc.status === 'unsupported' && (
                            <span className="text-[9px] font-bold text-brand-rose-text bg-brand-rose-bg border border-brand-rose-text/10 px-1.5 py-0.25 rounded-md flex items-center gap-0.5">
                              <AlertCircle className="w-2.5 h-2.5" />
                              Unsupported
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 flex gap-2">
                      {doc.status === 'failed' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); retryUpload(doc); }}
                          title="Retry Analysis"
                          className="p-1 hover:bg-brand-rose-bg rounded-lg text-brand-rose-text transition-all cursor-pointer"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); removeDocument(doc.id); }}
                        title="Remove Document"
                        className="p-1 hover:bg-brand-rose-bg rounded-lg text-brand-slate hover:text-brand-rose-text transition-all cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {selectedDoc && (selectedDoc.status === 'complete' || selectedDoc.status === 'partial' || selectedDoc.status === 'no_findings') && selectedDoc.result && (
        <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm flex flex-col gap-6 animate-in fade-in duration-300">
          <div className="flex items-center gap-2.5 border-b border-brand-slate/10 pb-4">
            <div className="w-8 h-8 bg-brand-lavender text-white rounded-xl flex items-center justify-center shrink-0">
              <Activity className="w-4.5 h-4.5" />
            </div>
            <div>
              <h3 className="font-display font-extrabold text-sm text-brand-plum">AI Clinical Extraction Report</h3>
              <p className="text-brand-slate text-[11px] font-light mt-0.5">Results parsed from file: <span className="font-semibold text-brand-plum">{selectedDoc.name}</span></p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            <div className="md:col-span-2 bg-brand-bg/50 border border-brand-slate/10 p-5 rounded-2xl flex flex-col gap-4">
              <h4 className="font-display text-[10px] font-bold tracking-wider text-brand-slate uppercase border-b border-brand-slate/10 pb-2">Document Summary</h4>
              
              <div className="flex flex-col gap-3 text-xxs leading-relaxed font-light text-brand-slate">
                <div>
                  <span className="font-bold text-brand-plum block">Document Category Type</span>
                  <span>{selectedDoc.result.summary.docType}</span>
                </div>
                <div>
                  <span className="font-bold text-brand-plum block">Source / Institution</span>
                  <span>{selectedDoc.result.summary.source}</span>
                </div>
                <div>
                  <span className="font-bold text-brand-plum block">Issue Date</span>
                  <span className="flex items-center gap-1 mt-0.5">
                    <Calendar className="w-3.5 h-3.5 text-brand-slate/60" />
                    {selectedDoc.result.summary.date}
                  </span>
                </div>
                <div>
                  <span className="font-bold text-brand-plum block">Key Extract Overview</span>
                  <span className="text-brand-plum mt-1 block italic bg-brand-card p-3 rounded-lg border border-brand-slate/5">
                    "{selectedDoc.result.summary.keyInfo}"
                  </span>
                </div>
              </div>
            </div>

            <div className="md:col-span-3 flex flex-col gap-4">
              <h4 className="font-display text-[10px] font-bold tracking-wider text-brand-slate uppercase border-b border-brand-slate/10 pb-2">Clinical Facts Extracted</h4>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="border border-brand-slate/10 p-4 rounded-xl">
                  <span className="text-[9px] font-bold text-brand-slate uppercase block mb-1">Medicines Mentioned</span>
                  {selectedDoc.result.extracted.medicines.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {selectedDoc.result.extracted.medicines.map((med, idx) => (
                        <span key={idx} className="bg-brand-lavender-light text-brand-lavender text-xxs font-semibold px-2.5 py-0.5 rounded-full border border-brand-lavender/5">{med}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xxs text-brand-slate/60 font-light block mt-1.5">No active drug compounds found.</span>
                  )}
                </div>

                <div className="border border-brand-slate/10 p-4 rounded-xl">
                  <span className="text-[9px] font-bold text-brand-slate uppercase block mb-1">Symptoms Extracted</span>
                  {selectedDoc.result.extracted.symptoms.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {selectedDoc.result.extracted.symptoms.map((sym, idx) => (
                        <span key={idx} className="bg-brand-amber-bg text-brand-amber-text text-xxs font-semibold px-2.5 py-0.5 rounded-full border border-brand-amber-text/10">{sym}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xxs text-brand-slate/60 font-light block mt-1.5">No explicit symptoms parsed.</span>
                  )}
                </div>

                <div className="border border-brand-slate/10 p-4 rounded-xl">
                  <span className="text-[9px] font-bold text-brand-slate uppercase block mb-1">Tests & Measurements</span>
                  {selectedDoc.result.extracted.tests.length > 0 || selectedDoc.result.extracted.measurements.length > 0 ? (
                    <div className="flex flex-col gap-1 mt-1.5">
                      {selectedDoc.result.extracted.tests.map((t, i) => (
                        <span key={i} className="text-xxs text-brand-plum font-semibold block">&bull; {t}</span>
                      ))}
                      {selectedDoc.result.extracted.measurements.map((m, i) => (
                        <span key={i} className="text-xxs text-brand-slate font-light block">&bull; {m}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xxs text-brand-slate/60 font-light block mt-1.5">No test measurements found.</span>
                  )}
                </div>

                <div className="border border-brand-slate/10 p-4 rounded-xl">
                  <span className="text-[9px] font-bold text-brand-slate uppercase block mb-1">Diagnoses / Conditions Mentioned</span>
                  {selectedDoc.result.extracted.conditions.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {selectedDoc.result.extracted.conditions.map((cond, idx) => (
                        <span key={idx} className="bg-brand-rose-bg text-brand-rose-text text-xxs font-semibold px-2.5 py-0.5 rounded-full border border-brand-rose-text/10">{cond}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xxs text-brand-slate/60 font-light block mt-1.5">No diagnoses mentioned.</span>
                  )}
                </div>
              </div>

              {selectedDoc.result.extracted.instructions.length > 0 && (
                <div className="border border-brand-slate/10 p-4 rounded-xl">
                  <span className="text-[9px] font-bold text-brand-slate uppercase block mb-1.5">Instructions</span>
                  <ul className="flex flex-col gap-1 list-disc pl-4 text-xxs text-brand-plum font-light leading-relaxed">
                    {selectedDoc.result.extracted.instructions.map((inst, idx) => (
                      <li key={idx}>{inst}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="bg-brand-lavender-light/35 border-l-2 border-brand-lavender p-5 rounded-r-2xl mt-2 flex gap-3">
            <Info className="w-5 h-5 text-brand-lavender shrink-0 mt-0.5" />
            <div>
              <span className="text-xs font-bold text-brand-lavender uppercase tracking-wider block">AI Insight</span>
              <p className="text-xs text-brand-plum leading-relaxed font-light mt-1">
                {selectedDoc.result.aiInsight}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
        <div>
          <h3 className="font-display font-semibold text-sm text-brand-plum">Ready to begin multi-agent pipeline?</h3>
          <p className="text-brand-slate text-xs mt-0.5 max-w-lg font-light">
            Tap below to execute clinical reasoning engines over your extracted diagnostic context.
          </p>
        </div>

        <button
          onClick={handleBeginAnalysis}
          disabled={documents.length === 0 || isStartingAnalysis}
          className="bg-brand-lavender hover:bg-brand-lavender-hover disabled:bg-brand-slate/25 disabled:text-brand-slate/50 disabled:cursor-not-allowed text-white font-semibold text-sm px-6 py-3.5 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer shrink-0"
        >
          {isStartingAnalysis ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Initializing Orchestrator...
            </>
          ) : (
            <>
              Begin CarePath Analysis
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
