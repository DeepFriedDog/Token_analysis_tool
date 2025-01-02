import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';
import { ValueType, NameType } from 'recharts/types/component/DefaultTooltipContent';

interface PriceData {
  timestamp: string;
  close: number;
  volume?: number;
}

interface PriceChartProps {
  data?: PriceData[];
  loading?: boolean;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<ValueType, NameType>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 border border-gray-200 shadow-lg rounded">
        <p className="text-sm text-gray-600">
          {new Date(label).toLocaleString()}
        </p>
        <p className="text-sm font-semibold text-blue-600">
          Price: ${Number(payload[0].value).toFixed(8)}
        </p>
      </div>
    );
  }
  return null;
};

export const PriceChart: React.FC<PriceChartProps> = ({ data = [], loading }) => {
  if (loading) {
    return (
      <div className="h-96 w-full mb-8 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500">Loading price data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-96 w-full mb-8 flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">No price data available</p>
      </div>
    );
  }

  const formattedData = data.map(point => ({
    ...point,
    timestamp: new Date(point.timestamp).getTime(),
    price: Number(point.close || 0),
    close: Number(point.close || 0)
  }));

  return (
    <div className="h-96 w-full mb-8 bg-white p-4 rounded-lg shadow">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={formattedData}>
          <XAxis 
            dataKey="timestamp" 
            type="number"
            domain={['auto', 'auto']}
            tickFormatter={(timestamp) => new Date(timestamp).toLocaleDateString()}
          />
          <YAxis 
            domain={['auto', 'auto']}
            tickFormatter={(value) => `$${value.toFixed(4)}`}
          />
          <Tooltip 
            content={<CustomTooltip />}
            cursor={{ stroke: '#2563eb', strokeWidth: 1 }}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke="#2563eb"
            fill="#3b82f6"
            fillOpacity={0.2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}; 