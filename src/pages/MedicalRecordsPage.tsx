import { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { apiClient } from '../services/apiClient';
import { 
  FolderOpen, 
  Image as ImageIcon, 
  FileText, 
  Clipboard, 
  Download, 
  AlertCircle,
  Clock,
  Trash2
} from 'lucide-react';
import type { MedicalRecord, RecordType } from '../types';

export default function MedicalRecordsPage() {
  const { patient } = usePatient();
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [activeCategory, setActiveCategory] = useState<'all' | RecordType>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecords = async () => {
    if (!patient) return;
    setIsLoading(true);
    setError(null);
    try {
      if (patient.id === 'demo_patient_id') {
        setRecords([
          {
            id: 'rec_1',
            patient_id: 'demo_patient_id',
            title: 'Chest X-Ray Posterior-Anterior',
            type: 'image',
            file_url: '#',
            file_name: 'chest_xray_post.png',
            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
            summary: 'Normal cardiac shadow, lung fields show slight hyperinflation, no consolidation or effusion.'
          },
          {
            id: 'rec_2',
            patient_id: 'demo_patient_id',
            title: 'Complete Blood Count (CBC) Panel',
            type: 'report',
            file_url: '#',
            file_name: 'cbc_blood_report.pdf',
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            summary: 'White blood cells 7.5K, Hemoglobin 14.2 g/dL, Platelets 220K. All values within normal biological ranges.'
          },
          {
            id: 'rec_3',
            patient_id: 'demo_patient_id',
            title: 'GP Albuterol Inhaler Prescription',
            type: 'prescription',
            file_url: '#',
            file_name: 'rx_albuterol_90mcg.pdf',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            summary: 'Albuterol Sulfate HFA 90mcg. 2 puffs inhaled every 4-6 hours as needed for shortness of breath or cough.'
          }
        ]);
      } else {
        const data = await apiClient.get<MedicalRecord[]>('/api/v1/records');
        setRecords(data);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch medical records. Ensure local API is active.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [patient]);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to remove this medical document?')) return;
    
    try {
      if (patient?.id === 'demo_patient_id') {
        setRecords(prev => prev.filter(r => r.id !== id));
      } else {
        await apiClient.delete(`/api/v1/records/${id}`);
        await fetchRecords();
      }
    } catch (err: any) {
      console.error(err);
      alert('Failed to delete medical record.');
    }
  };

  // Filter records based on category
  const filteredRecords = activeCategory === 'all' 
    ? records 
    : records.filter(r => r.type === activeCategory);

  const getRecordIcon = (type: RecordType) => {
    switch (type) {
      case 'image':
        return ImageIcon;
      case 'report':
        return FileText;
      case 'prescription':
        return Clipboard;
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={fetchRecords} className="text-xs font-bold underline">Retry</button>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-brand-slate/10 pb-1">
        {(['all', 'image', 'report', 'prescription'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-2.5 text-xs font-semibold capitalize rounded-t-xl transition-all border-b-2 -mb-1.5 cursor-pointer ${
              activeCategory === cat 
                ? 'border-brand-lavender text-brand-lavender font-bold' 
                : 'border-transparent text-brand-slate hover:text-brand-plum'
            }`}
          >
            {cat === 'all' ? 'All Documents' : `${cat}s`}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-lavender"></div>
        </div>
      ) : filteredRecords.length === 0 ? (
        <div className="bg-brand-card border border-brand-slate/10 p-12 rounded-2xl text-center flex flex-col items-center gap-6 my-6">
          <div className="w-14 h-14 bg-brand-bg rounded-full flex items-center justify-center text-brand-slate">
            <FolderOpen className="w-6 h-6" />
          </div>
          <div>
            <h2 className="font-display text-xl font-bold text-brand-plum mb-2">No documents found</h2>
            <p className="text-brand-slate text-xs max-w-xs leading-relaxed mx-auto">
              {activeCategory === 'all' 
                ? 'You have not uploaded any medical documents yet.' 
                : `No uploaded documents found matching category: "${activeCategory}s".`}
            </p>
          </div>
        </div>
      ) : (
        /* Records Grid Layout */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredRecords.map((rec) => {
            const Icon = getRecordIcon(rec.type);

            return (
              <div 
                key={rec.id}
                className="bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-xs hover:border-brand-lavender/35 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start gap-4 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-brand-bg text-brand-slate flex items-center justify-center shrink-0">
                        <Icon className="w-4.5 h-4.5" />
                      </div>
                      <div>
                        <h3 className="font-display font-semibold text-sm text-brand-plum max-w-[200px] truncate">
                          {rec.title}
                        </h3>
                        <span className="text-xxs text-brand-slate/75 block mt-0.5">
                          {rec.file_name}
                        </span>
                      </div>
                    </div>

                    <span className="text-xxs font-bold text-brand-slate uppercase tracking-wider bg-brand-bg px-2.5 py-1 rounded-full shrink-0">
                      {rec.type}
                    </span>
                  </div>

                  {rec.summary && (
                    <div className="bg-brand-bg/50 p-3 rounded-xl border border-brand-slate/5 text-xs text-brand-plum leading-relaxed font-light mb-4">
                      <span className="font-bold text-xxs text-brand-slate uppercase block mb-1">Extracted Summary</span>
                      "{rec.summary}"
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between border-t border-brand-slate/5 pt-3.5 mt-2">
                  <div className="flex items-center gap-1.5 text-xxs text-brand-slate">
                    <Clock className="w-3.5 h-3.5" />
                    {new Date(rec.created_at).toLocaleDateString()}
                  </div>

                  <div className="flex gap-2">
                    <a
                      href={rec.file_url}
                      download
                      className="p-2 rounded-lg bg-brand-bg hover:bg-brand-slate/10 text-brand-slate transition-all border border-brand-slate/10 flex items-center justify-center"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </a>
                    <button
                      onClick={() => handleDelete(rec.id)}
                      className="p-2 rounded-lg bg-brand-rose-bg hover:bg-brand-rose-bg/70 text-brand-rose-text transition-all border border-brand-rose-text/10 flex items-center justify-center cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
