export const formatPrice = (price: number | undefined | null): string => {
  if (price === undefined || price === null) return 'N/A';
  return price.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
    useGrouping: false
  });
};

export const formatPercentage = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(1);
}; 