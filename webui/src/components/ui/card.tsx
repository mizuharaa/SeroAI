import React, { type PropsWithChildren, type HTMLAttributes } from 'react'

export function Card({ className = '', children, ...rest }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div className={`rounded-xl border ${className}`} {...rest}>
      {children}
    </div>
  )
}


