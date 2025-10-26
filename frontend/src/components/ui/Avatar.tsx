import React from 'react';
import { clsx } from 'clsx';

interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
  fallback?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = 'User',
  name,
  size = 'md',
  fallback,
}) => {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
  };
  
  const getInitials = (fullName: string) => {
    const names = fullName.trim().split(' ');
    if (names.length === 1) return names[0].charAt(0).toUpperCase();
    return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
  };
  
  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={clsx('rounded-full object-cover', sizes[size])}
      />
    );
  }
  
  return (
    <div
      className={clsx(
        'rounded-full bg-blue-600 text-white font-medium flex items-center justify-center',
        sizes[size]
      )}
    >
      {fallback || (name ? getInitials(name) : alt.charAt(0).toUpperCase())}
    </div>
  );
};
