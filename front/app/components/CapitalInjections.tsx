"use client";

import { useState } from "react";
import {
  CapitalInjectionRequest,
  CapitalInjectionFrequency,
} from "../types/api";

interface CapitalInjectionsProps {
  capitalInjections: CapitalInjectionRequest[];
  setCapitalInjections: (injections: CapitalInjectionRequest[]) => void;
  currency: string;
}

export default function CapitalInjections({
  capitalInjections,
  setCapitalInjections,
  currency,
}: CapitalInjectionsProps) {
  const [newInjection, setNewInjection] = useState<CapitalInjectionRequest>({
    amount: 0,
    frequency: "monthly",
    start_period: 1,
    end_period: undefined,
    specific_periods: undefined,
  });

  const [showSpecificPeriods, setShowSpecificPeriods] = useState(false);
  const [specificPeriodsInput, setSpecificPeriodsInput] = useState("");

  const addInjection = () => {
    if (newInjection.amount <= 0) return;

    const injection: CapitalInjectionRequest = {
      ...newInjection,
      specific_periods:
        newInjection.frequency === "one_time"
          ? specificPeriodsInput
              .split(",")
              .map((p) => parseInt(p.trim()))
              .filter((p) => !isNaN(p))
          : undefined,
    };

    setCapitalInjections([...capitalInjections, injection]);

    // Reset form
    setNewInjection({
      amount: 0,
      frequency: "monthly",
      start_period: 1,
      end_period: undefined,
      specific_periods: undefined,
    });
    setSpecificPeriodsInput("");
    setShowSpecificPeriods(false);
  };

  const removeInjection = (index: number) => {
    setCapitalInjections(capitalInjections.filter((_, i) => i !== index));
  };

  const formatFrequency = (frequency: CapitalInjectionFrequency) => {
    switch (frequency) {
      case "monthly":
        return "Monthly";
      case "quarterly":
        return "Quarterly";
      case "yearly":
        return "Yearly";
      case "five_yearly":
        return "Every 5 Years";
      case "one_time":
        return "One-time";
      default:
        return frequency;
    }
  };

  const formatInjectionDescription = (injection: CapitalInjectionRequest) => {
    let description = `${currency}${injection.amount.toLocaleString()} - ${formatFrequency(injection.frequency)}`;

    if (injection.frequency === "one_time" && injection.specific_periods) {
      description += ` (Periods: ${injection.specific_periods.join(", ")})`;
    } else {
      description += ` (Period ${injection.start_period}`;
      if (injection.end_period) {
        description += ` to ${injection.end_period}`;
      } else {
        description += ` onwards`;
      }
      description += `)`;
    }

    return description;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Capital Injections
      </h3>

      {/* Add New Injection Form */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                {currency}
              </span>
              <input
                type="number"
                value={newInjection.amount}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    amount: Number(e.target.value),
                  })
                }
                className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                placeholder="5000"
                min="0"
              />
            </div>
          </div>

          {/* Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <select
              value={newInjection.frequency}
              onChange={(e) => {
                const freq = e.target.value as CapitalInjectionFrequency;
                setNewInjection({ ...newInjection, frequency: freq });
                setShowSpecificPeriods(freq === "one_time");
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            >
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
              <option value="five_yearly">Every 5 Years</option>
              <option value="one_time">One-time</option>
            </select>
          </div>
        </div>

        {/* Period Configuration */}
        {newInjection.frequency === "one_time" ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Periods (comma-separated)
            </label>
            <input
              type="text"
              value={specificPeriodsInput}
              onChange={(e) => setSpecificPeriodsInput(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="24, 48, 60"
            />
            <p className="text-xs text-gray-500 mt-1">
              Example: 24, 48 (for periods 24 and 48)
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Start Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Period
              </label>
              <input
                type="number"
                value={newInjection.start_period}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    start_period: Number(e.target.value),
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                placeholder="1"
                min="1"
              />
            </div>

            {/* End Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Period (Optional)
              </label>
              <input
                type="number"
                value={newInjection.end_period || ""}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    end_period: e.target.value
                      ? Number(e.target.value)
                      : undefined,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                placeholder="Leave empty for ongoing"
                min="1"
              />
            </div>
          </div>
        )}

        <button
          onClick={addInjection}
          disabled={newInjection.amount <= 0}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Add Capital Injection
        </button>
      </div>

      {/* Existing Injections List */}
      {capitalInjections.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-3">
            Added Capital Injections
          </h4>
          <div className="space-y-2">
            {capitalInjections.map((injection, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <span className="text-sm text-gray-700">
                  {formatInjectionDescription(injection)}
                </span>
                <button
                  onClick={() => removeInjection(index)}
                  className="px-3 py-1 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          {/* Total Summary */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <strong>
                Total Ongoing Injections: {currency}
                {capitalInjections
                  .filter((inj) => inj.frequency !== "one_time")
                  .reduce((sum, inj) => sum + inj.amount, 0)
                  .toLocaleString()}{" "}
                per period
              </strong>
            </div>
            {capitalInjections.some((inj) => inj.frequency === "one_time") && (
              <div className="text-sm text-gray-600">
                <strong>
                  One-time Injections: {currency}
                  {capitalInjections
                    .filter((inj) => inj.frequency === "one_time")
                    .reduce(
                      (sum, inj) =>
                        sum + inj.amount * (inj.specific_periods?.length || 1),
                      0,
                    )
                    .toLocaleString()}
                </strong>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
