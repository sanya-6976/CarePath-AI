import { useRef, useEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface SplitTextProps {
  text: string;
  className?: string;
  delay?: number;
  duration?: number;
  ease?: string;
  splitType?: 'chars' | 'words';
  from?: gsap.TweenVars;
  to?: gsap.TweenVars;
  threshold?: number;
  rootMargin?: string;
  textAlign?: 'left' | 'center' | 'right';
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'div';
  onLetterAnimationComplete?: () => void;
}

export default function SplitText({
  text,
  className = '',
  delay = 50,
  duration = 1.25,
  ease = 'power3.out',
  splitType = 'chars',
  from = { opacity: 0, y: 40 },
  to = { opacity: 1, y: 0 },
  threshold = 0.1,
  rootMargin = '-100px',
  textAlign = 'center',
  tag = 'p',
  onLetterAnimationComplete
}: SplitTextProps) {
  const ref = useRef<HTMLParagraphElement>(null);
  const animationCompletedRef = useRef(false);
  const [fontsLoaded, setFontsLoaded] = useState(false);

  useEffect(() => {
    if (document.fonts.status === 'loaded') {
      setFontsLoaded(true);
    } else {
      document.fonts.ready.then(() => {
        setFontsLoaded(true);
      });
    }
  }, []);

  useEffect(() => {
    if (!ref.current || !text || !fontsLoaded) return;
    if (animationCompletedRef.current) return;

    const el = ref.current;
    
    let targets: NodeListOf<Element> | Element[] = [];
    if (splitType === 'chars') {
      targets = el.querySelectorAll('.split-char');
    } else {
      targets = el.querySelectorAll('.split-word');
    }

    const startPct = (1 - threshold) * 100;
    const marginMatch = /^(-?\d+(?:\.\d+)?)(px|em|rem|%)?$/.exec(rootMargin);
    const marginValue = marginMatch ? parseFloat(marginMatch[1]) : 0;
    const marginUnit = marginMatch ? marginMatch[2] || 'px' : 'px';
    const sign =
      marginValue === 0
        ? ''
        : marginValue < 0
          ? `-=${Math.abs(marginValue)}${marginUnit}`
          : `+=${marginValue}${marginUnit}`;
    const start = `top ${startPct}%${sign}`;

    const tween = gsap.fromTo(
      targets,
      { ...from },
      {
        ...to,
        duration,
        ease,
        stagger: delay / 1000,
        scrollTrigger: {
          trigger: el,
          start,
          once: true,
          fastScrollEnd: true,
          anticipatePin: 0.4
        },
        onComplete: () => {
          animationCompletedRef.current = true;
          onLetterAnimationComplete?.();
        },
        willChange: 'transform, opacity',
        force3D: true
      }
    );

    return () => {
      ScrollTrigger.getAll().forEach(st => {
        if (st.trigger === el) st.kill();
      });
      tween.kill();
    };
  }, [text, delay, duration, ease, splitType, threshold, rootMargin, fontsLoaded, onLetterAnimationComplete, from, to]);

  const Tag = tag;
  const style = {
    textAlign,
    overflow: 'hidden' as const,
    display: 'inline-block' as const,
    whiteSpace: 'normal' as const,
    wordWrap: 'break-word' as const,
    willChange: 'transform, opacity'
  };

  const renderContent = () => {
    const words = text.split(' ');
    return words.map((word, wordIdx) => (
      <span key={wordIdx} className="split-word inline-block whitespace-nowrap">
        {word.split('').map((char, charIdx) => (
          <span key={charIdx} className="split-char inline-block" style={{ willChange: 'transform, opacity' }}>
            {char}
          </span>
        ))}
        {wordIdx < words.length - 1 ? '\u00A0' : ''}
      </span>
    ));
  };

  return (
    <Tag ref={ref as any} style={style} className={`split-parent ${className}`}>
      {renderContent()}
    </Tag>
  );
}
