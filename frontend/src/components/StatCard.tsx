interface StatCardProps {
  title: string;
  value: number | string;
  type: 'number' | 'text';
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, type }) => {
  const displayValue = type === 'number' ? Number(value).toLocaleString() : value;
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <p className="mt-1 text-2xl font-semibold text-gray-900">{displayValue}</p>
    </div>
  );
}; 