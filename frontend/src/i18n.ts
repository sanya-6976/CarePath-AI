/**
 * CarePath AI — centralised i18n strings.
 *
 * Locales
 *  en  – English (default)
 *  hi  – Hindi (full UI translation)
 *  hl  – Hinglish (natural Indian conversational, NOT machine translation)
 *
 * Usage:
 *   import { t, getLocale } from '../i18n';
 *   const text = t(getLocale(language));
 */

export type Locale = 'en' | 'hi' | 'hl';
export type LanguageType = 'English' | 'Hindi' | 'Hinglish';

/** Map PreferencesContext language name → locale code */
export function getLocale(language: LanguageType): Locale {
  if (language === 'Hindi') return 'hi';
  if (language === 'Hinglish') return 'hl';
  return 'en';
}

const copy = {
  // ─── Companion / Chat ──────────────────────────────────────────────────────
  en: {
    companion: 'CarePath Companion',
    subtitle: 'Your Healthcare Companion',
    placeholder: 'Ask about your CarePath journey…',
    send: 'Send',
    listen: 'Listen',
    stop: 'Stop',
    clear: 'Clear conversation',
    voiceUnavailable: 'Voice input is not supported by this browser.',
    historyOff: 'CarePath history is off. I will not use your saved health records.',
    historyOn: 'I can help you understand your CarePath records.',
    thinking: 'Thinking…',
    navConfirm: 'Taking you there now.',

    // ─── Navigation intents ───────────────────────────────────────────────
    nav: {
      dashboard: 'Opening Dashboard…',
      records: 'Opening Medical Records…',
      timeline: 'Opening Timeline…',
      medications: 'Opening Medications…',
      upload: 'Opening Upload Center…',
      settings: 'Opening Settings…',
      followup: 'Opening Follow-up…',
      analysis: 'Opening Analysis…',
      journey: 'Opening Care Journey…',
      doctorBridge: 'Opening Doctor Bridge…',
    },

    // ─── Tour ────────────────────────────────────────────────────────────
    tourStart: 'Start Guided Tour',
    tourStarting: 'Starting your guided tour…',
    tourNext: 'Next',
    tourPrev: 'Back',
    tourFinish: 'Finish Tour',
    tourStep: (current: number, total: number) => `Step ${current} of ${total}`,
    tourClose: 'Close tour',

    // ─── Pages ───────────────────────────────────────────────────────────
    dashboard: {
      greeting: 'Good to see you',
      subtitle: 'Here is your health overview',
    },
    timeline: {
      title: 'Health Timeline',
      subtitle: 'Your medical history at a glance',
    },
    records: {
      title: 'Medical Records',
      subtitle: 'Your uploaded documents and reports',
    },
    medications: {
      title: 'Medications',
      subtitle: 'Your tracked medications and schedule',
    },
    upload: {
      title: 'Upload Center',
      subtitle: 'Add medical documents for AI analysis',
    },
    settings: {
      title: 'Settings',
      subtitle: 'Customise your CarePath experience',
    },

    // ─── Tour step labels ─────────────────────────────────────────────────
    tourSteps: {
      'dashboard-summary': {
        title: 'Health Overview',
        body: 'This card shows your latest health status and AI-generated summary.',
      },
      'quick-actions': {
        title: 'Quick Actions',
        body: 'Jump straight to uploading documents, viewing records, or starting an AI analysis.',
      },
      'upload-zone': {
        title: 'Upload Zone',
        body: 'Drag and drop or click to upload lab reports, prescriptions, or medical scans.',
      },
      'upload-docs': {
        title: 'Uploaded Documents',
        body: 'Documents you have uploaded appear here. The AI agents will process them.',
      },
      'agent-pipeline': {
        title: 'AI Agent Pipeline',
        body: 'CarePath runs 14 specialised AI agents in sequence to analyse your medical context.',
      },
      'agent-progress': {
        title: 'Agent Progress',
        body: 'Watch each agent complete its task in real time — from Intake to Follow-up.',
      },
      'timeline-events': {
        title: 'Timeline Events',
        body: 'Key health events are plotted chronologically so you can see your care journey.',
      },
      'records-list': {
        title: 'Your Records',
        body: 'All medical documents and reports are listed here with upload date and type.',
      },
      'language-selector': {
        title: 'Language',
        body: 'Switch between English, Hindi, and Hinglish. The Companion adapts immediately.',
      },
      'companion-prefs': {
        title: 'Companion Preferences',
        body: 'Control voice responses, history access, and medical term simplification.',
      },
      'start-tour': {
        title: 'Guided Tour',
        body: 'You can restart this guided tour any time from here.',
      },
    },
  },

  hi: {
    companion: 'CarePath सहायक',
    subtitle: 'आपका स्वास्थ्य साथी',
    placeholder: 'अपनी CarePath यात्रा के बारे में पूछें…',
    send: 'भेजें',
    listen: 'सुनें',
    stop: 'रोकें',
    clear: 'बातचीत हटाएं',
    voiceUnavailable: 'इस ब्राउज़र में आवाज़ से लिखना उपलब्ध नहीं है।',
    historyOff: 'CarePath इतिहास बंद है। मैं आपके सहेजे हुए स्वास्थ्य रिकॉर्ड का उपयोग नहीं करूंगा।',
    historyOn: 'मैं आपके CarePath रिकॉर्ड को समझने में मदद कर सकता हूँ।',
    thinking: 'सोच रहा हूँ…',
    navConfirm: 'अभी वहाँ ले जा रहा हूँ।',

    nav: {
      dashboard: 'डैशबोर्ड खोल रहा हूँ…',
      records: 'मेडिकल रिकॉर्ड खोल रहा हूँ…',
      timeline: 'टाइमलाइन खोल रहा हूँ…',
      medications: 'दवाइयाँ खोल रहा हूँ…',
      upload: 'अपलोड सेंटर खोल रहा हूँ…',
      settings: 'सेटिंग्स खोल रहा हूँ…',
      followup: 'फ़ॉलो-अप खोल रहा हूँ…',
      analysis: 'विश्लेषण खोल रहा हूँ…',
      journey: 'केयर जर्नी खोल रहा हूँ…',
      doctorBridge: 'डॉक्टर ब्रिज खोल रहा हूँ…',
    },

    tourStart: 'गाइडेड टूर शुरू करें',
    tourStarting: 'आपका गाइडेड टूर शुरू हो रहा है…',
    tourNext: 'अगला',
    tourPrev: 'पिछला',
    tourFinish: 'टूर समाप्त करें',
    tourStep: (current: number, total: number) => `चरण ${current} / ${total}`,
    tourClose: 'टूर बंद करें',

    dashboard: {
      greeting: 'आपसे मिलकर खुशी हुई',
      subtitle: 'यहाँ आपका स्वास्थ्य सारांश है',
    },
    timeline: {
      title: 'स्वास्थ्य टाइमलाइन',
      subtitle: 'आपका चिकित्सा इतिहास एक नज़र में',
    },
    records: {
      title: 'मेडिकल रिकॉर्ड',
      subtitle: 'आपके अपलोड किए गए दस्तावेज़ और रिपोर्ट',
    },
    medications: {
      title: 'दवाइयाँ',
      subtitle: 'आपकी दर्ज दवाइयाँ और समय-सारिणी',
    },
    upload: {
      title: 'अपलोड सेंटर',
      subtitle: 'AI विश्लेषण के लिए मेडिकल दस्तावेज़ जोड़ें',
    },
    settings: {
      title: 'सेटिंग्स',
      subtitle: 'अपना CarePath अनुभव अनुकूलित करें',
    },

    tourSteps: {
      'dashboard-summary': {
        title: 'स्वास्थ्य सारांश',
        body: 'यह कार्ड आपकी नवीनतम स्वास्थ्य स्थिति और AI सारांश दिखाता है।',
      },
      'quick-actions': {
        title: 'त्वरित क्रियाएँ',
        body: 'दस्तावेज़ अपलोड करें, रिकॉर्ड देखें, या AI विश्लेषण शुरू करें।',
      },
      'upload-zone': {
        title: 'अपलोड क्षेत्र',
        body: 'खींचें और छोड़ें या क्लिक करके लैब रिपोर्ट, प्रिस्क्रिप्शन अपलोड करें।',
      },
      'upload-docs': {
        title: 'अपलोड दस्तावेज़',
        body: 'आपके अपलोड दस्तावेज़ यहाँ दिखते हैं। AI एजेंट इन्हें प्रोसेस करेंगे।',
      },
      'agent-pipeline': {
        title: 'AI एजेंट पाइपलाइन',
        body: 'CarePath आपके मेडिकल संदर्भ को विश्लेषित करने के लिए 14 AI एजेंट चलाता है।',
      },
      'agent-progress': {
        title: 'एजेंट प्रगति',
        body: 'देखें कि प्रत्येक एजेंट अपना काम वास्तविक समय में कैसे पूरा करता है।',
      },
      'timeline-events': {
        title: 'टाइमलाइन घटनाएँ',
        body: 'प्रमुख स्वास्थ्य घटनाएँ कालानुक्रमिक रूप से दिखाई जाती हैं।',
      },
      'records-list': {
        title: 'आपके रिकॉर्ड',
        body: 'सभी मेडिकल दस्तावेज़ और रिपोर्ट यहाँ अपलोड दिनांक के साथ सूचीबद्ध हैं।',
      },
      'language-selector': {
        title: 'भाषा',
        body: 'अंग्रेजी, हिंदी और हिंग्लिश के बीच स्विच करें।',
      },
      'companion-prefs': {
        title: 'सहायक प्राथमिकताएँ',
        body: 'आवाज़ प्रतिक्रियाएँ, इतिहास पहुँच और मेडिकल शब्द सरलीकरण नियंत्रित करें।',
      },
      'start-tour': {
        title: 'गाइडेड टूर',
        body: 'आप यहाँ से कभी भी यह गाइडेड टूर फिर से शुरू कर सकते हैं।',
      },
    },
  },

  hl: {
    companion: 'CarePath Companion',
    subtitle: 'Aapka Health Companion',
    placeholder: 'Apni CarePath journey ke baare mein poochhen…',
    send: 'Bhejo',
    listen: 'Suno',
    stop: 'Roko',
    clear: 'Baat clear karo',
    voiceUnavailable: 'Is browser mein voice input available nahi hai.',
    historyOff: 'CarePath history off hai. Main aapke health records use nahi karunga.',
    historyOn: 'Main aapke CarePath records ko samajhne mein help kar sakta hoon.',
    thinking: 'Soch raha hoon…',
    navConfirm: 'Abhi wahan le jaata hoon.',

    nav: {
      dashboard: 'Dashboard khol raha hoon…',
      records: 'Medical Records khol raha hoon…',
      timeline: 'Timeline khol raha hoon…',
      medications: 'Medications khol raha hoon…',
      upload: 'Upload Center khol raha hoon…',
      settings: 'Settings khol raha hoon…',
      followup: 'Follow-up khol raha hoon…',
      analysis: 'Analysis khol raha hoon…',
      journey: 'Care Journey khol raha hoon…',
      doctorBridge: 'Doctor Bridge khol raha hoon…',
    },

    tourStart: 'Guided Tour Start Karo',
    tourStarting: 'Aapka guided tour shuru ho raha hai…',
    tourNext: 'Aage',
    tourPrev: 'Peeche',
    tourFinish: 'Tour Khatam Karo',
    tourStep: (current: number, total: number) => `Step ${current} / ${total}`,
    tourClose: 'Tour band karo',

    dashboard: {
      greeting: 'Welcome back',
      subtitle: 'Yahan aapka health overview hai',
    },
    timeline: {
      title: 'Health Timeline',
      subtitle: 'Aapki medical history ek nazar mein',
    },
    records: {
      title: 'Medical Records',
      subtitle: 'Aapke uploaded documents aur reports',
    },
    medications: {
      title: 'Medications',
      subtitle: 'Aapki davaiyaan aur schedule',
    },
    upload: {
      title: 'Upload Center',
      subtitle: 'AI analysis ke liye medical documents add karo',
    },
    settings: {
      title: 'Settings',
      subtitle: 'Apna CarePath experience customize karo',
    },

    tourSteps: {
      'dashboard-summary': {
        title: 'Health Overview',
        body: 'Yeh card aapki latest health status aur AI summary dikhata hai.',
      },
      'quick-actions': {
        title: 'Quick Actions',
        body: 'Documents upload karo, records dekho, ya AI analysis shuru karo.',
      },
      'upload-zone': {
        title: 'Upload Zone',
        body: 'Drag-drop ya click karke lab reports, prescriptions upload karo.',
      },
      'upload-docs': {
        title: 'Uploaded Documents',
        body: 'Aapke uploaded documents yahan dikhte hain. AI agents inhe process karenge.',
      },
      'agent-pipeline': {
        title: 'AI Agent Pipeline',
        body: 'CarePath 14 AI agents chalata hai aapka medical context analyse karne ke liye.',
      },
      'agent-progress': {
        title: 'Agent Progress',
        body: 'Dekho har agent apna kaam real-time mein kaise complete karta hai.',
      },
      'timeline-events': {
        title: 'Timeline Events',
        body: 'Important health events chronological order mein dikhaye jaate hain.',
      },
      'records-list': {
        title: 'Aapke Records',
        body: 'Saare medical documents aur reports yahan list hain upload date ke saath.',
      },
      'language-selector': {
        title: 'Language',
        body: 'English, Hindi, aur Hinglish mein switch karo.',
      },
      'companion-prefs': {
        title: 'Companion Preferences',
        body: 'Voice responses, history access, aur medical terms simplification control karo.',
      },
      'start-tour': {
        title: 'Guided Tour',
        body: 'Aap yahan se kabhii bhi yeh guided tour phir shuru kar sakte ho.',
      },
    },
  },
} as const;

export const t = (locale: Locale) => copy[locale];
