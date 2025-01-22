import React, { useState } from 'react';
import { analyzeToken, analyzeSentiment } from '../services/api';
import { AnalysisParams, AnalysisResult } from '../types';
import { SentimentAnalysis, SentimentAnalysisParams } from '../types/sentiment';
import env from '../config/env';
import { SentimentAnalysis as SentimentDisplay } from './SentimentAnalysis';
import { TimeframeSelector } from './TimeframeSelector';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { TechnicalIndicators } from './TechnicalIndicators';
import { TechnicalAnalysis } from '../types/analysis';
import { SignalStatus } from './SignalStatus';
import { AdvancedIndicators } from './AdvancedIndicators';
import { AdvancedDCAStrategy } from './AdvancedDCAStrategy';
import { ExitSignals } from './ExitSignals';
import { transformDCARecommendations, transformAdvancedDCAStrategy } from '../utils/transformers';
import { PriceChart } from './PriceChart';
import { EntryZones } from './EntryZones';
import { validateAnalysisParams } from '../utils/validation';
import { getTechnicalSignals } from '../utils/technicalSignals';

export const TokenAnalysis: React.FC = () => {
  const [analysisParams, setAnalysisParams] = useState<AnalysisParams>({
    contractAddress: '',
    timeframe: '1h',
    intervalDays: 30,
    investmentAmount: 100,
  });

  const [sentimentParams, setSentimentParams] = useState<SentimentAnalysisParams>({
    telegram_channel: '',
    interval_days: 30,
    advanced_analysis: true
  });
  
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string[]>([]);
  const [sentimentLoading, setSentimentLoading] = useState(false);

  // Handle price & technical analysis
  const handleAnalyzeToken = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await analyzeToken(analysisParams);
      console.log('Raw API Response:', result);
      
      if (!result?.priceData?.price_history) {
        throw new Error('Invalid price data received');
      }
      
      // Transform the price data to match the PriceChart component's interface
      const transformedResult = {
        ...result,
        priceData: {
          current_price: result.priceData.price_history[result.priceData.price_history.length - 1]?.price || 0,
          price_history: result.priceData.price_history.map((point: any) => ({
            timestamp: point.timestamp,
            price: typeof point.price === 'string' ? parseFloat(point.price) : point.price,
            high: typeof point.high === 'string' ? parseFloat(point.high) : point.price,
            low: typeof point.low === 'string' ? parseFloat(point.low) : point.price
          }))
        }
      };
      
      console.log('Transformed result:', transformedResult);
      setAnalysisResult(transformedResult);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
      setError(errorMessage);
      console.error('Token analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Separate handler for sentiment analysis
  const handleAnalyzeSentiment = async () => {
    try {
      setSentimentLoading(true);
      setError(null);
      
      const result = await analyzeSentiment(sentimentParams);
      setSentimentData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze sentiment');
    } finally {
      setSentimentLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Sentiment Analysis Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Telegram Sentiment</h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telegram Channel
            </label>
            <input
              type="text"
              value={sentimentParams.telegram_channel}
              onChange={(e) => setSentimentParams(prev => ({
                ...prev,
                telegram_channel: e.target.value
              }))}
              className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
              placeholder="t.me/channel_name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interval Days
            </label>
            <input
              type="number"
              value={sentimentParams.interval_days}
              onChange={(e) => setSentimentParams(prev => ({
                ...prev,
                interval_days: Number(e.target.value)
              }))}
              className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="advancedAnalysis"
              checked={sentimentParams.advanced_analysis}
              onChange={(e) => setSentimentParams(prev => ({
                ...prev,
                advanced_analysis: e.target.checked
              }))}
              className="h-4 w-4 text-blue-600 rounded"
            />
            <label htmlFor="advancedAnalysis" className="ml-2 text-sm text-gray-700">
              Advanced Sentiment Analysis
            </label>
          </div>
        </div>

        <button
          onClick={handleAnalyzeSentiment}
          disabled={sentimentLoading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {sentimentLoading ? 'Analyzing Token Sentiment...' : 'Analyze Token Sentiment'}
        </button>
      </div>

      {/* Sentiment Analysis Results */}
      {sentimentData && (
        <SentimentDisplay 
          data={sentimentData}
          loading={sentimentLoading}
        />
      )}

      {/* Token Analysis Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Token Analysis Settings</h2>
        
        {/* Token Analysis Inputs */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contract Address
            </label>
            <input
              type="text"
              value={analysisParams.contractAddress}
              onChange={(e) => setAnalysisParams(prev => ({
                ...prev,
                contractAddress: e.target.value
              }))}
              className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
              placeholder="0x..."
            />
          </div>
          
          <TimeframeSelector
            timeframe={analysisParams.timeframe}
            intervalDays={analysisParams.intervalDays}
            investmentAmount={analysisParams.investmentAmount}
            onChange={(updates) => 
              setAnalysisParams(prev => ({ ...prev, ...updates }))
            }
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={handleAnalyzeToken}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Token'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Progress Display */}
        {progress.length > 0 && (
          <div className="mt-4 space-y-1">
            {progress.map((msg, i) => (
              <div key={i} className="text-sm text-gray-600">{msg}</div>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Results Section */}
      {analysisResult && analysisResult.priceData && (
        <>
          {/* Price Chart */}
          <div className="mb-8">
            <PriceChart 
              data={{
                current_price: analysisResult.priceData.current_price,
                price_history: analysisResult.priceData.price_history.map(point => ({
                  timestamp: point.timestamp,
                  price: point.price,
                  high: point.price * 1.001, // Fallback if high not available
                  low: point.price * 0.999   // Fallback if low not available
                }))
              }} 
            />
          </div>

          <div className="grid grid-cols-1 gap-6">
            {/* DCA Strategy with Signal Status */}
            <SignalStatus 
              analysis={analysisResult?.technical_analysis}
              currentPrice={analysisResult?.priceData.current_price}
            />

            {/* Technical Indicators */}
            <TechnicalIndicators
              analysis={analysisResult?.technical_analysis}
              currentPrice={analysisResult?.priceData.current_price}
            />

            {/* Entry Zones */}
            <EntryZones
              zones={transformDCARecommendations(
                analysisResult.technical_analysis,
                analysisResult.priceData.current_price,
                analysisParams.investmentAmount
              ).entry_points}
              currentPrice={analysisResult.priceData.current_price}
            />

            {/* Advanced Technical Analysis */}
            <AdvancedIndicators
              analysis={analysisResult?.technical_analysis}
            />

            {/* Advanced DCA Strategy */}
            {analysisResult?.technical_analysis.dca_recommendations && (
              <AdvancedDCAStrategy
                strategy={transformAdvancedDCAStrategy(
                  analysisResult.technical_analysis,
                  analysisParams.investmentAmount
                )}
                investmentAmount={analysisParams.investmentAmount}
              />
            )}

            {/* Exit Strategy */}
            {analysisResult?.technical_analysis.exit_signals && (
              <ExitSignals
                signals={analysisResult.technical_analysis.exit_signals}
                currentPrice={analysisResult.priceData.current_price}
                technicalSignals={{
                  macd: getTechnicalSignals(
                    analysisResult.technical_analysis,
                    analysisResult.priceData.current_price
                  ).macd_signal,
                  bb: getTechnicalSignals(
                    analysisResult.technical_analysis,
                    analysisResult.priceData.current_price
                  ).bb_signal
                }}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}; 

