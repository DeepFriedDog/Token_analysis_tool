import React from 'react';
import { formatPrice, formatPercentage } from '../utils/formatters';
import { TechnicalAnalysis } from '../types/analysis';

interface Props {
  analysis: TechnicalAnalysis;
  currentPrice: number;
}

interface EntryZone {
  price: number;
  strength: number;
  confidence: number;
  reasoning: string[];
}

export const TechnicalRecommendations: React.FC<Props> = ({ analysis, currentPrice }) => {
  // Early return if no analysis data
  if (!analysis) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">DCA Recommendations</h2>
        <p className="text-gray-500">Loading analysis...</p>
      </div>
    );
  }

  const { dca_recommendations, trend_analysis } = analysis;

  // If no recommendations or trend analysis available
  if (!dca_recommendations && !trend_analysis) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">DCA Recommendations</h2>
        <p className="text-gray-500">No recommendations available</p>
      </div>
    );
  }

  const hasEntryZones = dca_recommendations?.entry_zones && dca_recommendations.entry_zones.length > 0;
  const hasRiskAssessment = dca_recommendations?.risk_assessment;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">DCA Recommendations</h2>
      
      {/* Trend Analysis */}
      {trend_analysis && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Market Trend</h3>
          <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
            trend_analysis.primary_trend === 'bullish' ? 'bg-green-100 text-green-800' :
            trend_analysis.primary_trend === 'bearish' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {trend_analysis.primary_trend.toUpperCase()} (Strength: {formatPercentage(trend_analysis.strength)}%)
          </div>
        </div>
      )}

      {/* Entry Zones */}
      {hasEntryZones && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Recommended Entry Zones</h3>
          <div className="space-y-3">
            {dca_recommendations!.entry_zones.map((zone, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between mb-2">
                  <span className="font-medium">Price: ${formatPrice(zone.price)}</span>
                  <span className={`px-2 py-1 rounded-full text-sm ${
                    zone.confidence > 0.7 ? 'bg-green-100 text-green-800' :
                    zone.confidence > 0.4 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Confidence: {formatPercentage(zone.confidence)}%
                  </span>
                </div>
                {zone.reasoning?.length > 0 && (
                  <ul className="text-sm text-gray-600 list-disc list-inside">
                    {zone.reasoning.map((reason, i) => (
                      <li key={i}>{reason}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Assessment */}
      {hasRiskAssessment && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Risk Assessment</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="mb-3">
              <div className="text-sm text-gray-600 mb-1">Overall Risk Level</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    dca_recommendations!.risk_assessment.overall_risk > 0.7 ? 'bg-red-500' :
                    dca_recommendations!.risk_assessment.overall_risk > 0.4 ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${dca_recommendations!.risk_assessment.overall_risk * 100}%` }}
                />
              </div>
            </div>
            {dca_recommendations!.risk_assessment.key_risks?.length > 0 && (
              <div className="space-y-2">
                {dca_recommendations!.risk_assessment.key_risks.map((risk, index) => (
                  <div key={index} className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    <span className="text-sm">{risk}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}; 