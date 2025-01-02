import React, { useState } from 'react';
import { analyzeToken, analyzeSentiment } from '../services/api';
import { AnalysisParams, AnalysisResult } from '../types';
import { SentimentAnalysis, SentimentAnalysisParams } from '../types/sentiment';
import env from '../config/env';
import { TechnicalRecommendations } from './TechnicalRecommendations';
import { SentimentAnalysis as SentimentDisplay } from './SentimentAnalysis';

export const TokenAnalysis: React.FC = () => {
  const [analysisParams, setAnalysisParams] = useState<AnalysisParams>({
    contractAddress: '',
    timeframe: '1h',
    intervalDays: 30,
    investmentAmount: 100,
  });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string[]>([]);
  const [sentimentParams, setSentimentParams] = useState<SentimentAnalysisParams>({
    telegram_channel: '',
    interval_days: 30,
    advanced_analysis: false
  });
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis | null>(null);

  // Handle price & technical analysis
  const handleAnalyzeToken = async () => {
    let ws: WebSocket | null = null;
    try {
      setLoading(true);
      setError(null);
      setProgress([]);

      // (Optional) open WebSocket connection for progress updates.
      try {
        ws = new WebSocket(`${env.WS_URL}/ws/analysis`);
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          if (message.type === 'progress') {
            setProgress((prev) => [...prev, message.data]);
          }
        };
      } catch (wsError) {
        console.warn('WebSocket connection failed:', wsError);
      }

      console.log('Sending token analysis request with params:', analysisParams);
      const result = await analyzeToken(analysisParams);

      if (!result || !result.priceData || !result.technical_analysis) {
        throw new Error('Invalid response format from API');
      }

      setAnalysisResult(result);
    } catch (error: any) {
      setError(error.message || 'Analysis failed');
      console.error('Token analysis error:', error);
    } finally {
      setLoading(false);
      if (ws) {
        ws.close();
      }
    }
  };

  // Handle sentiment analysis only
  const handleAnalyzeSentiment = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!sentimentParams.telegram_channel) {
        setError('Please provide a Telegram channel to analyze.');
        return;
      }

      console.log('Sending sentiment analysis request with params:', sentimentParams);
      const sentimentResult = await analyzeSentiment(sentimentParams);
      setSentimentData(sentimentResult);
    } catch (error: any) {
      setError(error.message || 'Sentiment analysis failed');
      console.error('Sentiment analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-6">Token Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contract Address
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                value={analysisParams.contractAddress}
                onChange={(e) =>
                  setAnalysisParams({ ...analysisParams, contractAddress: e.target.value })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Timeframe
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                value={analysisParams.timeframe}
                onChange={(e) => setAnalysisParams({ ...analysisParams, timeframe: e.target.value })}
              >
                <option value="15m">15m</option>
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interval Days
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                value={analysisParams.intervalDays}
                onChange={(e) =>
                  setAnalysisParams({ ...analysisParams, intervalDays: parseInt(e.target.value, 10) })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Investment Amount
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                value={analysisParams.investmentAmount}
                onChange={(e) =>
                  setAnalysisParams({ ...analysisParams, investmentAmount: parseFloat(e.target.value) })
                }
              />
            </div>

            <button
              onClick={handleAnalyzeToken}
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              Analyze Token
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-6">Telegram Sentiment</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telegram Channel
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              value={sentimentParams.telegram_channel}
              onChange={(e) =>
                setSentimentParams({ ...sentimentParams, telegram_channel: e.target.value })
              }
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interval Days
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              value={sentimentParams.interval_days}
              onChange={(e) =>
                setSentimentParams({ ...sentimentParams, interval_days: parseInt(e.target.value, 10) })
              }
            />
          </div>

          <div className="relative flex items-start mt-4">
            <div className="flex items-center h-5">
              <input
                id="advanced-mode"
                type="checkbox"
                checked={sentimentParams.advanced_analysis}
                onChange={(e) => 
                  setSentimentParams({ ...sentimentParams, advanced_analysis: e.target.checked })
                }
                className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3 text-sm">
              <label htmlFor="advanced-mode" className="font-medium text-gray-700">
                Advanced Sentiment Analysis
              </label>
              <p className="text-gray-500 group relative">
                Enable detailed engagement metrics
                <span className="invisible group-hover:visible absolute left-0 bottom-6 w-72 bg-gray-900 text-white text-xs rounded p-2">
                  Advanced mode includes detailed member activity analysis, reaction patterns, and user engagement metrics. 
                  This analysis takes significantly longer but provides comprehensive insights into community behavior.
                  Features: member activity tracking, reaction analysis, engagement patterns, and user rankings.
                </span>
              </p>
            </div>
          </div>

          <button
            onClick={handleAnalyzeSentiment}
            disabled={loading}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            Analyze Token Sentiment
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {loading && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <p className="text-blue-700">Loading...</p>
        </div>
      )}

      {progress.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          {progress.map((p, idx) => (
            <div key={idx} className="text-gray-600">{p}</div>
          ))}
        </div>
      )}

      {analysisResult && (
        <div className="bg-white rounded-lg shadow p-6">
          <TechnicalRecommendations 
            analysis={{
              trend_analysis: analysisResult.technical_analysis.trend_analysis,
              dca_recommendations: analysisResult.technical_analysis.dca_recommendations,
              support_levels: [],
              resistance_levels: [],
              rsi: 0,
              volatility: 0,
              macd: {
                line: 0,
                signal: 0,
                histogram: 0
              }
            }}
            currentPrice={analysisResult.priceData.current_price} 
          />
        </div>
      )}

      {sentimentData && (
        <div className="bg-white rounded-lg shadow p-6">
          <SentimentDisplay data={sentimentData} loading={false} />
        </div>
      )}
    </div>
  );
}; 
