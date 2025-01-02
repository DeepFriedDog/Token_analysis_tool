import axios from 'axios';
import { AnalysisResult } from '../types/analysis';
import env from '../config/env';
import { SentimentAnalysis, SentimentAnalysisParams } from '../types/sentiment';
import React, { useState } from 'react';

const api = axios.create({
  baseURL: env.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalysisParams {
  contractAddress: string;
  timeframe: string;
  intervalDays: number;
  investmentAmount: number;
}

export const analyzeToken = async (params: AnalysisParams): Promise<AnalysisResult> => {
  try {
    const requestData = {
      contract_address: params.contractAddress,
      timeframe: params.timeframe,
      interval_days: params.intervalDays,
      investment_amount: params.investmentAmount
    };
    
    console.log('API Request:', requestData);
    const { data } = await api.post('/api/analyze', requestData);
    console.log('API Response:', data);
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    if (!data.priceData || !data.technical_analysis) {
      throw new Error('Invalid response format from API');
    }
    
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Analysis failed';
      throw new Error(errorMessage);
    }
    throw error;
  }
};

export const analyzeSentiment = async (params: SentimentAnalysisParams): Promise<SentimentAnalysis> => {
  try {
    const requestData = {
      telegram_channel: params.telegram_channel,
      interval_days: params.interval_days
    };
    
    const { data } = await api.post('/api/analyze-sentiment', requestData);
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Sentiment analysis failed';
      throw new Error(errorMessage);
    }
    throw error;
  }
}; 