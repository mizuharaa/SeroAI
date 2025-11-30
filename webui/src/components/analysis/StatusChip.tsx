import React from 'react';
import { CheckCircle2, Loader2, Clock } from 'lucide-react';

interface StatusChipProps {
  status: 'complete' | 'analyzing' | 'queued';
  className?: string;
}

export function StatusChip({ status, className = '' }: StatusChipProps) {
  const config = {
    complete: {
      icon: CheckCircle2,
      text: 'Complete',
      bg: 'bg-emerald-500/20 border-emerald-500/50',
      textColor: 'text-emerald-400',
      glow: 'shadow-emerald-500/50',
    },
    analyzing: {
      icon: Loader2,
      text: 'Analyzing',
      bg: 'bg-cyan-500/20 border-cyan-500/50',
      textColor: 'text-cyan-400',
      glow: 'shadow-cyan-500/50',
    },
    queued: {
      icon: Clock,
      text: 'Queued',
      bg: 'bg-slate-500/20 border-slate-500/50',
      textColor: 'text-slate-400',
      glow: 'shadow-slate-500/50',
    },
  };

  const { icon: Icon, text, bg, textColor, glow } = config[status];

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${bg} ${textColor} ${glow} shadow-lg text-xs font-semibold ${className}`}
    >
      {status === 'analyzing' ? (
        <Icon className="w-3 h-3 animate-spin" />
      ) : (
        <Icon className="w-3 h-3" />
      )}
      <span>{text}</span>
    </div>
  );
}

