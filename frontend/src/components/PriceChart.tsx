import React, { useEffect } from 'react';
import { formatPrice } from '../utils/format';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface Props {
  data: {
    current_price: number;
    price_history: Array<{
      timestamp: number;
      price: number;
      high: number;
      low: number;
    }>;
  };
}

export const PriceChart: React.FC<Props> = ({ data }) => {
  useEffect(() => {
    console.log('PriceChart raw data:', data);
  }, [data]);

  if (!data?.price_history?.length) {
    console.log('No price history available');
    return <div className="bg-white p-6 rounded-lg shadow mb-8">No price history available</div>;
  }

  const chartData = data.price_history.map(point => ({
    timestamp: typeof point.timestamp === 'string' ? Number(point.timestamp) : point.timestamp,
    price: typeof point.price === 'string' ? Number(point.price) : point.price,
    high: typeof point.high === 'string' ? Number(point.high) : point.high,
    low: typeof point.low === 'string' ? Number(point.low) : point.low
  }));

  const formatTooltipDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Price History</h2>
      <div style={{ width: '100%', height: 300, minWidth: '300px' }}>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart 
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp"
              type="number"
              domain={['auto', 'auto']}
              scale="time"
              tickFormatter={(timestamp) => {
                const date = new Date(timestamp);
                return date.toLocaleDateString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: '2-digit'
                });
              }}
            />
            <YAxis 
              tickFormatter={(value) => `$${formatPrice(value)}`}
            />
            <Tooltip 
              formatter={(value: number) => [`$${formatPrice(value)}`, 'Price']}
              labelFormatter={formatTooltipDate}
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="#3B82F6" 
              fill="#3B82F6" 
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}; 