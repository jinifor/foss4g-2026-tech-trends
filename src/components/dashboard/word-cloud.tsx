import { useMemo } from "react";

import { cn } from "@/lib/utils";
import type { KeywordCountItem } from "@/types/dashboard";

function polarPosition(index: number, total: number) {
  const angle = index * 137.5 * (Math.PI / 180);
  const radius = Math.sqrt(index / Math.max(total, 1)) * 42;
  return {
    x: 50 + Math.cos(angle) * radius,
    y: 50 + Math.sin(angle) * radius * 0.82,
    rotate: ((index % 7) - 3) * 6,
  };
}

export function WordCloud({
  words,
  className,
  maxWords = 48,
}: {
  words: KeywordCountItem[];
  className?: string;
  maxWords?: number;
}) {
  const layout = useMemo(() => {
    const max = Math.max(...words.map((word) => word.count), 1);
    const min = Math.min(...words.map((word) => word.count), 1);
    return words.slice(0, maxWords).map((word, index) => {
      const pos = polarPosition(index, words.length);
      const ratio = max === min ? 1 : (word.count - min) / (max - min);
      return {
        ...word,
        left: `${pos.x}%`,
        top: `${pos.y}%`,
        fontSize: `${16 + ratio * 30}px`,
        rotate: pos.rotate,
        opacity: 0.68 + ratio * 0.32,
      };
    });
  }, [maxWords, words]);

  return (
    <div className={cn("relative min-h-[420px] overflow-hidden rounded-[1.75rem] border border-border/60 bg-white/65", className)}>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(23,126,137,0.10),transparent_22%),radial-gradient(circle_at_80%_18%,rgba(217,108,61,0.10),transparent_20%),radial-gradient(circle_at_55%_75%,rgba(122,143,60,0.10),transparent_25%)]" />
      {layout.map((word) => (
        <span
          key={word.keyword}
          title={`${word.keyword}: ${word.count} talks`}
          className="absolute rounded-full px-2 py-1 font-semibold text-foreground/90 transition-transform duration-200 hover:scale-105"
          style={{
            left: word.left,
            top: word.top,
            fontSize: word.fontSize,
            transform: `translate(-50%, -50%) rotate(${word.rotate}deg)`,
            opacity: word.opacity,
            background: indexGradient(word.keyword),
          }}
        >
          {word.keyword}
        </span>
      ))}
    </div>
  );
}

function indexGradient(keyword: string) {
  const hash = Array.from(keyword).reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const palettes = [
    "rgba(23,126,137,0.12)",
    "rgba(217,108,61,0.12)",
    "rgba(122,143,60,0.12)",
    "rgba(124,92,255,0.12)",
  ];
  return palettes[hash % palettes.length];
}
