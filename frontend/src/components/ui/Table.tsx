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
