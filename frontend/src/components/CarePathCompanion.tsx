import { FormEvent, useEffect, useRef, useState } from 'react';
import { Bot, BrainCircuit, Mic, Send, Volume2, Square, Trash2, X, Map } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { usePreferences } from '../context/PreferencesContext';
import { t } from '../i18n';
import { companionService, type CompanionMessage } from '../services/companionService';

type SpeechRecognitionLike = {
  lang: string; continuous: boolean; interimResults: boolean;
  start: () => void; stop: () => void;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
};
declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognitionLike;
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  }
}

/**
 * Navigation intent classifier — runs client-side before hitting backend.
 * Returns a route string or null if no nav intent detected.
 */
function classifyNavIntent(message: string): string | null {
  const m = message.toLowerCase().trim();

  // Dashboard
  if (/\b(dashboard|home|overview|ghar|shuru|mukhy|dasbor|daashbord)\b/.test(m) ||
    /dashboard (dikhao|dikha|kholo|open|go|chalo)/.test(m) ||
    /\b(go to|open|show) (home|dashboard)\b/.test(m)) return '/dashboard';

  // Medical Records
  if (/\b(medical records?|records?|reports?|documents?|test results?)\b/.test(m) ||
    /\b(record|report) (dikhao|dikha|kahan|kholo|where)\b/.test(m) ||
    /\b(meri|my) (reports?|files?|records?)\b/.test(m)) return '/records';

  // Timeline
  if (/\b(timeline|history|health history|events?)\b/.test(m) ||
    /\b(timeline|samay rekha) (dikhao|dikha|kholo)\b/.test(m)) return '/timeline';

  // Medications
  if (/\b(medication|medicine|medicines?|drugs?|dawa|dawai|tablets?)\b/.test(m) ||
    /\b(dawa(iyan)?|meri (dawa|dawai)) (dikhao|dikha|kahan)\b/.test(m)) return '/medications';

  // Upload
  if (/\b(upload|add (document|report|file)|scan|lab report)\b/.test(m) ||
    /\b(upload karo|file (add|upload|bhejo))\b/.test(m)) return '/upload';

  // Settings
  if (/\b(settings|preferences|configuration|language|bhasha)\b/.test(m) ||
    /\b(setting|setting (badlo|karo|dikhao))\b/.test(m)) return '/settings';

  // Follow-up
  if (/\b(follow.?up|follow up|schedule|reminder|appointment)\b/.test(m) ||
    /\b(follow.?up (dikhao|kab|kahan))\b/.test(m)) return '/followup';

  // AI Analysis / Investigation
  if (/\b(analysis|investigation|ai analysis|investigate|diagnos)\b/.test(m) ||
    /\b(analysis|jaanch) (dikhao|start|shuru|karo)\b/.test(m)) return '/analysis';

  // Care Journey
  if (/\b(journey|care journey|care plan|careplan)\b/.test(m) ||
    /\b(journey|yatra) (dikhao|kahan)\b/.test(m)) return '/journey';

  // Doctor Bridge
  if (/\b(doctor|specialist|physician|specialist bridge|doctor bridge)\b/.test(m) &&
    /\b(connect|bridge|talk|contact|meet|milna|baat)\b/.test(m)) return '/doctor-bridge';

  return null;
}

/** Map nav route → text key in i18n nav object */
const routeToNavKey: Record<string, keyof ReturnType<typeof t>['nav']> = {
  '/dashboard': 'dashboard',
  '/records': 'records',
  '/timeline': 'timeline',
  '/medications': 'medications',
  '/upload': 'upload',
  '/settings': 'settings',
  '/followup': 'followup',
  '/analysis': 'analysis',
  '/journey': 'journey',
  '/doctor-bridge': 'doctorBridge',
};

export default function CarePathCompanion() {
  const { locale, voiceResponses, useCarePathHistory, simpleMedicalTerms, isTourActive, startTour } = usePreferences();
  const text = t(locale);
  const location = useLocation();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<CompanionMessage[]>([]);
  const [conversationId, setConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recording, setRecording] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const recognition = useRef<SpeechRecognitionLike | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);
  useEffect(() => () => window.speechSynthesis?.cancel(), []);

  const speak = (value: string) => {
    if (!('speechSynthesis' in window)) { setError('Text-to-speech is not supported by this browser.'); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(value);
    // Hinglish uses hi-IN for closest voice match
    utterance.lang = locale === 'hi' || locale === 'hl' ? 'hi-IN' : 'en-IN';
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => { setSpeaking(false); setError('Voice playback could not start.'); };
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    const message = input.trim();
    if (!message || loading) return;
    setInput('');
    setError('');

    // ── Step 1: check for "start tour" intent ──────────────────────────────
    if (/\b(start|begin|show|launch|guided) (tour|tutorial|walkthrough|demo)\b/i.test(message) ||
      /\b(tour start|tour karo|tour dikhao|guided tour)\b/i.test(message)) {
      const tourMsg = text.tourStarting;
      setMessages(p => [
        ...p,
        { role: 'user', content: message },
        { role: 'assistant', content: tourMsg },
      ]);
      startTour();
      return;
    }

    // ── Step 2: check for navigation intents ──────────────────────────────
    const navRoute = classifyNavIntent(message);
    if (navRoute) {
      const navKey = routeToNavKey[navRoute];
      const navMsg = navKey ? text.nav[navKey] : text.navConfirm;
      setMessages(p => [
        ...p,
        { role: 'user', content: message },
        { role: 'assistant', content: navMsg },
      ]);
      setTimeout(() => navigate(navRoute), 600);
      return;
    }

    // ── Step 3: send to backend ────────────────────────────────────────────
    setMessages(p => [...p, { role: 'user', content: message }]);
    setLoading(true);
    try {
      const result = await companionService.chat({
        message,
        conversation_id: conversationId,
        language: locale,
        page_context: location.pathname,
        use_carepath_history: useCarePathHistory,
        simple_medical_terms: simpleMedicalTerms,
      });
      setConversationId(result.conversation_id);
      setMessages(p => [...p, { role: 'assistant', content: result.answer }]);
      if (voiceResponses) speak(result.answer);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'CarePath Companion is temporarily unavailable. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMic = () => {
    const Constructor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Constructor) { setError(text.voiceUnavailable); return; }
    if (recording) { recognition.current?.stop(); return; }
    const rec = new Constructor();
    rec.lang = locale === 'hi' || locale === 'hl' ? 'hi-IN' : 'en-IN';
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e: any) => setInput(e.results[0][0].transcript);
    rec.onerror = () => setError('Microphone access or transcription failed. You can still type your question.');
    rec.onend = () => setRecording(false);
    recognition.current = rec;
    setError('');
    setRecording(true);
    rec.start();
  };

  const clear = () => {
    setMessages([]);
    setConversationId(undefined);
    setError('');
    window.speechSynthesis?.cancel();
    setSpeaking(false);
  };

  const localeLabel = locale === 'hi' ? 'हिन्दी' : locale === 'hl' ? 'Hinglish' : 'English';

  return (
    <div className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-40">
      {open && (
        <section
          aria-label={text.companion}
          className="mb-3 flex h-[min(640px,78vh)] w-[calc(100vw-2rem)] max-w-[400px] flex-col overflow-hidden rounded-3xl border border-brand-slate/15 bg-brand-card shadow-2xl animate-in slide-in-from-bottom-3 duration-200"
        >
          <header className="flex items-center gap-3 bg-brand-lavender px-4 py-3 text-white">
            <div className="rounded-xl bg-white/20 p-2">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="font-display font-bold">{text.companion}</h2>
              <p className="text-xs text-white/85">{text.subtitle} · {localeLabel}</p>
            </div>
            <button
              aria-label="Start guided tour"
              title="Start guided tour"
              onClick={() => { startTour(); setOpen(false); }}
              className="rounded-lg p-2 hover:bg-white/15"
            >
              <Map className="h-4 w-4" />
            </button>
            <button
              aria-label={text.clear}
              title={text.clear}
              onClick={clear}
              className="rounded-lg p-2 hover:bg-white/15"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            <button
              aria-label="Close companion"
              onClick={() => setOpen(false)}
              className="rounded-lg p-2 hover:bg-white/15"
            >
              <X className="h-5 w-5" />
            </button>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto bg-brand-bg/60 p-4">
            {!messages.length && (
              <p className="rounded-2xl bg-white p-3 text-sm text-brand-slate shadow-sm">
                {useCarePathHistory ? text.historyOn : text.historyOff}
              </p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`group flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${m.role === 'user' ? 'bg-brand-lavender text-white' : 'bg-white text-brand-plum shadow-sm'}`}>
                  <p>{m.content}</p>
                  {m.role === 'assistant' && (
                    <button
                      onClick={() => speaking ? (window.speechSynthesis.cancel(), setSpeaking(false)) : speak(m.content)}
                      className="mt-2 inline-flex items-center gap-1 text-xs text-brand-lavender hover:underline"
                    >
                      <Volume2 className="h-3.5 w-3.5" />
                      {speaking ? text.stop : text.listen}
                    </button>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-sm text-brand-slate">
                <Bot className="h-4 w-4 animate-pulse" />
                {text.thinking}
              </div>
            )}
            {error && (
              <p role="alert" className="rounded-xl bg-brand-rose-bg px-3 py-2 text-xs text-brand-rose-text">
                {error}
              </p>
            )}
            {!isTourActive && (
              <p className="text-xxs text-center text-brand-slate/50 mt-2">
                {locale === 'hi'
                  ? 'गाइडेड टूर के लिए "टूर शुरू करें" लिखें।'
                  : locale === 'hl'
                    ? '"tour start karo" type karo guided tour ke liye.'
                    : 'Type "start tour" for a guided walkthrough.'}
              </p>
            )}
            <div ref={endRef} />
          </div>

          <form onSubmit={submit} className="flex gap-2 border-t border-brand-slate/10 p-3">
            <button
              type="button"
              onClick={toggleMic}
              aria-label={recording ? 'Stop recording' : 'Use microphone'}
              className={`rounded-xl p-2 ${recording ? 'bg-brand-rose-bg text-brand-rose-text animate-pulse' : 'bg-brand-bg text-brand-lavender hover:bg-brand-lavender-light'}`}
            >
              {recording ? <Square className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              maxLength={4000}
              aria-label={text.placeholder}
              placeholder={text.placeholder}
              className="min-w-0 flex-1 rounded-xl border border-brand-slate/15 bg-white px-3 text-sm outline-none focus:border-brand-lavender"
            />
            <button
              disabled={!input.trim() || loading}
              aria-label={text.send}
              className="rounded-xl bg-brand-lavender p-2 text-white disabled:opacity-40"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </section>
      )}

      <button
        onClick={() => setOpen(v => !v)}
        aria-label={open ? 'Close CarePath Companion' : 'Open CarePath Companion'}
        title={text.companion}
        className="ml-auto flex h-14 w-14 items-center justify-center rounded-full bg-brand-lavender text-white shadow-lg transition hover:scale-105 active:scale-95"
      >
        <BrainCircuit className="h-6 w-6" />
      </button>
    </div>
  );
}
