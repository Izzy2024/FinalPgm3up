# 🎨 SIGRAA - Código de Componentes UI Base

Este documento contiene los componentes base necesarios para la implementación UX de clase mundial.

---

## 📋 Índice de Componentes

1. Button Component
2. Card Component
3. Input Component
4. Badge Component
5. Table Components
6. Dropdown Component
7. Progress Component
8. Avatar Component

---

## 1. Button Component

**Archivo**: `frontend/src/components/ui/Button.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  icon?: React.ReactNode;
  loading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  loading = false,
  children,
  className,
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow-md',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        (disabled || loading) && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
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
};

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
```

---

## 2. Card Component

**Archivo**: `frontend/src/components/ui/Card.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  padding = 'md',
  hover = false,
}) => {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-gray-200 shadow-sm',
        paddings[padding],
        hover && 'transition-shadow duration-200 hover:shadow-md',
        className
      )}
    >
      {children}
    </div>
  );
};

export const RecommendationCard: React.FC<{
  title: string;
  description: string;
  image: string;
  onAddToLibrary: () => void;
  onViewDetails: () => void;
}> = ({ title, description, image, onAddToLibrary, onViewDetails }) => {
  return (
    <Card padding="lg" hover>
      <div className="flex gap-8">
        <div className="flex-1">
          <h3 className="text-2xl font-semibold text-gray-900 mb-3">
            {title}
          </h3>
          <p className="text-gray-600 leading-relaxed mb-6">
            {description}
          </p>
          <div className="flex gap-3">
            <Button onClick={onAddToLibrary}>
              Add to Library
            </Button>
            <Button variant="secondary" onClick={onViewDetails}>
              View Details
            </Button>
          </div>
        </div>
        <div className="w-64 h-48 flex-shrink-0">
          <img
            src={image}
            alt={title}
            className="w-full h-full object-cover rounded-lg"
          />
        </div>
      </div>
    </Card>
  );
};
```

---

## 3. Input Component

**Archivo**: `frontend/src/components/ui/Input.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  fullWidth = false,
  className,
  ...props
}) => {
  return (
    <div className={clsx('flex flex-col gap-1.5', fullWidth && 'w-full')}>
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          className={clsx(
            'w-full px-4 py-2.5 border rounded-lg transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            error
              ? 'border-red-300 focus:ring-red-500'
              : 'border-gray-300 hover:border-gray-400',
            icon && 'pl-10',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export const SearchInput: React.FC<{
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
}> = ({ placeholder, value, onChange, className }) => {
  return (
    <div className={clsx('relative', className)}>
      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder || 'Search...'}
        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-colors"
      />
    </div>
  );
};

export const Textarea: React.FC<{
  label?: string;
  error?: string;
  rows?: number;
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>> = ({
  label,
  error,
  rows = 4,
  className,
  ...props
}) => {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <textarea
        rows={rows}
        className={clsx(
          'w-full px-4 py-2.5 border rounded-lg transition-colors resize-none',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          error
            ? 'border-red-300 focus:ring-red-500'
            : 'border-gray-300 hover:border-gray-400',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
```

---

## 4. Badge Component

**Archivo**: `frontend/src/components/ui/Badge.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  active?: boolean;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  active = false,
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
        onClick && 'cursor-pointer',
        'select-none'
      )}
    >
      {children}
    </span>
  );
};
```

---

## 5. Table Components

**Archivo**: `frontend/src/components/ui/Table.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

export const Table: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  return (
    <div className="overflow-x-auto">
      <table className={clsx('min-w-full divide-y divide-gray-200', className)}>
        {children}
      </table>
    </div>
  );
};

export const TableHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <thead className="bg-gray-50">
      <tr>{children}</tr>
    </thead>
  );
};

export const TableColumn: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  return (
    <th
      className={clsx(
        'px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider',
        className
      )}
    >
      {children}
    </th>
  );
};

export const TableBody: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>;
};

export const TableRow: React.FC<{ children: React.ReactNode; onClick?: () => void }> = ({
  children,
  onClick,
}) => {
  return (
    <tr
      onClick={onClick}
      className={clsx(
        'transition-colors',
        onClick && 'cursor-pointer hover:bg-gray-50'
      )}
    >
      {children}
    </tr>
  );
};

export const TableCell: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  return (
    <td className={clsx('px-6 py-4 text-sm text-gray-900', className)}>
      {children}
    </td>
  );
};
```

---

## 6. Dropdown Component

**Archivo**: `frontend/src/components/ui/Dropdown.tsx`

```typescript
import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

interface DropdownProps {
  label: string;
  options: { value: string; label: string }[];
  value?: string;
  onChange?: (value: string) => void;
}

export const Dropdown: React.FC<DropdownProps> = ({
  label,
  options,
  value,
  onChange,
}) => {
  const selectedOption = options.find(opt => opt.value === value);
  
  return (
    <Menu as="div" className="relative inline-block text-left">
      <Menu.Button className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
        {selectedOption?.label || label}
        <ChevronDownIcon className="w-4 h-4" />
      </Menu.Button>
      
      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
          <div className="py-1">
            {options.map((option) => (
              <Menu.Item key={option.value}>
                {({ active }) => (
                  <button
                    onClick={() => onChange?.(option.value)}
                    className={clsx(
                      'block w-full text-left px-4 py-2 text-sm',
                      active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                    )}
                  >
                    {option.label}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
};
```

---

## 7. Progress Component

**Archivo**: `frontend/src/components/ui/Progress.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';
import { CheckIcon } from '@heroicons/react/24/solid';

interface ProgressProps {
  filename: string;
  progress: number;
  complete?: boolean;
}

export const ProgressItem: React.FC<ProgressProps> = ({
  filename,
  progress,
  complete = false,
}) => {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">{filename}</span>
        {complete ? (
          <span className="flex items-center gap-1 text-sm text-green-600">
            <CheckIcon className="w-4 h-4" />
            Complete
          </span>
        ) : (
          <span className="text-sm text-gray-500">{progress}%</span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full transition-all duration-300',
            complete ? 'bg-green-500' : 'bg-blue-600'
          )}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};
```

---

## 8. Avatar Component

**Archivo**: `frontend/src/components/ui/Avatar.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
  fallback?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = 'User',
  size = 'md',
  fallback,
}) => {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
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
      {fallback || alt.charAt(0).toUpperCase()}
    </div>
  );
};
```

---

## 9. Barrel Export

**Archivo**: `frontend/src/components/ui/index.ts`

```typescript
export { Button, IconButton } from './Button';
export { Card, RecommendationCard } from './Card';
export { Input, SearchInput, Textarea } from './Input';
export { Badge } from './Badge';
export { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from './Table';
export { Dropdown } from './Dropdown';
export { ProgressItem } from './Progress';
export { Avatar } from './Avatar';
```

---

## 🎨 Archivo de Tokens CSS

**Archivo**: `frontend/src/styles/tokens.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Colors */
    --color-primary: 37 99 235;
    --color-primary-hover: 29 78 216;
    --color-primary-light: 219 234 254;
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 0.75rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    
    /* Border Radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.375rem;
    --radius-lg: 0.5rem;
    --radius-xl: 0.75rem;
    --radius-2xl: 1rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  }
  
  body {
    @apply font-sans antialiased bg-gray-50 text-gray-900;
  }
  
  h1 {
    @apply text-4xl font-bold tracking-tight;
  }
  
  h2 {
    @apply text-3xl font-semibold tracking-tight;
  }
  
  h3 {
    @apply text-2xl font-semibold;
  }
  
  h4 {
    @apply text-xl font-semibold;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

---

## 📦 Configuración de Tailwind

**Archivo**: `frontend/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

---

**Fecha de Creación**: Octubre 24, 2025
**Componentes Listos**: 8 componentes base
**Estado**: Listo para usar
**Next**: Implementar en páginas
