interface StatCardProps {
  title: string;
  value: number | null | undefined;
  type: 'number' | 'percentage';
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, type }) => {
  const formattedValue = value === null || value === undefined
    ? 'N/A'
    : type === 'percentage'
      ? `${value.toFixed(2)}%`
      : value.toLocaleString();

  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <h4 className="text-sm font-medium text-gray-500">{title}</h4>
      <div className="mt-2 text-2xl font-semibold text-gray-900">
        {formattedValue}
      </div>
    </div>
  );
}; 