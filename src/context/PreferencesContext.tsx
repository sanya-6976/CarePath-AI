import React, { createContext, useContext, useState, useEffect } from 'react';

export type LanguageType = 'English' | 'Hindi' | 'Hinglish';
export type TextSizeType = 'Standard' | 'Large' | 'Extra Large';

interface PreferencesContextType {
  language: LanguageType;
  setLanguage: (lang: LanguageType) => void;
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
}

const PreferencesContext = createContext<PreferencesContextType | undefined>(undefined);

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<LanguageType>(() => 
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
  const [textSize, setTextSize] = useState<TextSizeType>(() => 
    (localStorage.getItem('carepath_pref_text_size') as TextSizeType) || 'Standard'
  );
  const [reducedMotion, setReducedMotion] = useState<boolean>(() => 
    localStorage.getItem('carepath_pref_reduced_motion') === 'true'
  );
  const [highContrast, setHighContrast] = useState<boolean>(() => 
    localStorage.getItem('carepath_pref_high_contrast') === 'true'
  );

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('carepath_pref_language', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_follow_up_reminders', String(followUpReminders));
  }, [followUpReminders]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_appointment_reminders', String(appointmentReminders));
  }, [appointmentReminders]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_recovery_updates', String(recoveryUpdates));
  }, [recoveryUpdates]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_text_size', textSize);
    const root = document.documentElement;
    root.classList.remove('text-size-large', 'text-size-extra-large');
    if (textSize === 'Large') {
      root.classList.add('text-size-large');
    } else if (textSize === 'Extra Large') {
      root.classList.add('text-size-extra-large');
    }
  }, [textSize]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_reduced_motion', String(reducedMotion));
    const root = document.documentElement;
    if (reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }
  }, [reducedMotion]);

  useEffect(() => {
    localStorage.setItem('carepath_pref_high_contrast', String(highContrast));
    const root = document.documentElement;
    if (highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
  }, [highContrast]);

  return (
    <PreferencesContext.Provider
      value={{
        language,
        setLanguage,
        followUpReminders,
        setFollowUpReminders,
        appointmentReminders,
        setAppointmentReminders,
        recoveryUpdates,
        setRecoveryUpdates,
        textSize,
        setTextSize,
        reducedMotion,
        setReducedMotion,
        highContrast,
        setHighContrast
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
