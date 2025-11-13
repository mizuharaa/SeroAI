import React, { type HTMLAttributes, type PropsWithChildren } from 'react';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary';
}

export function Badge({ variant = 'default', className = '', children, ...rest }: PropsWithChildren<BadgeProps>) {
  const styles =
    variant === 'default'
      ? 'inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-900 text-white'
      : 'inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-800';
  return (
    <span className={`${styles} ${className}`} {...rest}>
      {children}
    </span>
  );
}

