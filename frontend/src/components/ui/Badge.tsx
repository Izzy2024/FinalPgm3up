import React from 'react';
import { clsx } from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  active?: boolean;
  clickable?: boolean;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  active = false,
  clickable = false,
  onClick,
}) => {
  const variants = {
    default: active
      ? 'bg-blue-600 text-white'
      : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    primary: 'bg-blue-100 text-blue-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
  };
  
  return (
    <span
      onClick={onClick}
      className={clsx(
        'inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-colors',
        variants[variant],
        (onClick || clickable) && 'cursor-pointer',
        'select-none'
      )}
    >
      {children}
    </span>
  );
};
