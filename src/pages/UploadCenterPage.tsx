import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadService } from '../services/uploadService';
import { analysisService } from '../services/analysisService';
import { usePatient } from '../context/PatientContext';
import { 
  FileText, 
  Image as ImageIcon, 
  Clipboard, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  ArrowRight,
  RefreshCw 
} from 'lucide-react';

interface UploaderProps {
  title: string;
  description: string;
  type: 'image' | 'report' | 'prescription';
  accept: string;
  icon: React.ComponentType<any>;
  onUploadSuccess: (recordId: string) => void;
}

function FileWidget({ title, description, type, accept, icon: Icon, onUploadSuccess }: UploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const uploadFile = async (selectedFile: File) => {
    setFile(selectedFile);
    setStatus('uploading');
    setProgress(20);

    try {
      let record;
      setProgress(50);
      if (type === 'image') {
        record = await uploadService.uploadImage(selectedFile);
      } else if (type === 'report') {
        record = await uploadService.uploadReport(selectedFile);
      } else {
        record = await uploadService.uploadPrescription(selectedFile);
      }
      setProgress(100);
      setStatus('success');
      onUploadSuccess(record?.id || 'mock_rec_id');
    } catch (err: any) {
      console.error(err);
      setStatus('error');
      setErrorMessage(err.message || 'File upload failed. Ensure the local API is running.');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const resetUploader = () => {
    setFile(null);
    setProgress(0);
    setStatus('idle');
    setErrorMessage('');
  };

  return (
    <div 
      className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center transition-all bg-brand-card min-h-[220px] ${
        dragActive ? 'border-brand-lavender bg-brand-lavender-light/30' : 'border-brand-slate/20 hover:border-brand-lavender/40'
      }`}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
    >
      {status === 'idle' && (
        <>
          <div className="w-12 h-12 rounded-xl bg-brand-bg flex items-center justify-center text-brand-slate mb-4">
            <Icon className="w-6 h-6" />
          </div>
          <h3 className="font-display font-semibold text-sm text-brand-plum mb-1">{title}</h3>
          <p className="text-brand-slate text-xs mb-4 leading-relaxed max-w-xs">{description}</p>
          <label className="bg-brand-bg hover:bg-brand-slate/10 text-brand-plum text-xxs font-semibold px-4 py-2.5 rounded-lg border border-brand-slate/15 cursor-pointer transition-all">
            Choose File
            <input 
              type="file" 
              accept={accept} 
              className="hidden" 
              onChange={handleFileInput} 
            />
          </label>
          <span className="text-xxs text-brand-slate/60 mt-2">Accepted formats: {accept}</span>
        </>
      )}

      {status === 'uploading' && (
        <div className="flex flex-col items-center w-full">
          <Loader2 className="w-8 h-8 text-brand-lavender animate-spin mb-4" />
          <h4 className="text-xs font-semibold text-brand-plum mb-2">Uploading {file?.name}...</h4>
          <div className="w-full bg-brand-bg h-1.5 rounded-full overflow-hidden max-w-xs">
            <div className="bg-brand-lavender h-full transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {status === 'success' && (
        <>
          <CheckCircle className="w-10 h-10 text-brand-sage-text mb-4" />
          <h4 className="text-xs font-semibold text-brand-sage-text mb-1">Upload Successful</h4>
          <p className="text-xxs text-brand-slate max-w-xs truncate mb-4">{file?.name}</p>
          <button 
            onClick={resetUploader}
            className="text-xxs font-semibold text-brand-slate underline hover:no-underline"
          >
            Upload Another
          </button>
        </>
      )}

      {status === 'error' && (
        <>
          <AlertCircle className="w-10 h-10 text-brand-rose-text mb-4" />
          <h4 className="text-xs font-semibold text-brand-rose-text mb-1.5">Upload Failed</h4>
          <p className="text-xxs text-brand-rose-text max-w-xs mb-4 leading-relaxed">{errorMessage}</p>
          <div className="flex gap-4">
            <button 
              onClick={() => file && uploadFile(file)}
              className="flex items-center gap-1 bg-brand-rose-bg text-brand-rose-text text-xxs font-semibold px-3 py-2 rounded-lg border border-brand-rose-text/10"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
            <button 
              onClick={resetUploader}
              className="text-xxs font-semibold text-brand-slate underline hover:no-underline"
            >
              Cancel
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function UploadCenterPage() {
  const { patient } = usePatient();
  const navigate = useNavigate();
  const [uploadedRecords, setUploadedRecords] = useState<string[]>([]);
  const [isStartingAnalysis, setIsStartingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const handleUploadSuccess = (recordId: string) => {
    setUploadedRecords(prev => [...prev, recordId]);
  };

  const handleBeginAnalysis = async () => {
    if (!patient) return;
    setIsStartingAnalysis(true);
    setAnalysisError(null);

    try {
      if (patient.id === 'demo_patient_id') {
        // Direct route to results page for demo bypass
        navigate('/analysis/processing?demo=true');
      } else {
        const response = await analysisService.startAnalysis(patient.id);
        navigate(`/analysis/processing?id=${response.id}`);
      }
    } catch (err: any) {
      console.error(err);
      setAnalysisError(err.message || 'Unable to launch clinical analysis. Ensure the backend api is active.');
    } finally {
      setIsStartingAnalysis(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">

      {analysisError && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{analysisError}</span>
        </div>
      )}

      {/* Grid of upload widgets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FileWidget
          title="Medical Image"
          description="Chest X-rays, MRIs, CT scans, ultrasound files, or skin photographs."
          type="image"
          accept=".png,.jpg,.jpeg,.dcm"
          icon={ImageIcon}
          onUploadSuccess={handleUploadSuccess}
        />

        <FileWidget
          title="Medical Report"
          description="Lab work reports, blood panels, clinical letters, or pathology papers."
          type="report"
          accept=".pdf,.txt,.docx"
          icon={FileText}
          onUploadSuccess={handleUploadSuccess}
        />

        <FileWidget
          title="Prescription Script"
          description="Active medications list, pharmaceutical scripts, or dosing directions."
          type="prescription"
          accept=".png,.jpg,.pdf"
          icon={Clipboard}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>

      {/* Actions and Begin Analysis */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 mt-4">
        <div>
          <h3 className="font-display font-semibold text-sm text-brand-plum">Ready to analyze?</h3>
          <p className="text-brand-slate text-xs mt-0.5 max-w-lg">
            {uploadedRecords.length > 0
              ? `You have uploaded ${uploadedRecords.length} document(s). Tap below to send this metadata to the clinical reasoning engines.`
              : 'Add at least one medical document or photograph above to activate the CarePath multi-agent analysis.'}
          </p>
        </div>

        <button
          onClick={handleBeginAnalysis}
          disabled={uploadedRecords.length === 0 && patient?.id !== 'demo_patient_id' || isStartingAnalysis}
          className="bg-brand-lavender hover:bg-brand-lavender-hover disabled:bg-brand-slate/25 disabled:text-brand-slate/50 disabled:cursor-not-allowed text-white font-semibold text-sm px-6 py-3.5 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer shrink-0"
        >
          {isStartingAnalysis ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Initializing Engines...
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
