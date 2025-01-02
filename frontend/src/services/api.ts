import axios from 'axios';
import { AnalysisParams, AnalysisResult, SentimentAnalysis, SentimentAnalysisParams } from '../types';
import env from '../config/env';

const api = axios.create({
  baseURL: env.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    
    return data as AnalysisResult;
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

    console.log('API Request:', requestData);
    const { data } = await api.post('/api/analyze-sentiment', requestData);
    console.log('API Response:', data);
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    if (!data.channel_stats || 
        !data.sentiment_metrics || 
        !data.engagement_metrics || 
        !data.topic_analysis) {
      throw new Error('Invalid response format from API');
    }
    
    if (typeof data.channel_stats.total_members === 'undefined' ||
        typeof data.channel_stats.active_members === 'undefined' ||
        typeof data.channel_stats.messages_per_day === 'undefined') {
      throw new Error('Missing required channel statistics');
    }
    
    if (typeof data.sentiment_metrics.positive_percentage === 'undefined' ||
        typeof data.sentiment_metrics.negative_percentage === 'undefined' ||
        typeof data.sentiment_metrics.neutral_percentage === 'undefined' ||
        !Array.isArray(data.sentiment_metrics.sentiment_trend)) {
      throw new Error('Missing required sentiment metrics');
    }
    
    return data as SentimentAnalysis;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Sentiment analysis failed';
      throw new Error(errorMessage);
    }
    throw error;
  }
}; 