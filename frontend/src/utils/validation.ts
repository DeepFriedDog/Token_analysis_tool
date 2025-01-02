import { ethers } from 'ethers';

export interface ValidationError {
  field: string;
  message: string;
}

export const validateAnalysisParams = (params: {
  contractAddress: string;
  timeframe: string;
  intervalDays: number;
  investmentAmount: number;
}): ValidationError[] => {
  const errors: ValidationError[] = [];

  // Validate contract address
  if (!params.contractAddress) {
    errors.push({ field: 'contractAddress', message: 'Contract address is required' });
  } else if (!ethers.isAddress(params.contractAddress)) {
    errors.push({ field: 'contractAddress', message: 'Invalid Ethereum address format' });
  }

  // Validate timeframe
  const validTimeframes = ['15m', '1h', '4h', '1d'];
  if (!validTimeframes.includes(params.timeframe)) {
    errors.push({ field: 'timeframe', message: 'Invalid timeframe selection' });
  }

  // Validate interval days
  if (params.intervalDays < 1 || params.intervalDays > 365) {
    errors.push({ field: 'intervalDays', message: 'Interval must be between 1 and 365 days' });
  }

  // Validate investment amount
  if (params.investmentAmount <= 0) {
    errors.push({ field: 'investmentAmount', message: 'Investment amount must be positive' });
  }

  return errors;
}; 