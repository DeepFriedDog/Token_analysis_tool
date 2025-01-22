import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { AnalysisParams, AnalysisResult, SentimentAnalysis, SentimentAnalysisParams } from '../types';
import env from '../config/env';

// Extend AxiosRequestConfig to include retry count
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  retryCount?: number;
}

const api = axios.create({
  baseURL: env.API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,  // 2 minutes
  withCredentials: true
});

// Retry logic with exponential backoff
let retryDelay = 1000; // Start with 1 second
const maxRetries = 3;

api.interceptors.response.use(undefined, async (err: AxiosError) => {
  const config = err.config as CustomAxiosRequestConfig;
  
  if (!config) {
    return Promise.reject(err);
  }

  config.retryCount = config.retryCount ?? 0;

  if (config.retryCount < maxRetries) {
    config.retryCount += 1;
    
    // Exponential backoff
    const delay = retryDelay * Math.pow(2, config.retryCount - 1);
    console.log(`Retrying request (${config.retryCount}/${maxRetries}) after ${delay}ms...`);
    
    return new Promise(resolve => {
      setTimeout(() => resolve(api.request(config)), delay);
    });
  }

  return Promise.reject(err);
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

    // Match the backend response structure from api.py
    const priceHistory = data.priceData?.price_history?.map((point: any) => ({
      timestamp: point.timestamp,
      price: parseFloat(point.price || point.value || '0'),
      high: parseFloat(point.high || point.formatted?.high || point.value || '0'),
      low: parseFloat(point.low || point.formatted?.low || point.value || '0')
    })) || [];

    const transformedData: AnalysisResult = {
      priceData: {
        current_price: parseFloat(data.priceData?.current_price || '0'),
        price_history: priceHistory
      },
      technical_analysis: {
        trend_analysis: data.technical_analysis?.trend_analysis || { 
          primary_trend: 'neutral', 
          strength: 0 
        },
        dca_recommendations: data.technical_analysis?.dca_recommendations || {
          entry_zones: [],
          risk_assessment: { overall_risk: 0 }
        },
        advanced_indicators: data.technical_analysis?.advanced_indicators || {},
        exit_signals: data.technical_analysis?.exit_signals || []
      }
    };

    if (!transformedData.priceData.price_history.length) {
      console.error('Raw price data:', data.priceData);
      throw new Error('No price data available for the specified token');
    }
    
    return transformedData;
  } catch (error) {
    console.error('API Error:', error);
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Unable to connect to the API server. Please check if the server is running.');
      }
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. The analysis is taking longer than expected. Please try again.');
      }
      const message = error.response?.data?.error || error.message || 'Analysis failed';
      throw new Error(message);
    }
    throw error;
  }
};

export const analyzeSentiment = async (params: SentimentAnalysisParams): Promise<SentimentAnalysis> => {
  try {
    const requestData = {
      telegram_channel: params.telegram_channel,
      interval_days: params.interval_days,
      advanced_analysis: params.advanced_analysis
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