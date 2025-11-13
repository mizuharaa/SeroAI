import React, { type ButtonHTMLAttributes, type PropsWithChildren } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'sm' | 'lg' | 'default'
}

export function Button({ variant = 'default', size = 'default', className = '', children, ...rest }: PropsWithChildren<ButtonProps>) {
  const base = 'inline-flex items-center justify-center rounded-lg transition-all'
  const variants = {
    default: 'bg-gray-900 text-white hover:bg-gray-800',
    outline: 'border border-gray-300 text-gray-900 bg-white hover:bg-gray-50',
    ghost: 'text-gray-700 hover:bg-gray-100'
  }[variant]
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    default: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }[size]
  return (
    <button className={`${base} ${variants} ${sizes} ${className}`} {...rest}>
      {children}
    </button>
  )
}


