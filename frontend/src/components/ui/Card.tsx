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
  image?: string;
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
            <button 
              onClick={onAddToLibrary}
              className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add to Library
            </button>
            <button 
              onClick={onViewDetails}
              className="px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              View Details
            </button>
          </div>
        </div>
        {image && (
          <div className="w-64 h-48 flex-shrink-0">
            <img
              src={image}
              alt={title}
              className="w-full h-full object-cover rounded-lg"
            />
          </div>
        )}
      </div>
    </Card>
  );
};
