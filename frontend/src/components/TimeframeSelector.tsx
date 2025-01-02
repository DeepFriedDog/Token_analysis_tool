import React from 'react';

interface TimeframeSelectorProps {
  timeframe: string;
  intervalDays: number;
  investmentAmount: number;
  onChange: (updates: Partial<{
    timeframe: string;
    intervalDays: number;
    investmentAmount: number;
  }>) => void;
  errors?: {
    timeframe?: string;
    intervalDays?: string;
    investmentAmount?: string;
  };
  disabled?: boolean;
}

export const TimeframeSelector: React.FC<TimeframeSelectorProps> = ({
  timeframe,
  intervalDays,
  investmentAmount,
  onChange,
  errors,
  disabled
}) => {
  const timeframes = [
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timeframe
        </label>
        <select
          value={timeframe}
          onChange={(e) => onChange({ timeframe: e.target.value })}
          disabled={disabled}
          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
            disabled ? 'bg-gray-100 cursor-not-allowed' : ''
          }`}
        >
          {timeframes.map((tf) => (
            <option key={tf.value} value={tf.value}>
              {tf.label}
            </option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Analysis Period (Days)
        </label>
        <input
          type="number"
          value={intervalDays}
          onChange={(e) => onChange({ intervalDays: parseInt(e.target.value) })}
          min="1"
          max="365"
          disabled={disabled}
          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
            disabled ? 'bg-gray-100 cursor-not-allowed' : ''
          }`}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Investment Amount (USD)
        </label>
        <input
          type="number"
          value={investmentAmount}
          onChange={(e) => onChange({ investmentAmount: parseFloat(e.target.value) })}
          min="0"
          step="0.01"
          disabled={disabled}
          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
            disabled ? 'bg-gray-100 cursor-not-allowed' : ''
          }`}
        />
      </div>
    </div>
  );
}; 