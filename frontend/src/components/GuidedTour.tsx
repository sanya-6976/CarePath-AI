/**
 * GuidedTour — lightweight DOM-based interactive tour engine.
 *
 * How it works:
 *  1. When `isTourActive` is true, it collects all elements with [data-tour] on the current route.
 *  2. It renders a floating tooltip positioned near the target element.
 *  3. Keyboard: Escape = close, ArrowRight / Enter = next, ArrowLeft = prev.
 *  4. The target element is scrolled into view and highlighted with a ring.
 *  5. Multi-language: reads tourSteps from i18n based on current locale.
 *  6. Mobile-friendly: tooltip repositions to avoid viewport overflow.
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { ChevronLeft, ChevronRight, X, Map } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { usePreferences } from '../context/PreferencesContext';
import { t } from '../i18n';

interface TourStep {
  key: string;
  element: HTMLElement;
  title: string;
  body: string;
}

interface TooltipPosition {
  top: number;
  left: number;
  placement: 'top' | 'bottom' | 'left' | 'right';
}

function computePosition(el: HTMLElement): TooltipPosition {
  const rect = el.getBoundingClientRect();
  const tooltipW = 300;
  const tooltipH = 140;
  const gap = 12;
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  // Prefer bottom placement
  if (rect.bottom + tooltipH + gap < vh) {
    const left = Math.max(8, Math.min(rect.left + rect.width / 2 - tooltipW / 2, vw - tooltipW - 8));
    return { top: rect.bottom + gap + window.scrollY, left, placement: 'bottom' };
  }
  // Try top
  if (rect.top - tooltipH - gap > 0) {
    const left = Math.max(8, Math.min(rect.left + rect.width / 2 - tooltipW / 2, vw - tooltipW - 8));
    return { top: rect.top - tooltipH - gap + window.scrollY, left, placement: 'top' };
  }
  // Try right
  if (rect.right + tooltipW + gap < vw) {
    const top = Math.max(8, Math.min(rect.top + rect.height / 2 - tooltipH / 2, vh - tooltipH - 8));
    return { top: top + window.scrollY, left: rect.right + gap, placement: 'right' };
  }
  // Left
  const top = Math.max(8, Math.min(rect.top + rect.height / 2 - tooltipH / 2, vh - tooltipH - 8));
  return { top: top + window.scrollY, left: Math.max(8, rect.left - tooltipW - gap), placement: 'left' };
}

export default function GuidedTour() {
  const { isTourActive, endTour, locale } = usePreferences();
  const text = t(locale);
  const location = useLocation();

  const [steps, setSteps] = useState<TourStep[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [position, setPosition] = useState<TooltipPosition | null>(null);
  const highlightRef = useRef<HTMLElement | null>(null);
  const overlayRef = useRef<HTMLDivElement | null>(null);

  // Collect data-tour elements on the current page
  const collectSteps = useCallback(() => {
    const elements = Array.from(
      document.querySelectorAll<HTMLElement>('[data-tour]')
    );
    const stepDefs = (text as any).tourSteps as Record<string, { title: string; body: string }>;
    const collected: TourStep[] = elements
      .map((el) => {
        const key = el.getAttribute('data-tour') || '';
        const def = stepDefs?.[key];
        if (!def) return null;
        return { key, element: el, title: def.title, body: def.body };
      })
      .filter(Boolean) as TourStep[];
    return collected;
  }, [text]);

  // Re-collect steps whenever tour activates or route changes
  useEffect(() => {
    if (!isTourActive) {
      removeHighlight();
      setPosition(null);
      return;
    }
    // Small delay to let page render
    const timer = setTimeout(() => {
      const collected = collectSteps();
      setSteps(collected);
      setCurrentIndex(0);
    }, 200);
    return () => clearTimeout(timer);
  }, [isTourActive, location.pathname, collectSteps]);

  // Highlight & position tooltip on step change
  useEffect(() => {
    if (!isTourActive || steps.length === 0) return;
    const step = steps[currentIndex];
    if (!step) return;

    // Scroll element into view
    step.element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Apply highlight ring after scroll
    setTimeout(() => {
      removeHighlight();
      step.element.style.outline = '3px solid rgb(139 92 246)';
      step.element.style.outlineOffset = '4px';
      step.element.style.borderRadius = '8px';
      step.element.style.transition = 'outline 0.2s';
      step.element.style.zIndex = '9998';
      step.element.style.position = step.element.style.position || 'relative';
      highlightRef.current = step.element;

      const pos = computePosition(step.element);
      setPosition(pos);
    }, 350);
  }, [currentIndex, steps, isTourActive]);

  function removeHighlight() {
    if (highlightRef.current) {
      highlightRef.current.style.outline = '';
      highlightRef.current.style.outlineOffset = '';
      highlightRef.current.style.zIndex = '';
      highlightRef.current = null;
    }
  }

  // Keyboard navigation
  useEffect(() => {
    if (!isTourActive) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { handleClose(); }
      else if (e.key === 'ArrowRight' || e.key === 'Enter') { handleNext(); }
      else if (e.key === 'ArrowLeft') { handlePrev(); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isTourActive, currentIndex, steps.length]);

  function handleClose() {
    removeHighlight();
    endTour();
  }

  function handleNext() {
    if (currentIndex < steps.length - 1) {
      setCurrentIndex((i) => i + 1);
    } else {
      handleClose();
    }
  }

  function handlePrev() {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
    }
  }

  if (!isTourActive || steps.length === 0 || !position) return null;

  const step = steps[currentIndex];
  const isLast = currentIndex === steps.length - 1;
  const totalLabel = typeof text.tourStep === 'function'
    ? text.tourStep(currentIndex + 1, steps.length)
    : `${currentIndex + 1} / ${steps.length}`;

  return (
    <>
      {/* Dark overlay backdrop — low opacity so user sees the page */}
      <div
        ref={overlayRef}
        className="fixed inset-0 z-[9990] pointer-events-none"
        style={{ background: 'rgba(30,20,50,0.25)' }}
        aria-hidden="true"
      />

      {/* Tooltip */}
      <div
        role="dialog"
        aria-modal="false"
        aria-label="Guided tour step"
        style={{
          position: 'absolute',
          top: position.top,
          left: position.left,
          width: 300,
          zIndex: 9999,
        }}
        className="rounded-2xl bg-white border border-brand-lavender/30 shadow-2xl p-4 flex flex-col gap-3 animate-in fade-in slide-in-from-bottom-2 duration-200"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-lavender-light text-brand-lavender flex items-center justify-center shrink-0">
              <Map className="w-3.5 h-3.5" />
            </div>
            <span className="font-display font-bold text-sm text-brand-plum leading-tight">
              {step.title}
            </span>
          </div>
          <button
            onClick={handleClose}
            aria-label={text.tourClose}
            className="rounded-lg p-1 hover:bg-brand-bg text-brand-slate shrink-0 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <p className="text-xs text-brand-slate leading-relaxed">
          {step.body}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between gap-2 pt-1 border-t border-brand-slate/10">
          <span className="text-xxs text-brand-slate/70 font-medium">{totalLabel}</span>
          <div className="flex gap-1.5">
            {currentIndex > 0 && (
              <button
                onClick={handlePrev}
                aria-label={text.tourPrev}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-brand-slate hover:bg-brand-bg transition-colors"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                {text.tourPrev}
              </button>
            )}
            <button
              onClick={handleNext}
              aria-label={isLast ? text.tourFinish : text.tourNext}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-brand-lavender text-white hover:opacity-90 transition-opacity"
            >
              {isLast ? text.tourFinish : text.tourNext}
              {!isLast && <ChevronRight className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
