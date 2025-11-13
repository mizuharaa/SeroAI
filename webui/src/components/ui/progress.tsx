import React, { type HTMLAttributes, type PropsWithChildren } from 'react';

interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
}

export function Progress({ value, className = '', ...rest }: PropsWithChildren<ProgressProps>) {
  return (
    <div className={`w-full h-2 bg-gray-200 rounded-full overflow-hidden ${className}`} {...rest}>
      <div
        className="h-full bg-gradient-to-r from-orange-500 via-rose-500 to-pink-600 rounded-full transition-all"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  );
}

