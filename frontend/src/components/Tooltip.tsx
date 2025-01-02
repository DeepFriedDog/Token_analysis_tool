import React from 'react';

interface TooltipProps {
  text: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ text }) => {
  return (
    <div className="group relative inline-block ml-2">
      <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-sm text-white rounded-md absolute left-1/2 -translate-x-1/2 translate-y-full mt-1 px-2 py-1 pointer-events-none w-48 text-center">
        {text}
      </div>
    </div>
  );
}; 