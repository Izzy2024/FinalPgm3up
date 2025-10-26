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
