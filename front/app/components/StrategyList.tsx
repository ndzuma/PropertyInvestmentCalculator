"use client";

import { StrategyRequest } from "../types/api";
import { Button } from "@/components/ui/button";

interface StrategyListProps {
  strategies: StrategyRequest[];
  onRemoveStrategy: (index: number) => void;
}

export default function StrategyList({
  strategies,
  onRemoveStrategy,
}: StrategyListProps) {
  const formatStrategyType = (type: string) => {
    switch (type) {
      case "cash_only":
        return "Cash Only";
      case "leveraged":
        return "Leveraged";
      case "mixed":
        return "Mixed Portfolio";
      default:
        return type;
    }
  };

  const getStrategyDetails = (strategy: StrategyRequest) => {
    const details: string[] = [];

    if (
      strategy.strategy_type === "leveraged" ||
      strategy.strategy_type === "mixed"
    ) {
      if (strategy.ltv_ratio) {
        details.push(`LTV: ${(strategy.ltv_ratio * 100).toFixed(0)}%`);
      }
      if (strategy.interest_rate) {
        details.push(`Interest: ${(strategy.interest_rate * 100).toFixed(1)}%`);
      }
      if (strategy.enable_refinancing) {
        details.push(`Refinancing: ${strategy.refinance_frequency}`);
      }
    }

    if (strategy.strategy_type === "mixed") {
      if (strategy.leveraged_property_ratio && strategy.cash_property_ratio) {
        details.push(
          `Split: ${(strategy.leveraged_property_ratio * 100).toFixed(0)}% Leveraged / ${(strategy.cash_property_ratio * 100).toFixed(0)}% Cash`,
        );
      }
      if (strategy.first_property_type) {
        details.push(`First: ${strategy.first_property_type}`);
      }
    }

    details.push(`${strategy.simulation_years} years`);

    if (strategy.reinvest_cashflow) {
      details.push("Reinvesting");
    }

    return details;
  };

  if (strategies.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Selected Strategies
        </h3>
        <div className="text-center text-gray-500 py-8">
          <p>No strategies added yet.</p>
          <p className="text-sm mt-2">
            Define a strategy on the left to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Selected Strategies ({strategies.length})
      </h3>

      <div className="space-y-3">
        {strategies.map((strategy, index) => (
          <div
            key={index}
            className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div className="flex-1">
              {/* Strategy Name and Type */}
              <div className="flex items-center gap-3 mb-2">
                <h4 className="font-medium text-gray-900">{strategy.name}</h4>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${
                    strategy.strategy_type === "cash_only"
                      ? "bg-green-100 text-green-800"
                      : strategy.strategy_type === "leveraged"
                        ? "bg-blue-100 text-blue-800"
                        : "bg-purple-100 text-purple-800"
                  }`}
                >
                  {formatStrategyType(strategy.strategy_type)}
                </span>
              </div>

              {/* Strategy Details */}
              <div className="flex flex-wrap gap-2">
                {getStrategyDetails(strategy).map((detail, detailIndex) => (
                  <span
                    key={detailIndex}
                    className="px-2 py-1 text-xs bg-white text-gray-600 rounded border"
                  >
                    {detail}
                  </span>
                ))}
              </div>
            </div>

            {/* Remove Button */}
            <Button
              onClick={() => onRemoveStrategy(index)}
              variant="destructive"
              size="sm"
              className="ml-4 flex-shrink-0"
            >
              Remove
            </Button>
          </div>
        ))}
      </div>

      {/* Strategy Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <div className="flex justify-between items-center">
            <span>
              <strong>
                Ready to simulate {strategies.length} strateg
                {strategies.length === 1 ? "y" : "ies"}
              </strong>
            </span>
            <div className="text-xs text-gray-500">
              Click simulate to compare results
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
