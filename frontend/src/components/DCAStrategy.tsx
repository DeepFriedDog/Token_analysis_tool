import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';
import { TechnicalAnalysis } from '../types/analysis';
import { CheckCircleIcon, InformationCircleIcon } from '@heroicons/react/solid';

interface DCAStrategyProps {
  analysis: TechnicalAnalysis;
  currentPrice: number;
  investmentAmount: number;
  strategy?: {
    entry_points: Array<{
      price: number;
      percentage: number;
      position_size: number;
      strength?: number;
    }>;
    exit_points: Array<{ price: number; percentage: number }>;
    risk_score: number;
    expected_return: number;
    investment_distribution: Array<{
      amount: number;
      price_target: number;
    }>;
  };
}

const Tooltip: React.FC<{ text: string }> = ({ text }) => (
  <div className="ml-2 group relative inline-block">
    <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <div className="hidden group-hover:block absolute z-10 w-64 p-2 mt-1 text-sm bg-gray-900 text-white rounded shadow-lg">
      {text}
    </div>
  </div>
);

const SignalIndicator: React.FC<{ active: boolean; label: string; tooltip: string }> = ({ active, label, tooltip }) => (
  <div className="flex items-center space-x-2">
    <div className={`w-3 h-3 rounded-full ${active ? 'bg-green-500' : 'bg-red-500'}`} />
    <span className="text-sm">{label}</span>
    <Tooltip text={tooltip} />
  </div>
);

export const DCAStrategy: React.FC<DCAStrategyProps> = ({ analysis, currentPrice, strategy, investmentAmount }) => {
  if (!strategy || !analysis) {
    return (
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">DCA Strategy</h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-gray-500">No DCA strategy data available</p>
        </div>
      </div>
    );
  }

  const { advanced_indicators: ai } = analysis;
  
  // Individual signals with explanations
  const signals = {
    rsi: {
      active: ai?.rsi ? ai.rsi < 30 : false,
      label: "RSI Oversold",
      tooltip: "RSI below 30 indicates oversold conditions, suggesting a potential bounce"
    },
    macd: {
      active: ai?.macd ? ai.macd.line > ai.macd.signal : false,
      label: "MACD Bullish",
      tooltip: "MACD line above signal line indicates upward momentum"
    },
    bollinger: {
      active: ai?.bollinger_bands ? currentPrice < ai.bollinger_bands.lower : false,
      label: "Below BB",
      tooltip: "Price below lower Bollinger Band suggests oversold conditions"
    },
    movingAverage: {
      active: ai?.ema_20 && ai?.sma_50 ? ai.ema_20 > ai.sma_50 : false,
      label: "MA Bullish",
      tooltip: "20 EMA above 50 SMA indicates upward trend"
    }
  };

  const allSignalsGreen = Object.values(signals).every(s => s.active);

  // Calculate position sizes based on total investment and signal strength
  const totalStrength = strategy.entry_points.reduce((sum, point) => sum + (point.strength || 1), 0);
  const adjustedEntryPoints = strategy.entry_points.map(point => ({
    ...point,
    position_size: Number(((investmentAmount * (point.strength || 1)) / totalStrength).toFixed(2))
  }));

  return (
    <div className="mb-8">
      <div className="flex items-center">
        <h2 className="text-xl font-semibold">DCA Strategy</h2>
        {allSignalsGreen && (
          <div className="ml-3 flex items-center text-green-600">
            <CheckCircleIcon className="w-5 h-5 mr-1" />
            <span className="text-sm">All signals aligned</span>
          </div>
        )}
      </div>

      {/* Signal Status Section */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <div className="flex items-center mb-3">
          <h3 className="font-medium">Signal Status</h3>
          <Tooltip text="Combined technical signals indicate market conditions" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(signals).map(([key, signal]) => (
            <SignalIndicator key={key} {...signal} />
          ))}
        </div>
      </div>

      {/* Technical Indicators Section */}
      <div className="bg-white p-6 rounded-lg shadow mb-4">
        <div className="flex items-center mb-4">
          <h3 className="text-lg font-semibold">Technical Indicators</h3>
          <Tooltip text="Key technical indicators used for analysis" />
        </div>
        <div className="grid grid-cols-2 gap-6">
          <div className="p-4 border rounded-lg">
            <div className="flex items-center mb-3">
              <span className="text-base font-medium">MACD</span>
              <Tooltip text="Moving Average Convergence Divergence (MACD) shows trend direction and momentum. Bullish when MACD line crosses above signal line." />
            </div>
            <div className="space-y-2 text-base">
              <div className="flex justify-between">
                <span className="text-gray-600">Line:</span>
                <span>${formatPrice(ai?.macd?.line ?? 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Signal:</span>
                <span>${formatPrice(ai?.macd?.signal ?? 0)}</span>
              </div>
            </div>
          </div>
          
          <div className="p-4 border rounded-lg">
            <div className="flex items-center mb-3">
              <span className="text-base font-medium">Bollinger Bands</span>
              <Tooltip text="Statistical boundaries around price. Price below lower band suggests oversold conditions." />
            </div>
            <div className="space-y-2 text-base">
              <div className="flex justify-between">
                <span className="text-gray-600">Upper:</span>
                <span>${formatPrice(ai.bollinger_bands.upper)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Lower:</span>
                <span>${formatPrice(ai.bollinger_bands.lower)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Entry Points Section */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex items-center mb-3">
          <h3 className="font-medium">Entry Points</h3>
          <Tooltip text="Position sizes are weighted by signal strength and total to exactly your investment amount" />
        </div>
        <div className="space-y-2">
          {adjustedEntryPoints.map((point, i) => (
            <div key={i} className="flex justify-between items-center">
              <span>Price: ${formatPrice(point.price)}</span>
              <div className="flex items-center space-x-4">
                <span className="text-green-600">(-{formatPercentage(point.percentage)}%)</span>
                <span className="text-sm text-gray-600">${formatPrice(point.position_size)}</span>
                <div className="w-16 bg-gray-200 rounded-full h-1.5">
                  <div 
                    className="bg-green-500 h-1.5 rounded-full"
                    style={{ width: `${((point.strength || 1) / totalStrength) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 