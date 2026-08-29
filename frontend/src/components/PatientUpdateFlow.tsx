import React, { useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { Send, FileText, Pill, Activity, ChevronDown, ChevronUp, Stethoscope, Image as ImageIcon, Loader2 } from 'lucide-react';

export const PatientUpdateFlow: React.FC = () => {
    const { patient } = usePatient();
    const [updateType, setUpdateType] = useState('symptom');
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [statusText, setStatusText] = useState('');

    const options = [
        { id: 'symptom', label: 'Symptoms', icon: <Activity size={14} /> },
        { id: 'treatment', label: 'Treatment', icon: <Pill size={14} /> },
        { id: 'doctor', label: 'Doctor Visit', icon: <Stethoscope size={14} /> },
        { id: 'document', label: 'New Document', icon: <FileText size={14} /> },
        { id: 'image', label: 'New Image', icon: <ImageIcon size={14} /> },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim() || !patient?.id) return;
        
        setIsSubmitting(true);
        setStatusText('Saving your update...');
        
        try {
            // Send update to the new custom medical router
            const res = await fetch('http://localhost:8000/api/v1/medical/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patient_id: patient.id === 'demo_patient_id' ? '821d5ad3-e9a7-4c1a-88c8-fb19c8d61f8e' : patient.id, // Demo fallback
                    update_type: updateType,
                    content
                })
            });
            
            if (res.ok) {
                setStatusText('Updating your timeline...');
                await new Promise(r => setTimeout(r, 600)); // Visual spacing for polished feel
                
                setStatusText('Analyzing patient context & running AI agents...');
                
                // Trigger an analysis
                await fetch('http://localhost:8000/api/v1/medical/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        patient_id: patient.id === 'demo_patient_id' ? '821d5ad3-e9a7-4c1a-88c8-fb19c8d61f8e' : patient.id
                    })
                });
                
                setStatusText('Your CarePath has been updated.');
                setTimeout(() => {
                    setContent('');
                    setStatusText('');
                    setIsOpen(false);
                    window.location.reload(); // Refresh to show new state
                }, 1500);
            } else {
                setStatusText('CarePath couldn\'t update your analysis right now.');
            }
        } catch (error) {
            console.error('Error submitting update:', error);
            setStatusText('CarePath couldn\'t update your analysis right now.');
        } finally {
            if (statusText === 'CarePath couldn\'t update your analysis right now.') {
                setIsSubmitting(false);
            }
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-brand-slate/10 p-6 mt-6 mb-6">
            {!isOpen ? (
                <div 
                    className="flex justify-between items-center cursor-pointer group" 
                    onClick={() => setIsOpen(true)}
                >
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-brand-plum text-white rounded-xl flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                            <Activity className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-brand-plum group-hover:text-brand-lavender transition-colors">
                                + Update My Condition
                            </h3>
                            <p className="text-xs text-brand-slate mt-1">CarePath remembers your history. Add new symptoms or updates here.</p>
                        </div>
                    </div>
                    <ChevronDown size={20} className="text-brand-slate opacity-50 group-hover:opacity-100 transition-opacity" />
                </div>
            ) : (
                <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex justify-between items-center mb-5 cursor-pointer" onClick={() => !isSubmitting && setIsOpen(false)}>
                        <h3 className="text-sm font-bold text-brand-plum flex items-center gap-2">
                            What has changed?
                        </h3>
                        {!isSubmitting && <ChevronUp size={20} className="text-brand-slate hover:text-brand-plum transition-colors" />}
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="flex flex-wrap gap-2 mb-4">
                            {options.map(opt => (
                                <button 
                                    key={opt.id}
                                    type="button" 
                                    onClick={() => setUpdateType(opt.id)} 
                                    disabled={isSubmitting}
                                    className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                                        updateType === opt.id 
                                        ? 'bg-brand-lavender text-white shadow-sm border border-brand-lavender' 
                                        : 'bg-white border border-brand-slate/15 text-brand-slate hover:border-brand-lavender/50 hover:bg-brand-bg disabled:opacity-50'
                                    }`}
                                >
                                    {opt.icon} {opt.label}
                                </button>
                            ))}
                        </div>

                        <div className="relative">
                            <textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="Describe what changed... (e.g. My rash has become worse after using the cream for 7 days.)"
                                className="w-full border border-brand-slate/15 bg-brand-bg rounded-xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-brand-lavender/30 focus:border-brand-lavender/50 focus:bg-white resize-none min-h-[120px] transition-all text-brand-plum placeholder:text-brand-slate/60"
                                disabled={isSubmitting}
                            />
                        </div>

                        {statusText && (
                            <div className="mt-4 p-4 rounded-xl bg-brand-lavender-light border border-brand-lavender/20 flex items-center gap-3 animate-in fade-in duration-300">
                                {isSubmitting ? (
                                    <Loader2 className="w-4 h-4 text-brand-lavender animate-spin" />
                                ) : (
                                    <Activity className="w-4 h-4 text-brand-lavender" />
                                )}
                                <span className="text-xs font-semibold text-brand-plum">
                                    {statusText}
                                </span>
                            </div>
                        )}

                        <div className="flex justify-end mt-4">
                            <button 
                                type="submit" 
                                disabled={!content.trim() || isSubmitting}
                                className="bg-brand-plum text-white px-6 py-3 rounded-xl text-xs font-bold flex items-center gap-2 hover:bg-brand-lavender transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                            >
                                {isSubmitting ? 'Updating...' : 'Update My CarePath'}
                                {!isSubmitting && <Send size={14} />}
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
};
