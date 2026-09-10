import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonVariant = 'primary' | 'secondary' | 'success'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  children: ReactNode
}

const variantClass: Record<ButtonVariant, string> = {
  primary:
    'w-full bg-gradient-to-r from-violet-600 to-orange-500 text-white hover:opacity-95 disabled:opacity-50',
  secondary: 'bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50',
  success: 'bg-green-600 text-white hover:bg-green-700 disabled:opacity-50',
}

export function Button({
  variant = 'primary',
  className = '',
  children,
  type = 'button',
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`rounded-md px-4 py-2.5 text-sm font-semibold transition ${variantClass[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
