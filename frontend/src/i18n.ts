export type Locale = 'en' | 'hi';

const copy = {
  en: { companion: 'CarePath Companion', subtitle: 'Your Healthcare Companion', placeholder: 'Ask about your CarePath journey…', send: 'Send', listen: 'Listen', stop: 'Stop', clear: 'Clear conversation', voiceUnavailable: 'Voice input is not supported by this browser.', historyOff: 'CarePath history is off. I will not use your saved health records.' },
  hi: { companion: 'CarePath सहायक', subtitle: 'आपका स्वास्थ्य साथी', placeholder: 'अपनी CarePath यात्रा के बारे में पूछें…', send: 'भेजें', listen: 'सुनें', stop: 'रोकें', clear: 'बातचीत हटाएं', voiceUnavailable: 'इस ब्राउज़र में आवाज़ से लिखना उपलब्ध नहीं है।', historyOff: 'CarePath इतिहास बंद है। मैं आपके सहेजे हुए स्वास्थ्य रिकॉर्ड का उपयोग नहीं करूंगा।' },
} as const;

export const t = (locale: Locale) => copy[locale];
