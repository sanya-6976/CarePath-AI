import { useState } from 'react';
import { Link } from 'react-router-dom';
import { usePreferences } from '../context/PreferencesContext';
import type { LanguageType, TextSizeType } from '../context/PreferencesContext';
import { Globe, Bell, Eye, User, Check, ChevronDown } from 'lucide-react';

export default function SettingsPage() {
  const {
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
  } = usePreferences();

  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [textSizeDropdownOpen, setTextSizeDropdownOpen] = useState(false);

  const toggleLangDropdown = () => setLangDropdownOpen(!langDropdownOpen);
  const toggleTextSizeDropdown = () => setTextSizeDropdownOpen(!textSizeDropdownOpen);

  const selectLanguage = (lang: LanguageType) => {
    setLanguage(lang);
    setLangDropdownOpen(false);
  };

  const selectTextSize = (size: TextSizeType) => {
    setTextSize(size);
    setTextSizeDropdownOpen(false);
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 animate-in fade-in duration-300 pb-16">
      
      {/* 1. LANGUAGE & COMMUNICATION CARD */}
      <section className="bg-brand-card border border-brand-slate/10 rounded-2xl p-6 shadow-xs flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-brand-slate/10 pb-3">
          <div className="w-8 h-8 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center">
            <Globe className="w-4.5 h-4.5" />
          </div>
          <div>
            <h2 className="font-display font-bold text-base text-brand-plum">Language & Communication</h2>
            <p className="text-xxs text-brand-slate font-light">Set your preferred translation and message style.</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-2">
          <div>
            <label className="text-sm font-semibold text-brand-plum block">Language</label>
            <span className="text-xs text-brand-slate font-light">Choose the language you prefer for your CarePath experience.</span>
          </div>

          {/* Custom Select Box */}
          <div className="relative w-full sm:w-48">
            <button
              onClick={toggleLangDropdown}
              className="w-full flex items-center justify-between bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-sm font-medium text-brand-plum hover:border-brand-lavender hover:bg-brand-card transition-all text-left outline-none cursor-pointer"
            >
              <span>{language}</span>
              <ChevronDown className={`w-4 h-4 text-brand-slate transition-transform ${langDropdownOpen ? 'rotate-180' : ''}`} />
            </button>
            {langDropdownOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setLangDropdownOpen(false)} />
                <div className="absolute right-0 mt-2 w-full bg-brand-card border border-brand-slate/15 rounded-xl shadow-md overflow-hidden z-25 animate-in fade-in slide-in-from-top-1 duration-150">
                  {(['English', 'Hindi', 'Hinglish'] as LanguageType[]).map((lang) => (
                    <button
                      key={lang}
                      onClick={() => selectLanguage(lang)}
                      className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-left hover:bg-brand-bg text-brand-plum transition-all cursor-pointer font-medium"
                    >
                      <span>{lang}</span>
                      {language === lang && <Check className="w-4 h-4 text-brand-lavender" />}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* 2. NOTIFICATIONS CARD */}
      <section className="bg-brand-card border border-brand-slate/10 rounded-2xl p-6 shadow-xs flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-brand-slate/10 pb-3">
          <div className="w-8 h-8 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center">
            <Bell className="w-4.5 h-4.5" />
          </div>
          <div>
            <h2 className="font-display font-bold text-base text-brand-plum">Notifications</h2>
            <p className="text-xxs text-brand-slate font-light">Choose how and when CarePath reminds you of your schedule.</p>
          </div>
        </div>

        <div className="flex flex-col gap-4 divide-y divide-brand-slate/5">
          {/* Item 1 */}
          <div className="flex items-center justify-between pt-1">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">Follow-up reminders</span>
              <span className="text-xs text-brand-slate font-light">Stay prompted to log daily check-ins and recovery milestones.</span>
            </div>
            <button
              onClick={() => setFollowUpReminders(!followUpReminders)}
              aria-label="Toggle Follow-up reminders"
              className={`w-11 h-6 rounded-full transition-all relative ${
                followUpReminders ? 'bg-brand-lavender' : 'bg-brand-slate/20'
              } cursor-pointer`}
            >
              <div
                className={`w-4.5 h-4.5 rounded-full bg-white absolute top-0.75 left-0.75 transition-all shadow-xs ${
                  followUpReminders ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>

          {/* Item 2 */}
          <div className="flex items-center justify-between pt-3">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">Appointment reminders</span>
              <span className="text-xs text-brand-slate font-light">Receive warnings before consultations with matched specialists.</span>
            </div>
            <button
              onClick={() => setAppointmentReminders(!appointmentReminders)}
              aria-label="Toggle Appointment reminders"
              className={`w-11 h-6 rounded-full transition-all relative ${
                appointmentReminders ? 'bg-brand-lavender' : 'bg-brand-slate/20'
              } cursor-pointer`}
            >
              <div
                className={`w-4.5 h-4.5 rounded-full bg-white absolute top-0.75 left-0.75 transition-all shadow-xs ${
                  appointmentReminders ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>

          {/* Item 3 */}
          <div className="flex items-center justify-between pt-3">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">Recovery updates</span>
              <span className="text-xs text-brand-slate font-light">Get alerts when AI agents update your diagnostic path mapping.</span>
            </div>
            <button
              onClick={() => setRecoveryUpdates(!recoveryUpdates)}
              aria-label="Toggle Recovery updates"
              className={`w-11 h-6 rounded-full transition-all relative ${
                recoveryUpdates ? 'bg-brand-lavender' : 'bg-brand-slate/20'
              } cursor-pointer`}
            >
              <div
                className={`w-4.5 h-4.5 rounded-full bg-white absolute top-0.75 left-0.75 transition-all shadow-xs ${
                  recoveryUpdates ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>
        </div>
      </section>

      {/* 3. ACCESSIBILITY CARD ("Make CarePath easier to use") */}
      <section className="bg-brand-card border border-brand-slate/10 rounded-2xl p-6 shadow-xs flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-brand-slate/10 pb-3">
          <div className="w-8 h-8 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center">
            <Eye className="w-4.5 h-4.5" />
          </div>
          <div>
            <h2 className="font-display font-bold text-base text-brand-plum">Make CarePath easier to use</h2>
            <p className="text-xxs text-brand-slate font-light">Configure view settings for better visibility and interface control.</p>
          </div>
        </div>

        <div className="flex flex-col gap-4 divide-y divide-brand-slate/5">
          {/* Dropdown Selector */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">Text size</span>
              <span className="text-xs text-brand-slate font-light">Scale page fonts to make reading descriptions easier.</span>
            </div>

            <div className="relative w-full sm:w-48">
              <button
                onClick={toggleTextSizeDropdown}
                className="w-full flex items-center justify-between bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-2.5 text-sm font-medium text-brand-plum hover:border-brand-lavender hover:bg-brand-card transition-all text-left outline-none cursor-pointer"
              >
                <span>{textSize}</span>
                <ChevronDown className={`w-4 h-4 text-brand-slate transition-transform ${textSizeDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              {textSizeDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setTextSizeDropdownOpen(false)} />
                  <div className="absolute right-0 mt-2 w-full bg-brand-card border border-brand-slate/15 rounded-xl shadow-md overflow-hidden z-25 animate-in fade-in slide-in-from-top-1 duration-150">
                    {(['Standard', 'Large', 'Extra Large'] as TextSizeType[]).map((size) => (
                      <button
                        key={size}
                        onClick={() => selectTextSize(size)}
                        className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-left hover:bg-brand-bg text-brand-plum transition-all cursor-pointer font-medium"
                      >
                        <span>{size}</span>
                        {textSize === size && <Check className="w-4 h-4 text-brand-lavender" />}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Switch 1 */}
          <div className="flex items-center justify-between pt-3">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">Reduced motion</span>
              <span className="text-xs text-brand-slate font-light">Limit moving layout elements and text animations.</span>
            </div>
            <button
              onClick={() => setReducedMotion(!reducedMotion)}
              aria-label="Toggle Reduced motion"
              className={`w-11 h-6 rounded-full transition-all relative ${
                reducedMotion ? 'bg-brand-lavender' : 'bg-brand-slate/20'
              } cursor-pointer`}
            >
              <div
                className={`w-4.5 h-4.5 rounded-full bg-white absolute top-0.75 left-0.75 transition-all shadow-xs ${
                  reducedMotion ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>

          {/* Switch 2 */}
          <div className="flex items-center justify-between pt-3">
            <div>
              <span className="text-sm font-semibold text-brand-plum block">High contrast</span>
              <span className="text-xs text-brand-slate font-light">Increase visual clarity of text headers and border lines.</span>
            </div>
            <button
              onClick={() => setHighContrast(!highContrast)}
              aria-label="Toggle High contrast"
              className={`w-11 h-6 rounded-full transition-all relative ${
                highContrast ? 'bg-brand-lavender' : 'bg-brand-slate/20'
              } cursor-pointer`}
            >
              <div
                className={`w-4.5 h-4.5 rounded-full bg-white absolute top-0.75 left-0.75 transition-all shadow-xs ${
                  highContrast ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>
        </div>
      </section>


      {/* 5. GENERAL CARD */}
      <section className="bg-brand-card border border-brand-slate/10 rounded-2xl p-6 shadow-xs flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-brand-slate/10 pb-3">
          <div className="w-8 h-8 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center">
            <User className="w-4.5 h-4.5" />
          </div>
          <div>
            <h2 className="font-display font-bold text-base text-brand-plum">General</h2>
            <p className="text-xxs text-brand-slate font-light">Update generic details related to your account profile.</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
          <div>
            <span className="text-sm font-semibold text-brand-plum block">Profile preferences</span>
            <span className="text-xs text-brand-slate font-light">Change your personal name, gender, or listed allergies.</span>
          </div>
          <Link
            to="/profile"
            className="px-4 py-2 bg-brand-lavender hover:bg-brand-lavender-hover text-white rounded-xl text-xs font-semibold shadow-xs transition-all w-full sm:w-auto text-center"
          >
            Manage profile
          </Link>
        </div>
      </section>

    </div>
  );
}
