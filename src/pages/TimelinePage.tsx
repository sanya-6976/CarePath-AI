import React, { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { timelineService } from '../services/timelineService';
import { 
  Activity, 
  Upload, 
  Sparkles, 
  UserCheck, 
  Calendar, 
  CheckSquare, 
  AlertCircle, 
  PlusCircle, 
  FileText,
  X
} from 'lucide-react';
import type { TimelineEvent, TimelineEventType } from '../types';

export default function TimelinePage() {
  const { patient } = usePatient();
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // New event form modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newType, setNewType] = useState<TimelineEventType>('symptom');
  const [newDetails, setNewDetails] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchTimeline = async () => {
    if (!patient) return;
    setIsLoading(true);
    setError(null);
    try {
      if (patient.id === 'demo_patient_id') {
        setEvents([
          {
            id: '1',
            patient_id: 'demo_patient_id',
            type: 'symptom',
            title: 'Logged Symptoms',
            description: 'Dry cough, mild chest tightness on exertion.',
            details: 'Symptoms started 3 days ago. No fever, sore throat, or congestion.',
            timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
          },
          {
            id: '2',
            patient_id: 'demo_patient_id',
            type: 'upload',
            title: 'Uploaded Chest X-Ray',
            description: 'Image file chest_xray_post.png uploaded.',
            details: 'File processed by Vision Agent. Findings include hyperinflation, clear lung fields, no infiltrates.',
            timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
          },
          {
            id: '3',
            patient_id: 'demo_patient_id',
            type: 'analysis',
            title: 'CarePath AI Recommendation',
            description: 'Specialist routing to Pulmonology recommended.',
            details: 'Reasoning: Exertional shortness of breath with hyperinflation signs indicates assessment for airway hyperreactivity or occupational exposures.',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
          }
        ]);
      } else {
        const data = await timelineService.getTimeline(patient.id);
        // Sort events chronologically descending
        const sorted = [...data].sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        setEvents(sorted);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch journey timeline events. Verify local API.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [patient]);

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patient || !newTitle || !newDesc) return;
    setIsSubmitting(true);

    const eventPayload = {
      patient_id: patient.id,
      type: newType,
      title: newTitle,
      description: newDesc,
      details: newDetails,
      timestamp: new Date().toISOString()
    };

    try {
      if (patient.id === 'demo_patient_id') {
        const mockNewEvent: TimelineEvent = {
          id: String(events.length + 1),
          ...eventPayload
        };
        setEvents(prev => [mockNewEvent, ...prev]);
      } else {
        await timelineService.addTimelineEvent(eventPayload);
        await fetchTimeline();
      }
      setModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      setNewDetails('');
    } catch (err: any) {
      console.error(err);
      alert(err.message || 'Failed to append event to timeline.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get icon and color based on event type
  const getEventStyle = (type: TimelineEventType) => {
    switch (type) {
      case 'symptom':
        return { icon: Activity, bg: 'bg-brand-amber-bg text-brand-amber-text border-brand-amber-text/10' };
      case 'upload':
        return { icon: Upload, bg: 'bg-brand-lavender-light text-brand-lavender border-brand-lavender/10' };
      case 'analysis':
        return { icon: Sparkles, bg: 'bg-brand-lavender text-white border-brand-lavender/10' };
      case 'referral':
        return { icon: UserCheck, bg: 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/10' };
      case 'consultation':
        return { icon: Calendar, bg: 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/10' };
      default:
        return { icon: CheckSquare, bg: 'bg-brand-bg text-brand-slate border-brand-slate/10' };
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 relative">
      {/* Action Row */}
      <div className="flex justify-end">
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center justify-center gap-1.5 bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-sm cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" />
          Add Event
        </button>
      </div>

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={fetchTimeline} className="text-xs font-bold underline">Retry</button>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-lavender mb-4"></div>
          <p className="text-brand-slate text-sm">Building CarePath timeline map...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="bg-brand-card border border-brand-slate/10 p-12 rounded-2xl text-center flex flex-col items-center gap-6 my-6">
          <div className="w-14 h-14 bg-brand-bg rounded-full flex items-center justify-center text-brand-slate">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h2 className="font-display text-xl font-bold text-brand-plum mb-2">No care journey events yet</h2>
            <p className="text-brand-slate text-xs max-w-xs leading-relaxed mx-auto">
              Your timeline will populate automatically once symptoms are recorded or medical files are analyzed.
            </p>
          </div>
        </div>
      ) : (
        /* Vertical Timeline Map */
        <div className="relative border-l border-brand-slate/20 ml-4 pl-8 py-4 flex flex-col gap-8">
          {events.map((event) => {
            const style = getEventStyle(event.type);
            const Icon = style.icon;

            return (
              <div key={event.id} className="relative group">
                {/* Timeline node */}
                <div className={`absolute -left-12.5 top-1 w-9 h-9 rounded-full border flex items-center justify-center shadow-sm ${style.bg} transition-transform group-hover:scale-105`}>
                  <Icon className="w-4 h-4" />
                </div>

                {/* Event Card */}
                <div className="bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-xs hover:border-brand-lavender/35 transition-all">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                    <h3 className="font-display font-semibold text-sm text-brand-plum">{event.title}</h3>
                    <span className="text-xxs text-brand-slate/70">
                      {new Date(event.timestamp).toLocaleDateString(undefined, { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>

                  <p className="text-brand-slate text-xs leading-relaxed font-light mb-3">
                    {event.description}
                  </p>

                  {event.details && (
                    <div className="bg-brand-bg/60 border border-brand-slate/5 p-3 rounded-xl text-xs text-brand-plum leading-relaxed font-light italic">
                      {event.details}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Event Modal Overlay */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-plum/45 backdrop-blur-sm">
          <div className="bg-brand-card w-full max-w-md rounded-2xl border border-brand-slate/10 p-6 shadow-md flex flex-col gap-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between">
              <h3 className="font-display font-bold text-base text-brand-plum">Log Timeline Milestone</h3>
              <button 
                onClick={() => setModalOpen(false)}
                className="p-1 rounded-lg hover:bg-brand-bg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddEvent} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xxs font-semibold text-brand-slate">Event Title</label>
                <input 
                  type="text" 
                  placeholder="e.g. Consulted General Practitioner"
                  value={newTitle} 
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xxs font-semibold text-brand-slate">Event Category</label>
                <select 
                  value={newType} 
                  onChange={(e) => setNewType(e.target.value as TimelineEventType)}
                  className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
                >
                  <option value="symptom">Symptom Logging</option>
                  <option value="upload">Document Upload</option>
                  <option value="consultation">Specialist Consultation</option>
                  <option value="followup">Follow-up check-in</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xxs font-semibold text-brand-slate">Short Description</label>
                <input 
                  type="text" 
                  placeholder="Brief summary of the milestone"
                  value={newDesc} 
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xxs font-semibold text-brand-slate">Clinical Notes / Details (Optional)</label>
                <textarea 
                  rows={3}
                  placeholder="Extra advice, symptoms changes, or diagnosis notes..."
                  value={newDetails} 
                  onChange={(e) => setNewDetails(e.target.value)}
                  className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-1.5 cursor-pointer mt-2"
              >
                Log Event
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
