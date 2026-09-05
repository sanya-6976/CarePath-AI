import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getLocale, type Locale } from '../i18n';

export type LanguageType = 'English' | 'Hindi' | 'Hinglish';
export type TextSizeType = 'Standard' | 'Large' | 'Extra Large';

interface PreferencesContextType {
  language: LanguageType;
  setLanguage: (lang: LanguageType) => void;
  locale: Locale;
  followUpReminders: boolean;
  setFollowUpReminders: (val: boolean) => void;
  appointmentReminders: boolean;
  setAppointmentReminders: (val: boolean) => void;
  recoveryUpdates: boolean;
  setRecoveryUpdates: (val: boolean) => void;
  textSize: TextSizeType;
  setTextSize: (size: TextSizeType) => void;
  reducedMotion: boolean;
  setReducedMotion: (val: boolean) => void;
  highContrast: boolean;
  setHighContrast: (val: boolean) => void;
  voiceResponses: boolean;
  setVoiceResponses: (val: boolean) => void;
  useCarePathHistory: boolean;
  setUseCarePathHistory: (val: boolean) => void;
  simpleMedicalTerms: boolean;
  setSimpleMedicalTerms: (val: boolean) => void;
  // Guided Tour
  isTourActive: boolean;
  startTour: () => void;
  endTour: () => void;
}

const PreferencesContext = createContext<PreferencesContextType | undefined>(undefined);

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<LanguageType>(() =>
    (localStorage.getItem('carepath_pref_language') as LanguageType) || 'English'
  );
  const [followUpReminders, setFollowUpReminders] = useState<boolean>(() =>
    localStorage.getItem('carepath_pref_follow_up_reminders') !== 'false'
  );
  const [appointmentReminders, setAppointmentReminders] = useState<boolean>(() =>
    localStorage.getItem('carepath_pref_appointment_reminders') !== 'false'
  );
  const [recoveryUpdates, setRecoveryUpdates] = useState<boolean>(() =>
    localStorage.getItem('carepath_pref_recovery_updates') !== 'false'
  );
  const [textSize, setTextSizeState] = useState<TextSizeType>(() =>
    (localStorage.getItem('carepath_pref_text_size') as TextSizeType) || 'Standard'
  );
  const [reducedMotion, setReducedMotionState] = useState<boolean>(() =>
    localStorage.getItem('carepath_pref_reduced_motion') === 'true'
  );
  const [highContrast, setHighContrastState] = useState<boolean>(() =>
    localStorage.getItem('carepath_pref_high_contrast') === 'true'
  );
  const [voiceResponses, setVoiceResponses] = useState(() =>
    localStorage.getItem('carepath_pref_voice_responses') === 'true'
  );
  const [useCarePathHistory, setUseCarePathHistory] = useState(() =>
    localStorage.getItem('carepath_pref_use_history') !== 'false'
  );
  const [simpleMedicalTerms, setSimpleMedicalTerms] = useState(() =>
    localStorage.getItem('carepath_pref_simple_terms') !== 'false'
  );
  const [isTourActive, setIsTourActive] = useState(false);

  // Derived locale
  const locale: Locale = getLocale(language);

  // Language setter — also updates document lang attribute
  const setLanguage = useCallback((lang: LanguageType) => {
    setLanguageState(lang);
    const localeCode = getLocale(lang);
    document.documentElement.setAttribute('lang', localeCode === 'hi' ? 'hi' : 'en');
  }, []);

  // Text size setter
  const setTextSize = useCallback((size: TextSizeType) => {
    setTextSizeState(size);
    const root = document.documentElement;
    root.classList.remove('text-size-large', 'text-size-extra-large');
    if (size === 'Large') root.classList.add('text-size-large');
    else if (size === 'Extra Large') root.classList.add('text-size-extra-large');
  }, []);

  // Reduced motion setter
  const setReducedMotion = useCallback((val: boolean) => {
    setReducedMotionState(val);
    document.documentElement.classList.toggle('reduced-motion', val);
  }, []);

  // High contrast setter
  const setHighContrast = useCallback((val: boolean) => {
    setHighContrastState(val);
    document.documentElement.classList.toggle('high-contrast', val);
  }, []);

  // Tour controls
  const startTour = useCallback(() => setIsTourActive(true), []);
  const endTour = useCallback(() => setIsTourActive(false), []);

  // Persist to localStorage
  useEffect(() => { localStorage.setItem('carepath_pref_language', language); }, [language]);
  useEffect(() => { localStorage.setItem('carepath_pref_follow_up_reminders', String(followUpReminders)); }, [followUpReminders]);
  useEffect(() => { localStorage.setItem('carepath_pref_appointment_reminders', String(appointmentReminders)); }, [appointmentReminders]);
  useEffect(() => { localStorage.setItem('carepath_pref_recovery_updates', String(recoveryUpdates)); }, [recoveryUpdates]);
  useEffect(() => { localStorage.setItem('carepath_pref_text_size', textSize); }, [textSize]);
  useEffect(() => { localStorage.setItem('carepath_pref_reduced_motion', String(reducedMotion)); }, [reducedMotion]);
  useEffect(() => { localStorage.setItem('carepath_pref_high_contrast', String(highContrast)); }, [highContrast]);
  useEffect(() => { localStorage.setItem('carepath_pref_voice_responses', String(voiceResponses)); }, [voiceResponses]);
  useEffect(() => { localStorage.setItem('carepath_pref_use_history', String(useCarePathHistory)); }, [useCarePathHistory]);
  useEffect(() => { localStorage.setItem('carepath_pref_simple_terms', String(simpleMedicalTerms)); }, [simpleMedicalTerms]);

  // Re-apply CSS classes on mount (in case user refreshes with non-default settings)
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('text-size-large', 'text-size-extra-large');
    if (textSize === 'Large') root.classList.add('text-size-large');
    else if (textSize === 'Extra Large') root.classList.add('text-size-extra-large');
    root.classList.toggle('reduced-motion', reducedMotion);
    root.classList.toggle('high-contrast', highContrast);
    root.setAttribute('lang', locale === 'hi' ? 'hi' : 'en');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // intentionally run once on mount

  return (
    <PreferencesContext.Provider
      value={{
        language, setLanguage, locale,
        followUpReminders, setFollowUpReminders,
        appointmentReminders, setAppointmentReminders,
        recoveryUpdates, setRecoveryUpdates,
        textSize, setTextSize,
        reducedMotion, setReducedMotion,
        highContrast, setHighContrast,
        voiceResponses, setVoiceResponses,
        useCarePathHistory, setUseCarePathHistory,
        simpleMedicalTerms, setSimpleMedicalTerms,
        isTourActive, startTour, endTour,
      }}
    >
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const context = useContext(PreferencesContext);
  if (context === undefined) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
}

/** Convenience hook: returns current locale code ('en' | 'hi' | 'hl') */
export function useLocale() {
  return usePreferences().locale;
}
