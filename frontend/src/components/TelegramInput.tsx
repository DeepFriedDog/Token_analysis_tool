interface TelegramInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

export const TelegramInput: React.FC<TelegramInputProps> = ({ value, onChange, error }) => {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Telegram Channel URL
      </label>
      <div className="mt-1">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="e.g., https://t.me/channelname"
          className={`block w-full rounded-md shadow-sm ${
            error 
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
          } sm:text-sm`}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}; 