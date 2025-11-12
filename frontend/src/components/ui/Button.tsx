import React from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'neon' | 'neonGreen';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  icon?: React.ReactNode;
  loading?: boolean;
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  loading = false,
  children,
  className,
  disabled,
  type = 'button',
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow-md',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    neon: 'relative overflow-hidden text-white shadow-neon focus:ring-pink-500 bg-gradient-to-r from-[#00ffd5] via-[#7c3aed] to-[#ff00e6] bg-[length:200%_200%] animate-gradient-x',
    neonGreen: 'relative overflow-hidden text-white shadow-neon focus:ring-emerald-500 bg-gradient-to-r from-[#22c55e] via-[#06b6d4] to-[#84cc16] bg-[length:200%_200%] animate-gradient-x',
  };
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      ref={ref}
      type={type}
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        (disabled || loading) && 'opacity-50 cursor-not-allowed',
        (variant === 'neon' || variant === 'neonGreen') && 'animate-glow',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {variant === 'neon' && (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shine"
        />
      )}
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {icon && !loading && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export const IconButton: React.FC<{
  icon: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ icon, onClick, variant = 'ghost', size = 'md', className }) => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };
  
  const variants = {
    primary: 'text-blue-600 hover:bg-blue-50',
    secondary: 'text-gray-600 hover:bg-gray-100',
    ghost: 'text-gray-500 hover:text-gray-700 hover:bg-gray-100',
  };
  
  return (
    <button
      onClick={onClick}
      className={clsx(
        'inline-flex items-center justify-center rounded-lg transition-colors',
        sizes[size],
        variants[variant],
        className
      )}
    >
      {icon}
    </button>
  );
};
