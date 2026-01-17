"use client";

import { StrategyResult } from "../types/api";

interface SimulationResultsDataProps {
  results: StrategyResult[];
  currency: string;
}

export default function SimulationResultsData({
  results,
  currency,
}: SimulationResultsDataProps) {
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
    <div className="space-y-6">
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
        <div className="pt-6 border-t border-gray-200">
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
