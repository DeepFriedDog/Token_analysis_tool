import React, { useState } from 'react';
import { TokenInput } from './TokenInput';
import { TimeframeSelector } from './TimeframeSelector';
import { PriceChart } from './PriceChart';
import { AdvancedIndicatorsPanel } from './AdvancedIndicators';
import { AdvancedDCAStrategy } from './AdvancedDCAStrategy';
import { ExitStrategy } from './ExitStrategy';
import { validateAnalysisParams, ValidationError } from '../utils/validation';
import { AnalysisResult, TechnicalAnalysis } from '../types/analysis';
import { analyzeToken, AnalysisParams, analyzeSentiment } from '../services/api';
import env from '../config/env';
import { TechnicalRecommendations } from './TechnicalRecommendations';
import { DCAStrategy } from './DCAStrategy';
import { SentimentAnalysis as SentimentAnalysisComponent } from './SentimentAnalysis';
import { SentimentAnalysis, SentimentAnalysisParams } from '../types/sentiment';

type TechnicalSignal = {
  macd_signal: 'buy' | 'sell' | 'neutral';
  rsi_signal: 'overbought' | 'oversold' | 'neutral';
  bb_signal: 'upper_break' | 'lower_break' | 'neutral';
};

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
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [sentimentParams, setSentimentParams] = useState<SentimentAnalysisParams>({
    telegram_channel: '',
    interval_days: 30
  });
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis | null>(null);

  const handleAnalyze = async () => {
    let ws: WebSocket | null = null;
    
    try {
      setLoading(true);
      setError(null);
      setProgress([]);
      setValidationErrors([]);
      
      const errors = validateAnalysisParams(analysisParams);
      if (errors.length > 0) {
        setValidationErrors(errors);
        setError(errors[0].message);
        return;
      }

      // Connect to WebSocket
      try {
        ws = new WebSocket(`${env.WS_URL}/ws/analysis`);
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          if (message.type === 'progress') {
            setProgress(prev => [...prev, message.data]);
          }
        };
      } catch (wsError) {
        console.warn('WebSocket connection failed:', wsError);
      }

      // Run token analysis
      console.log('Sending analysis request with params:', analysisParams);
      const result = await analyzeToken(analysisParams);
      
      if (!result || !result.priceData || !result.technical_analysis) {
        throw new Error('Invalid response format from API');
      }

      setAnalysisResult(result);

      // Run sentiment analysis if telegram channel is provided
      if (sentimentParams.telegram_channel) {
        try {
          const sentimentResult = await analyzeSentiment(sentimentParams);
          setSentimentData(sentimentResult);
        } catch (sentimentError) {
          console.error('Sentiment analysis error:', sentimentError);
          // Don't throw error here to avoid interrupting the main analysis flow
        }
      }
      
    } catch (err) {
      console.error('Analysis error:', err);
      if (err instanceof Error) {
        setError(err.message);
        setAnalysisResult(null);
        setSentimentData(null);
      } else {
        setError('An unexpected error occurred while analyzing the token');
      }
    } finally {
      setLoading(false);
      if (ws && ws.readyState === WebSocket.OPEN) {
        try {
          ws.close();
        } catch (closeError) {
          console.warn('Error closing WebSocket:', closeError);
        }
      }
    }
  };

  const getFieldError = (field: string): string | undefined => {
    return validationErrors.find(error => error.field === field)?.message;
  };

  const currentPrice = analysisResult?.priceData[analysisResult.priceData.length - 1]?.close;

  const getTechnicalSignals = (analysis: TechnicalAnalysis | undefined, price: number | undefined): TechnicalSignal => {
    if (!analysis?.advanced_indicators || !price) {
      return {
        macd_signal: 'neutral',
        rsi_signal: 'neutral',
        bb_signal: 'neutral'
      };
    }

    const { advanced_indicators: ai } = analysis;

    let macdSignal: TechnicalSignal['macd_signal'] = 'neutral';
    if (ai.macd) {
      macdSignal = ai.macd.line > ai.macd.signal ? 'buy' : 'sell';
    }

    let rsiSignal: TechnicalSignal['rsi_signal'] = 'neutral';
    if (ai.rsi) {
      if (ai.rsi > 70) rsiSignal = 'overbought';
      else if (ai.rsi < 30) rsiSignal = 'oversold';
    }

    let bbSignal: TechnicalSignal['bb_signal'] = 'neutral';
    if (ai.bollinger_bands) {
      if (ai.bollinger_bands.upper > price) bbSignal = 'upper_break';
      else if (ai.bollinger_bands.lower > price) bbSignal = 'lower_break';
    }

    return {
      macd_signal: macdSignal,
      rsi_signal: rsiSignal,
      bb_signal: bbSignal
    };
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <TokenInput 
          value={analysisParams.contractAddress}
          onChange={(value) => setAnalysisParams(prev => ({...prev, contractAddress: value}))}
          error={getFieldError('contractAddress')}
        />
        <TimeframeSelector
          timeframe={analysisParams.timeframe}
          intervalDays={analysisParams.intervalDays}
          investmentAmount={analysisParams.investmentAmount}
          onChange={(updates) => setAnalysisParams(prev => ({...prev, ...updates}))}
          errors={{
            timeframe: getFieldError('timeframe'),
            intervalDays: getFieldError('intervalDays'),
            investmentAmount: getFieldError('investmentAmount')
          }}
        />
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Telegram Channel URL (optional)
          </label>
          <input
            type="text"
            value={sentimentParams.telegram_channel}
            onChange={(e) => setSentimentParams(prev => ({...prev, telegram_channel: e.target.value}))}
            placeholder="e.g., https://t.me/channelname"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        
        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        <button 
          onClick={handleAnalyze}
          disabled={loading}
          className={`w-full mt-4 px-4 py-2 rounded-md text-white font-medium ${
            loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {loading ? 'Analyzing...' : 'Analyze Token'}
        </button>
      </div>
      
      {analysisResult && (
        <div className="space-y-6">
          <PriceChart 
            data={analysisResult.priceData} 
            loading={loading} 
          />
          
          {currentPrice && (
            <>
              <DCAStrategy
                analysis={analysisResult.technical_analysis}
                currentPrice={currentPrice}
                investmentAmount={analysisParams.investmentAmount}
                strategy={{
                  entry_points: (analysisResult.dca_strategy?.entry_points || []).map(point => ({
                    ...point,
                    position_size: 0
                  })),
                  exit_points: analysisResult.dca_strategy?.exit_points || [],
                  risk_score: analysisResult.dca_strategy?.risk_tolerance || 0,
                  expected_return: analysisResult.dca_strategy?.expected_return || 0,
                  investment_distribution: analysisResult.dca_strategy?.position_sizes || []
                }}
              />
              
              {sentimentData && (
                <SentimentAnalysisComponent 
                  data={sentimentData}
                  loading={loading}
                />
              )}
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AdvancedIndicatorsPanel 
                  indicators={analysisResult.technical_analysis.advanced_indicators}
                  currentPrice={currentPrice}
                />
                {analysisResult.dca_strategy && (
                  <AdvancedDCAStrategy 
                    strategy={analysisResult.dca_strategy}
                    investmentAmount={analysisParams.investmentAmount}
                  />
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}; 
