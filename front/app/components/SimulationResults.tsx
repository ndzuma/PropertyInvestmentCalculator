"use client";

import { StrategyResult } from "../types/api";

interface SimulationResultsProps {
  results: StrategyResult[];
  currency: string;
  isLoading: boolean;
  error?: string;
}

export default function SimulationResults({
  results,
  currency,
  isLoading,
  error,
}: SimulationResultsProps) {
  if (isLoading) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
          Simulation Results
        </h3>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Running simulations...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
          Simulation Results
        </h3>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-red-400">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Simulation Error
              </h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
          Simulation Results
        </h3>
        <div className="text-center text-gray-500 py-12">
          <p>No simulation results yet.</p>
          <p className="text-sm mt-2">
            Add strategies and click simulate to see results.
          </p>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return `${currency}${amount.toLocaleString()}`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Track seen strategy names to ensure unique keys
  const seenNames: Record<string, number> = {};

  const getUniqueKey = (strategyName: string): string => {
    if (!(strategyName in seenNames)) {
      seenNames[strategyName] = 0;
      return strategyName;
    } else {
      seenNames[strategyName]++;
      return `${strategyName}-${seenNames[strategyName]}`;
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
        Simulation Results
      </h3>

      {/* Dynamic Width Results Display */}
      <div className="space-y-4">
        {Array.from(
          { length: Math.ceil(results.length / 4) },
          (_, rowIndex) => (
            <div key={rowIndex} className="flex gap-4">
              {results
                .slice(rowIndex * 4, (rowIndex + 1) * 4)
                .map((result, colIndex) => {
                  const resultsInThisRow = Math.min(
                    4,
                    results.length - rowIndex * 4,
                  );
                  return (
                    <div
                      key={getUniqueKey(result.strategy_name)}
                      className="bg-gray-50 rounded-lg border border-gray-200 p-4 flex-1"
                      style={{ width: `${100 / resultsInThisRow}%` }}
                    >
                      {/* Strategy Header */}
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-900 text-sm mb-1">
                          {result.strategy_name}
                        </h4>
                        {result.summary.simulation_ended && (
                          <span className="inline-flex px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded-full">
                            Ended Early: {result.summary.end_reason}
                          </span>
                        )}
                      </div>

                      {/* Key Metrics */}
                      <div className="space-y-3">
                        {/* Portfolio Value */}
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Portfolio Value
                          </div>
                          <div className="text-lg font-bold text-gray-900">
                            {formatCurrency(
                              result.summary.final_portfolio_value,
                            )}
                          </div>
                        </div>

                        {/* Property Count */}
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Properties
                          </div>
                          <div className="text-sm font-medium text-gray-900">
                            {result.summary.final_property_count}
                          </div>
                        </div>

                        {/* Total Equity */}
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Total Equity
                          </div>
                          <div className="text-sm font-medium text-green-600">
                            {formatCurrency(result.summary.final_equity)}
                          </div>
                        </div>

                        {/* Monthly Cash Flow */}
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Monthly Cash Flow
                          </div>
                          <div
                            className={`text-sm font-medium ${
                              result.summary.monthly_cashflow >= 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {formatCurrency(result.summary.monthly_cashflow)}
                          </div>
                        </div>

                        {/* Total Cash Invested */}
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Cash Invested
                          </div>
                          <div className="text-sm font-medium text-gray-900">
                            {formatCurrency(result.summary.total_cash_invested)}
                          </div>
                        </div>

                        {/* Return on Investment */}
                        {result.summary.total_cash_invested > 0 && (
                          <div>
                            <div className="text-xs text-gray-500 mb-1">
                              Return on Investment
                            </div>
                            <div className="text-sm font-medium text-blue-600">
                              {formatPercentage(
                                (result.summary.final_equity -
                                  result.summary.total_cash_invested) /
                                  result.summary.total_cash_invested,
                              )}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Events Summary */}
                      <div className="mt-4 pt-3 border-t border-gray-200">
                        <div className="text-xs text-gray-500 space-y-1">
                          {result.events.property_purchases.length > 0 && (
                            <div>
                              {result.events.property_purchases.length} purchase
                              {result.events.property_purchases.length !== 1
                                ? "s"
                                : ""}
                            </div>
                          )}
                          {result.events.refinancing_events.length > 0 && (
                            <div>
                              {result.events.refinancing_events.length}{" "}
                              refinancing
                              {result.events.refinancing_events.length !== 1
                                ? "s"
                                : ""}
                            </div>
                          )}
                          {result.events.capital_injections.length > 0 && (
                            <div>
                              {result.events.capital_injections.length} capital
                              injection
                              {result.events.capital_injections.length !== 1
                                ? "s"
                                : ""}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Performance Bar */}
                      <div className="mt-4">
                        <div className="text-xs text-gray-500 mb-1">
                          Performance vs Others
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{
                              width: `${
                                (result.summary.final_portfolio_value /
                                  Math.max(
                                    ...results.map(
                                      (r) => r.summary.final_portfolio_value,
                                    ),
                                  )) *
                                100
                              }%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          ),
        )}
      </div>

      {/* Summary Stats */}
      {results.length > 1 && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h4 className="text-md font-semibold text-gray-800 mb-4">
            Comparison Summary
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Best Portfolio Value</div>
              <div className="font-medium">
                {formatCurrency(
                  Math.max(
                    ...results.map((r) => r.summary.final_portfolio_value),
                  ),
                )}
              </div>
            </div>
            <div>
              <div className="text-gray-500">Best Cash Flow</div>
              <div className="font-medium">
                {formatCurrency(
                  Math.max(...results.map((r) => r.summary.monthly_cashflow)),
                )}
              </div>
            </div>
            <div>
              <div className="text-gray-500">Most Properties</div>
              <div className="font-medium">
                {Math.max(
                  ...results.map((r) => r.summary.final_property_count),
                )}
              </div>
            </div>
            <div>
              <div className="text-gray-500">Best ROI</div>
              <div className="font-medium">
                {formatPercentage(
                  Math.max(
                    ...results
                      .filter((r) => r.summary.total_cash_invested > 0)
                      .map(
                        (r) =>
                          (r.summary.final_equity -
                            r.summary.total_cash_invested) /
                          r.summary.total_cash_invested,
                      ),
                  ),
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
