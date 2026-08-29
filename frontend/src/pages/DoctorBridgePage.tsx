import React, { useState, useEffect } from 'react';
import { usePatient } from '../context/PatientContext';
import { useAuth } from '../context/AuthContext';
import { doctorBridgeService, DoctorQuestion, DoctorReview } from '../services/doctorBridgeService';
import { 
  FileCheck, 
  User, 
  ClipboardList, 
  CheckCircle2, 
  Brain, 
  Copy, 
  Plus, 
  Stethoscope, 
  ChevronRight, 
  RotateCcw,
  BookOpen,
  CalendarCheck,
  AlertCircle,
  Clock,
  ArrowLeft
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DoctorBridgePage() {
  const { patient } = usePatient();
  const { user } = useAuth();

  const [activeStep, setActiveStep] = useState<number>(1);
  const [questions, setQuestions] = useState<DoctorQuestion[]>([]);
  const [customQuestionText, setCustomQuestionText] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Doctor Form State (Simulation)
  const [recommendationOutcome, setRecommendationOutcome] = useState<'confirm' | 'modify'>('confirm');
  const [modifiedSpecialist, setModifiedSpecialist] = useState('Allergist / Immunologist');
  const [doctorNote, setDoctorNote] = useState(
    'Reviewed X-ray lower right lobe consolidation. Clinical symptoms correlate with mild bronchial irritation. Confirmed referral routing to pulmonologist for complete spirometry workup.'
  );
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([
    'Continue current plan',
    'Complete recommended test',
    'Follow up on specified date'
  ]);
  const [followUpDate, setFollowUpDate] = useState('2026-08-25');
  const [doctorName, setDoctorName] = useState('Dr. Robert Chen, MD');

  const [currentReview, setCurrentReview] = useState<DoctorReview | null>(null);
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);

  const loadData = () => {
    setQuestions(doctorBridgeService.getQuestions());
    
    // Read uploaded documents
    const storedDocsRaw = localStorage.getItem('carepath_uploaded_docs');
    const storedDocs = storedDocsRaw ? JSON.parse(storedDocsRaw) : [];
    setUploadedDocs(storedDocs);

    const review = doctorBridgeService.getReview();
    setCurrentReview(review);
    
    if (review) {
      // If already reviewed, default to Step 4 (Approved Feedback)
      setActiveStep(4);
      setRecommendationOutcome(review.recommendation === 'confirm' ? 'confirm' : 'modify');
      setDoctorNote(review.doctorNote);
      setSelectedRecommendations(review.doctorRecommendations);
      setFollowUpDate(review.followUpDate);
      setDoctorName(review.reviewedBy);
    } else {
      setActiveStep(1);
      if (storedDocs.length > 0) {
        const names = storedDocs.map((d: any) => d.name).join(', ');
        setDoctorNote(
          `Reviewed patient uploaded clinical documents (${names}). Extracted clinical findings and symptoms evaluated. Confirmed clinical management plan and referral routing.`
        );
      }
    }
  };

  useEffect(() => {
    loadData();

    // Listen for updates from other views (e.g. Dashboard resets)
    window.addEventListener('doctor_review_updated', loadData);
    return () => {
      window.removeEventListener('doctor_review_updated', loadData);
    };
  }, [patient]);

  const handleAddQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customQuestionText.trim()) return;
    const updated = doctorBridgeService.addQuestion(customQuestionText);
    setQuestions(updated);
    setCustomQuestionText('');
  };

  const handleToggleAsked = (id: string) => {
    const updated = doctorBridgeService.toggleQuestionAsked(id);
    setQuestions(updated);
  };

  const handleCopyQuestion = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleToggleRecommendation = (rec: string) => {
    setSelectedRecommendations(prev => 
      prev.includes(rec) ? prev.filter(r => r !== rec) : [...prev, rec]
    );
  };

  const handleSubmitDoctorReview = () => {
    const review: DoctorReview = {
      isReviewed: true,
      reviewedBy: doctorName,
      reviewedDate: new Date().toLocaleDateString(),
      recommendation: recommendationOutcome,
      originalRecommendation: 'Pulmonologist / Respirologist',
      modifiedSpecialist: recommendationOutcome === 'modify' ? modifiedSpecialist : undefined,
      doctorNote: doctorNote,
      doctorRecommendations: selectedRecommendations,
      followUpDate: followUpDate
    };
    doctorBridgeService.submitReview(review);
    loadData();
    setActiveStep(4);
  };

  const handleResetBridge = () => {
    if (window.confirm('Reset this clinical simulation to configure a new review?')) {
      doctorBridgeService.resetReview();
      loadData();
      setActiveStep(1);
    }
  };

  const patientName = patient?.name || user?.name || 'Jane Doe';

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-300">
      {/* Header */}
      {currentReview && (
        <div className="flex items-center justify-end gap-4 flex-wrap border-b border-brand-slate/10 pb-4">
          <button
            onClick={handleResetBridge}
            className="flex items-center gap-1.5 text-xxs font-bold text-brand-rose-text hover:text-brand-rose-text/80 border border-brand-rose-text/10 px-3.5 py-2 rounded-xl bg-brand-rose-bg/20 transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Simulation
          </button>
        </div>
      )}

      {/* Progress Tracker Stepper (Navigation Block) */}
      <div className="bg-brand-card border border-brand-slate/10 p-4 rounded-2xl shadow-xxs">
        <div className="flex flex-col md:flex-row justify-between gap-4">
          {[
            { step: 1, label: 'Patient Brief', icon: User },
            { step: 2, label: 'Discussion Questions', icon: ClipboardList },
            { step: 3, label: 'Doctor Review (Sim)', icon: Stethoscope },
            { step: 4, label: 'Approved Feedback', icon: FileCheck }
          ].map(s => {
            const Icon = s.icon;
            const isActive = activeStep === s.step;
            const isCompleted = activeStep > s.step;
            
            return (
              <button
                key={s.step}
                disabled={s.step === 4 && !currentReview}
                onClick={() => setActiveStep(s.step)}
                className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all border text-left ${
                  isActive
                    ? 'bg-brand-lavender text-white border-brand-lavender shadow-sm'
                    : isCompleted
                    ? 'bg-brand-sage-bg border-brand-sage-text/10 text-brand-sage-text hover:bg-brand-sage-bg/85 cursor-pointer'
                    : 'bg-brand-bg border-brand-slate/10 text-brand-slate hover:border-brand-slate/20 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{s.label}</span>
                {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-brand-sage-text shrink-0" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Dynamic Step Panel Content */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm flex flex-col gap-6 animate-in fade-in duration-300">
        
        {/* STEP 1: PATIENT BRIEF */}
        {activeStep === 1 && (
          <div className="flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
            <div className="border-b border-brand-slate/10 pb-4">
              <h3 className="font-display font-extrabold text-sm text-brand-plum uppercase tracking-wider">Patient Clinical Summary Brief</h3>
              <p className="text-brand-slate text-[11px] font-light mt-0.5">Designed to brief your practitioner efficiently.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Patient Overview & Symptoms */}
              <div className="flex flex-col gap-5">
                <div className="bg-brand-bg/50 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider border-b border-brand-slate/10 pb-1.5">Patient Overview</h4>
                  <div className="grid grid-cols-2 gap-3 text-xxs text-brand-slate font-light leading-relaxed">
                    <div>
                      <span className="font-bold text-brand-plum block">Patient Name</span>
                      <span>{patientName}</span>
                    </div>
                    <div>
                      <span className="font-bold text-brand-plum block">Primary Concern</span>
                      <span>Pulmonary Check-up</span>
                    </div>
                    <div>
                      <span className="font-bold text-brand-plum block">Journey Duration</span>
                      <span>4 Days Active</span>
                    </div>
                    <div>
                      <span className="font-bold text-brand-plum block">Profile Context</span>
                      <span>Age {patient?.age || '28'} &bull; {patient?.gender || 'Female'}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-brand-bg/50 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider border-b border-brand-slate/10 pb-1.5">Symptom Summary</h4>
                  <p className="text-xs text-brand-plum leading-relaxed bg-brand-card p-3 rounded-xl border border-brand-slate/5 font-light italic">
                    "{patient?.current_symptoms || 'Dry cough logged for 3 days alongside chest tightness and mild exertional dyspnea.'}"
                  </p>
                  <div className="text-xxs text-brand-slate font-light leading-relaxed">
                    <span className="font-bold text-brand-plum block">Changes Over Time</span>
                    <span>Cough intensity increased slightly on Day 2; breathlessness noted during light walking.</span>
                  </div>
                </div>
              </div>

              {/* Treatment History & Records */}
              <div className="flex flex-col gap-5">
                <div className="bg-brand-bg/50 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider border-b border-brand-slate/10 pb-1.5 flex justify-between items-center">
                    <span>Extracted Prescription Regimen</span>
                    {uploadedDocs.length > 0 && <span className="text-brand-lavender text-[9px] font-semibold">Parsed from Uploaded Files</span>}
                  </h4>
                  <div className="text-xxs text-brand-slate font-light leading-relaxed flex flex-col gap-2">
                    {(() => {
                      const extractedMeds: { name: string; source: string }[] = [];
                      uploadedDocs.forEach((d: any) => {
                        if (d.result?.extracted?.medicines) {
                          d.result.extracted.medicines.forEach((m: string) => {
                            extractedMeds.push({ name: m, source: d.name });
                          });
                        }
                      });

                      if (extractedMeds.length > 0) {
                        return extractedMeds.map((m, idx) => (
                          <div key={idx}>
                            <span className="font-bold text-brand-plum">{m.name}</span>
                            <span className="block text-brand-slate">Prescribed in uploaded file: {m.source}</span>
                          </div>
                        ));
                      }

                      return (
                        <>
                          <div>
                            <span className="font-bold text-brand-plum">Albuterol Sulfate Inhaler (90 mcg)</span>
                            <span className="block">Dose: 2 puffs every 4-6 hours as needed &bull; Duration: 14 days</span>
                          </div>
                          <div>
                            <span className="font-bold text-brand-plum">Metformin Oral Tablet (500 mg)</span>
                            <span className="block">Dose: 1 tablet twice daily with meals &bull; Ongoing</span>
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>

                <div className="bg-brand-bg/50 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider border-b border-brand-slate/10 pb-1.5 flex justify-between items-center">
                    <span>Uploaded Diagnostics & Files</span>
                    {uploadedDocs.length > 0 && <span className="text-brand-lavender text-[9px] font-semibold">{uploadedDocs.length} Document(s)</span>}
                  </h4>
                  <div className="text-xxs text-brand-slate font-light leading-relaxed flex flex-col gap-2.5">
                    {uploadedDocs.length > 0 ? (
                      uploadedDocs.map((doc: any) => {
                        const meds = doc.result?.extracted?.medicines?.length > 0 ? `Medicines: ${doc.result.extracted.medicines.join(', ')}` : '';
                        const conds = doc.result?.extracted?.conditions?.length > 0 ? `Diagnoses: ${doc.result.extracted.conditions.join(', ')}` : '';
                        const tests = doc.result?.extracted?.measurements?.length > 0 ? `Metrics: ${doc.result.extracted.measurements.join('; ')}` : '';
                        const sub = [conds, meds, tests].filter(Boolean).join(' | ');

                        return (
                          <div key={doc.id} className="bg-brand-card p-2.5 rounded-xl border border-brand-slate/10">
                            <span className="font-bold text-brand-plum block">{doc.name} ({doc.category})</span>
                            <span className="block text-brand-slate mt-0.5">{sub || doc.result?.summary?.keyInfo || 'Parsed into clinical memory graph.'}</span>
                          </div>
                        );
                      })
                    ) : (
                      <>
                        <div>
                          <span className="font-bold text-brand-plum">01_patient_medical_record.pdf</span>
                          <span className="block">Extracted: Hypertension, Diabetes Mellitus, Metformin 500mg, Lisinopril 10mg.</span>
                        </div>
                        <div>
                          <span className="font-bold text-brand-plum">rx_albuterol_90mcg.pdf</span>
                          <span className="block">Extracted: Albuterol 90mcg (2 puffs every 4-6 hours).</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* AI Suggestion block (passive clinical suggestion terminology) */}
            <div className="bg-brand-lavender-light/35 border-l-2 border-brand-lavender p-5 rounded-r-2xl flex gap-3 mt-2">
              <Brain className="w-5 h-5 text-brand-lavender shrink-0 mt-0.5" />
              <div>
                <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider block">AI Navigation Suggestion</span>
                <p className="text-xs text-brand-plum leading-relaxed font-light mt-1">
                  {uploadedDocs.length > 0 ? (
                    `CarePath reviewed your uploaded documents (${uploadedDocs.map(d => d.name).join(', ')}). Based on parsed health records and symptom logs, CarePath suggests discussing your ongoing medication response and diagnostic values with your primary practitioner.`
                  ) : (
                    'CarePath noticed consolidation markings in your right lower lobe scan and sub-optimal symptom recovery under bronchodilators. CarePath suggests discussing with your doctor whether a specialist pulmonologist consult is appropriate.'
                  )}
                </p>
              </div>
            </div>

            {/* CTA */}
            <div className="flex justify-end mt-4">
              <button
                onClick={() => setActiveStep(2)}
                className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-6 py-3 rounded-xl transition-all shadow-sm flex items-center gap-1 cursor-pointer"
              >
                Go to Discussion Questions
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: CASE-SPECIFIC QUESTIONS */}
        {activeStep === 2 && (
          <div className="flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
            <div className="border-b border-brand-slate/10 pb-4">
              <h3 className="font-display font-extrabold text-sm text-brand-plum uppercase tracking-wider">Suggested Questions for Your Appointment</h3>
              <p className="text-brand-slate text-[11px] font-light mt-0.5">Copy or track diagnostic questions compiled from your clinical history.</p>
            </div>

            {/* Question checklist */}
            <div className="flex flex-col gap-4">
              {questions.map((q) => (
                <div 
                  key={q.id}
                  className={`border rounded-2xl p-4 transition-all flex items-start justify-between gap-4 ${
                    q.isAsked ? 'border-brand-sage-text/20 bg-brand-sage-bg/5' : 'border-brand-slate/10 bg-brand-bg/10'
                  }`}
                >
                  <div className="flex gap-3 items-start min-w-0">
                    <button
                      onClick={() => handleToggleAsked(q.id)}
                      className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 mt-0.5 cursor-pointer transition-all ${
                        q.isAsked 
                          ? 'bg-brand-sage-text border-brand-sage-text text-white' 
                          : 'border-brand-slate/30 hover:border-brand-lavender bg-brand-card'
                      }`}
                    >
                      {q.isAsked && <CheckCircle2 className="w-3.5 h-3.5 fill-current" />}
                    </button>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-brand-plum leading-relaxed">{q.text}</p>
                      <span className="text-xxs text-brand-slate font-light mt-1.5 block italic leading-snug">
                        Why relevant: {q.relevance}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleCopyQuestion(q.id, q.text)}
                    className="p-2 hover:bg-brand-lavender-light text-brand-slate hover:text-brand-lavender rounded-lg shrink-0 transition-all cursor-pointer relative"
                    title="Copy Question"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    {copiedId === q.id && (
                      <span className="absolute -top-7 -left-6 bg-brand-plum text-white text-[9px] px-1.5 py-0.5 rounded shadow-xs whitespace-nowrap">
                        Copied!
                      </span>
                    )}
                  </button>
                </div>
              ))}
            </div>

            {/* Custom Question Form */}
            <form onSubmit={handleAddQuestion} className="bg-brand-bg/40 border border-brand-slate/5 p-4 rounded-2xl flex flex-col gap-3">
              <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block">Add My Own Question</label>
              <div className="flex gap-2.5">
                <input
                  type="text"
                  placeholder="e.g. Can we review if a repeat X-ray is needed in two weeks?"
                  value={customQuestionText}
                  onChange={(e) => setCustomQuestionText(e.target.value)}
                  className="bg-brand-card border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs text-brand-plum outline-none focus:border-brand-lavender transition-all flex-1"
                />
                <button
                  type="submit"
                  className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-xxs transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
            </form>

            {/* CTA */}
            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setActiveStep(1)}
                className="text-xs font-bold text-brand-slate hover:text-brand-plum flex items-center gap-1 cursor-pointer"
              >
                Back to Patient Brief
              </button>
              <button
                onClick={() => setActiveStep(3)}
                className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-6 py-3 rounded-xl transition-all shadow-sm flex items-center gap-1 cursor-pointer"
              >
                Simulate Doctor Review Portal
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: DOCTOR REVIEW INTERFACE (SIMULATOR) */}
        {activeStep === 3 && (
          <div className="flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
            <div className="border-b border-brand-slate/10 pb-4">
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-bold text-brand-rose-text bg-brand-rose-bg border border-brand-rose-text/10 px-2 py-0.5 rounded-md">SIMULATION PORTAL</span>
                <h3 className="font-display font-extrabold text-sm text-brand-plum uppercase tracking-wider">Clinician Decision Workspace</h3>
              </div>
              <p className="text-brand-slate text-[11px] font-light mt-0.5">Simulate how a physician would review AI suggestions and issue sign-offs.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
              {/* Left 3 columns: Summary review */}
              <div className="lg:col-span-3 flex flex-col gap-5">
                <div className="border border-brand-slate/10 p-5 rounded-2xl flex flex-col gap-3 bg-brand-bg/30">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase block tracking-wider border-b border-brand-slate/5 pb-1">AI Recommendation Mapping</h4>
                  <div className="text-xs font-light leading-relaxed">
                    <span className="font-bold text-brand-plum block">Specialist Suggestion: Pulmonologist</span>
                    <span className="text-brand-slate block mt-1">Based on right lower lobe consolidation markings and lack of bronchodilator therapeutic progress.</span>
                  </div>
                </div>

                {/* Confirm/Modify inputs */}
                <div className="flex flex-col gap-4">
                  <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Clinical Referral Assessment</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2.5 p-4 border rounded-2xl cursor-pointer hover:bg-brand-bg/40 transition-all flex-1 border-brand-slate/10">
                      <input
                        type="radio"
                        name="outcome"
                        checked={recommendationOutcome === 'confirm'}
                        onChange={() => setRecommendationOutcome('confirm')}
                        className="text-brand-lavender focus:ring-brand-lavender cursor-pointer"
                      />
                      <div className="text-xxs">
                        <span className="font-bold text-brand-plum block">Confirm Recommendation</span>
                        <span className="text-brand-slate font-light mt-0.5 block">Endorse Pulmonologist match</span>
                      </div>
                    </label>

                    <label className="flex items-center gap-2.5 p-4 border rounded-2xl cursor-pointer hover:bg-brand-bg/40 transition-all flex-1 border-brand-slate/10">
                      <input
                        type="radio"
                        name="outcome"
                        checked={recommendationOutcome === 'modify'}
                        onChange={() => setRecommendationOutcome('modify')}
                        className="text-brand-lavender focus:ring-brand-lavender cursor-pointer"
                      />
                      <div className="text-xxs">
                        <span className="font-bold text-brand-plum block">Modify Recommendation</span>
                        <span className="text-brand-slate font-light mt-0.5 block">Redirect to alternative match</span>
                      </div>
                    </label>
                  </div>
                </div>

                {recommendationOutcome === 'modify' && (
                  <div className="flex flex-col gap-1.5 animate-in slide-in-from-top-1 duration-200">
                    <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Alternative Specialist Routing</label>
                    <select
                      value={modifiedSpecialist}
                      onChange={(e) => setModifiedSpecialist(e.target.value)}
                      className="bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs text-brand-plum cursor-pointer outline-none focus:border-brand-lavender transition-all"
                    >
                      <option value="Allergist / Immunologist">Allergist / Immunologist</option>
                      <option value="Cardiologist">Cardiologist</option>
                      <option value="General Internist">General Internist</option>
                      <option value="Infectious Disease Specialist">Infectious Disease Specialist</option>
                    </select>
                  </div>
                )}

                {/* Doctor Note */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Clinical Practitioner Note</label>
                  <textarea
                    rows={4}
                    value={doctorNote}
                    onChange={(e) => setDoctorNote(e.target.value)}
                    placeholder="Enter clinical assessment directions..."
                    className="bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-xs text-brand-plum outline-none focus:border-brand-lavender transition-all leading-relaxed font-light"
                  />
                </div>
              </div>

              {/* Right 2 columns: Checklists & signing */}
              <div className="lg:col-span-2 flex flex-col gap-5">
                {/* Checklists */}
                <div className="bg-brand-bg/40 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-brand-slate uppercase block tracking-wider border-b border-brand-slate/5 pb-1">Recommended Actions</h4>
                  
                  <div className="flex flex-col gap-2.5 mt-1.5">
                    {[
                      'Continue current plan',
                      'Complete recommended test',
                      'Follow up on specified date',
                      'Schedule pulmonary spirometry test'
                    ].map(rec => {
                      const isSelected = selectedRecommendations.includes(rec);
                      return (
                        <button
                          key={rec}
                          type="button"
                          onClick={() => handleToggleRecommendation(rec)}
                          className={`flex items-center gap-2 text-xxs font-semibold text-left p-2.5 rounded-xl border transition-all ${
                            isSelected 
                              ? 'bg-brand-sage-bg border-brand-sage-text/25 text-brand-sage-text' 
                              : 'bg-brand-card border-brand-slate/10 text-brand-slate hover:border-brand-slate/20'
                          }`}
                        >
                          <CheckCircle2 className={`w-4 h-4 shrink-0 ${isSelected ? 'text-brand-sage-text' : 'text-brand-slate/20'}`} />
                          <span>{rec}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Follow-up date */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Follow-up Review Date</label>
                  <input
                    type="date"
                    value={followUpDate}
                    onChange={(e) => setFollowUpDate(e.target.value)}
                    className="bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs text-brand-plum outline-none focus:border-brand-lavender transition-all"
                  />
                </div>

                {/* Signing Practitioner Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Practitioner Name / Signature</label>
                  <input
                    type="text"
                    value={doctorName}
                    onChange={(e) => setDoctorName(e.target.value)}
                    placeholder="Dr. Robert Chen, MD"
                    className="bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs text-brand-plum font-semibold outline-none focus:border-brand-lavender transition-all"
                  />
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="flex justify-between items-center mt-4 border-t border-brand-slate/5 pt-4">
              <button
                onClick={() => setActiveStep(2)}
                className="text-xs font-bold text-brand-slate hover:text-brand-plum flex items-center gap-1 cursor-pointer"
              >
                Back to Questions
              </button>
              
              <button
                onClick={handleSubmitDoctorReview}
                className="bg-brand-sage-text hover:bg-brand-sage-text/90 text-white text-xs font-bold px-6 py-3.5 rounded-xl transition-all shadow-sm flex items-center gap-1.5 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                Submit Clinical Sign-off
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: APPROVED FEEDBACK */}
        {activeStep === 4 && (
          <div className="flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
            <div className="border-b border-brand-slate/10 pb-4">
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-bold text-brand-sage-text bg-brand-sage-bg border border-brand-sage-text/10 px-2 py-0.5 rounded-md">VERIFIED SIGN-OFF</span>
                <h3 className="font-display font-extrabold text-sm text-brand-plum uppercase tracking-wider">Physician Approved Guidance</h3>
              </div>
              <p className="text-brand-slate text-[11px] font-light mt-0.5">CarePath recommendation overridden and signed off by your attending physician.</p>
            </div>

            {/* Clinical Validation card */}
            <div className="border border-brand-sage-text/20 bg-brand-sage-bg/5 p-6 rounded-3xl flex flex-col md:flex-row gap-5 items-start">
              <div className="w-12 h-12 rounded-xl bg-brand-sage-bg text-brand-sage-text flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6 stroke-[2.5]" />
              </div>
              
              <div className="flex-1 flex flex-col gap-3 min-w-0">
                <div>
                  <span className="text-[10px] font-bold text-brand-sage-text uppercase tracking-wider block">Clinical Status</span>
                  <h3 className="font-display font-extrabold text-md md:text-lg text-brand-plum mt-1">
                    Recommendation Reviewed & Approved
                  </h3>
                  <span className="text-[10px] text-brand-slate block mt-0.5">
                    Authorized by <span className="font-bold text-brand-plum">{currentReview?.reviewedBy || doctorName}</span> &bull; Issued {currentReview?.reviewedDate || new Date().toLocaleDateString()}
                  </span>
                </div>

                <div className="border-t border-brand-slate/10 pt-3 flex flex-col gap-2">
                  <div className="flex flex-wrap items-center gap-3 text-xxs text-brand-slate font-light">
                    <div>
                      <span className="font-bold text-brand-plum block">CarePath AI Suggested:</span>
                      <span>Specialist Review ({currentReview?.originalRecommendation || 'Pulmonologist / Respirologist'})</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-brand-slate/30 hidden md:block" />
                    <div>
                      <span className="font-bold text-brand-sage-text block">Doctor Endorsed Result:</span>
                      <span>
                        {currentReview?.recommendation === 'confirm' 
                          ? `Confirmed (${currentReview.originalRecommendation})`
                          : `Modified to: ${currentReview?.modifiedSpecialist || modifiedSpecialist}`}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Doctor Note display */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              {/* Note */}
              <div className="md:col-span-3 border border-brand-slate/10 p-5 rounded-2xl flex flex-col gap-2 bg-brand-bg/30">
                <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block">Physician Clinical Assessment Note</span>
                <p className="text-xs text-brand-plum leading-relaxed font-light italic">
                  "{currentReview?.doctorNote || doctorNote}"
                </p>
              </div>

              {/* Verified Checklist */}
              <div className="md:col-span-2 bg-brand-bg/50 border border-brand-slate/5 p-5 rounded-2xl flex flex-col gap-3">
                <span className="text-[10px] font-bold text-brand-slate uppercase block tracking-wider border-b border-brand-slate/10 pb-1.5">Approved Next Action Steps</span>
                <div className="flex flex-col gap-2">
                  {(currentReview?.doctorRecommendations || selectedRecommendations).map((rec, i) => (
                    <div key={i} className="flex gap-2 items-center text-xxs text-brand-plum font-semibold">
                      <CheckCircle2 className="w-4 h-4 text-brand-sage-text shrink-0" />
                      <span>{rec}</span>
                    </div>
                  ))}
                  <div className="mt-2.5 p-3.5 bg-brand-card border border-brand-slate/10 rounded-xl flex items-center gap-2">
                    <Clock className="w-4 h-4 text-brand-lavender shrink-0" />
                    <div className="text-xxs text-brand-slate leading-tight font-light">
                      <span className="font-bold text-brand-plum block">Next Follow-up Check</span>
                      <span>Date: {currentReview?.followUpDate || followUpDate}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Return link */}
            <div className="flex justify-between items-center mt-4 border-t border-brand-slate/10 pt-4">
              <Link 
                to="/dashboard"
                className="text-xs font-bold text-brand-slate hover:text-brand-plum inline-flex items-center gap-1.5"
              >
                <ArrowLeft className="w-4 h-4" />
                Return to Dashboard
              </Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
