import { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { notificationService } from '../services/notificationService';
import { 
  Bell, 
  Check, 
  MailOpen, 
  AlertCircle, 
  CheckCircle2 
} from 'lucide-react';
import type { AppNotification } from '../types';

export default function NotificationsPage() {
  const { patient } = usePatient();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (patient?.id === 'demo_patient_id') {
        setNotifications([
          {
            id: '1',
            title: 'Welcome to CarePath AI',
            message: 'Your healthcare navigation profile has been initialized successfully.',
            read: true,
            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          },
          {
            id: '2',
            title: 'Upload Completed',
            message: 'Chest X-Ray document uploaded. Vision Agent analysis is ready to begin.',
            read: false,
            created_at: new Date(Date.now() - 86400000).toISOString(),
          },
          {
            id: '3',
            title: 'Analysis Recommended Specialist',
            message: 'Our clinical supervisor has recommended consulting a Pulmonologist based on chest X-ray findings.',
            read: false,
            created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
          }
        ]);
      } else {
        const data = await notificationService.getNotifications();
        setNotifications(data);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to retrieve notifications.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [patient]);

  const handleMarkAsRead = async (id: string) => {
    try {
      if (patient?.id === 'demo_patient_id') {
        setNotifications(prev => 
          prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
      } else {
        await notificationService.markAsRead(id);
        await fetchNotifications();
      }
    } catch (err: any) {
      console.error(err);
      alert('Failed to mark notification as read.');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const unread = notifications.filter(n => !n.read);
      if (unread.length === 0) return;
      
      if (patient?.id === 'demo_patient_id') {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      } else {
        await Promise.all(unread.map(n => notificationService.markAsRead(n.id)));
        await fetchNotifications();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      {/* Action Row */}
      {unreadCount > 0 && (
        <div className="flex justify-end">
          <button
            onClick={handleMarkAllAsRead}
            className="flex items-center justify-center gap-1.5 text-xxs font-semibold text-brand-lavender hover:underline cursor-pointer border border-brand-lavender/20 rounded-xl px-4 py-2 bg-brand-card shadow-xs"
          >
            <Check className="w-3.5 h-3.5" />
            Mark all read
          </button>
        </div>
      )}

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-lavender"></div>
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-brand-card border border-brand-slate/10 p-12 rounded-2xl text-center flex flex-col items-center gap-6 my-6">
          <div className="w-14 h-14 bg-brand-bg rounded-full flex items-center justify-center text-brand-slate">
            <MailOpen className="w-6 h-6" />
          </div>
          <div>
            <h2 className="font-display text-xl font-bold text-brand-plum mb-2">Clear notifications</h2>
            <p className="text-brand-slate text-xs max-w-xs leading-relaxed mx-auto">
              You are up to date! Future path recommendations or document confirmations appear here.
            </p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {notifications.map((n) => (
            <div 
              key={n.id}
              className={`border p-5 rounded-2xl transition-all shadow-xs flex gap-4 ${
                n.read 
                  ? 'bg-brand-card border-brand-slate/10 opacity-75' 
                  : 'bg-brand-lavender-light/35 border-brand-lavender/30 ring-2 ring-brand-lavender/5'
              }`}
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                n.read ? 'bg-brand-bg text-brand-slate' : 'bg-brand-lavender text-white'
              }`}>
                <Bell className="w-4 h-4" />
              </div>

              <div className="flex-1 flex flex-col gap-1.5">
                <div className="flex justify-between items-start gap-3">
                  <h3 className={`text-sm font-semibold ${n.read ? 'text-brand-plum' : 'text-brand-plum font-bold'}`}>
                    {n.title}
                  </h3>
                  <span className="text-[10px] text-brand-slate/60 shrink-0 mt-0.5">
                    {new Date(n.created_at).toLocaleDateString(undefined, { 
                      month: 'short', 
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>

                <p className="text-brand-slate text-xs font-light leading-relaxed">
                  {n.message}
                </p>

                {!n.read && (
                  <button
                    onClick={() => handleMarkAsRead(n.id)}
                    className="flex items-center gap-1 text-xxs text-brand-lavender font-bold mt-2 hover:underline w-fit"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Mark as read
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
