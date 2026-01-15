"use client";

import { useState, useEffect } from "react";
import {
  StrategyRequest,
  StrategyType,
  RefineFrequency,
  StrategyPreset,
} from "../types/api";

interface StrategyBuilderProps {
  onAddStrategy: (strategy: StrategyRequest) => void;
}

export default function StrategyBuilder({
  onAddStrategy,
}: StrategyBuilderProps) {
  const [strategy, setStrategy] = useState<StrategyRequest>({
    name: "",
    strategy_type: "cash_only",
    simulation_years: 10,
    reinvest_cashflow: true,
    enable_refinancing: false,
    refinance_frequency: "never",
  });

  const [presets, setPresets] = useState<StrategyPreset[]>([]);
  const [loadingPresets, setLoadingPresets] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string>("");

  // Load presets from API
  useEffect(() => {
    const loadPresets = async () => {
      setLoadingPresets(true);
      try {
        const response = await fetch("http://localhost:8001/strategy-presets");
        if (response.ok) {
          const data = await response.json();
          setPresets(data);
        }
      } catch (error) {
        console.error("Failed to load presets:", error);
      }
      setLoadingPresets(false);
    };

    loadPresets();
  }, []);

  const updateStrategy = (field: keyof StrategyRequest, value: any) => {
    setStrategy((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const loadPreset = (presetName: string) => {
    const preset = presets.find((p) => p.name === presetName);
    if (preset) {
      setStrategy({
        name: preset.name,
        strategy_type: preset.strategy_type,
        simulation_years: 10,
        reinvest_cashflow: true,
        enable_refinancing: false,
        refinance_frequency: "never",
        ...preset.config,
      });
    }
  };

  const handlePresetChange = (presetName: string) => {
    setSelectedPreset(presetName);
    if (presetName) {
      loadPreset(presetName);
    }
  };

  const addStrategy = () => {
    if (!strategy.name.trim()) {
      alert("Please enter a strategy name");
      return;
    }

    // Validate based on strategy type
    if (
      strategy.strategy_type === "leveraged" ||
      strategy.strategy_type === "mixed"
    ) {
      if (
        !strategy.ltv_ratio ||
        strategy.ltv_ratio <= 0 ||
        strategy.ltv_ratio >= 1
      ) {
        alert("LTV ratio must be between 0 and 1");
        return;
      }
      if (!strategy.interest_rate || strategy.interest_rate <= 0) {
        alert("Interest rate must be greater than 0");
        return;
      }
    }

    if (strategy.strategy_type === "mixed") {
      if (!strategy.leveraged_property_ratio || !strategy.cash_property_ratio) {
        alert("Mixed strategy requires property ratios");
        return;
      }
      if (
        Math.abs(
          strategy.leveraged_property_ratio + strategy.cash_property_ratio - 1,
        ) > 0.001
      ) {
        alert("Property ratios must sum to 1.0");
        return;
      }
    }

    onAddStrategy(strategy);

    // Reset form
    setStrategy({
      name: "",
      strategy_type: "cash_only",
      simulation_years: 10,
      reinvest_cashflow: true,
      enable_refinancing: false,
      refinance_frequency: "never",
    });
    setSelectedPreset("");
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Define Strategy
      </h3>

      <div className="space-y-4">
        {/* Load Preset or Create New */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Load Preset Strategy (Optional)
          </label>
          <select
            value={selectedPreset}
            onChange={(e) => handlePresetChange(e.target.value)}
            disabled={loadingPresets}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          >
            <option value="">Create new strategy</option>
            {presets.map((preset) => (
              <option key={preset.name} value={preset.name}>
                {preset.name} - {preset.description}
              </option>
            ))}
          </select>
        </div>

        {/* Strategy Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy Name
          </label>
          <input
            type="text"
            value={strategy.name}
            onChange={(e) => updateStrategy("name", e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
            placeholder="My Investment Strategy"
          />
        </div>

        {/* Strategy Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy Type
          </label>
          <select
            value={strategy.strategy_type}
            onChange={(e) =>
              updateStrategy("strategy_type", e.target.value as StrategyType)
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          >
            <option value="cash_only">Cash Only</option>
            <option value="leveraged">Leveraged</option>
            <option value="mixed">Mixed Portfolio</option>
          </select>
        </div>

        {/* Leveraged Strategy Parameters */}
        {(strategy.strategy_type === "leveraged" ||
          strategy.strategy_type === "mixed") && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* LTV Ratio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LTV Ratio
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={strategy.ltv_ratio || 0}
                    onChange={(e) =>
                      updateStrategy("ltv_ratio", Number(e.target.value))
                    }
                    className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="0.7"
                    min="0"
                    max="0.99"
                    step="0.01"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    %
                  </span>
                </div>
              </div>

              {/* Interest Rate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interest Rate
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={
                      strategy.interest_rate ? strategy.interest_rate * 100 : 0
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "interest_rate",
                        Number(e.target.value) / 100,
                      )
                    }
                    className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="10"
                    min="0"
                    step="0.1"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    %
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Loan Term */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loan Term
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={strategy.loan_term_years || 20}
                    onChange={(e) =>
                      updateStrategy("loan_term_years", Number(e.target.value))
                    }
                    className="w-full px-4 pr-16 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="20"
                    min="1"
                    max="50"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    years
                  </span>
                </div>
              </div>

              {/* Appreciation Rate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Appreciation Rate
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={
                      strategy.appreciation_rate
                        ? strategy.appreciation_rate * 100
                        : 6
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "appreciation_rate",
                        Number(e.target.value) / 100,
                      )
                    }
                    className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="6"
                    min="0"
                    step="0.1"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    %
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mixed Strategy Parameters */}
        {strategy.strategy_type === "mixed" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Leveraged Property Ratio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Leveraged Property Ratio
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={
                      strategy.leveraged_property_ratio
                        ? strategy.leveraged_property_ratio * 100
                        : 60
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "leveraged_property_ratio",
                        Number(e.target.value) / 100,
                      )
                    }
                    className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="60"
                    min="0"
                    max="100"
                    step="1"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    %
                  </span>
                </div>
              </div>

              {/* Cash Property Ratio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cash Property Ratio
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={
                      strategy.cash_property_ratio
                        ? strategy.cash_property_ratio * 100
                        : 40
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "cash_property_ratio",
                        Number(e.target.value) / 100,
                      )
                    }
                    className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    placeholder="40"
                    min="0"
                    max="100"
                    step="1"
                  />
                  <span
                    className="absolute right-3 top-1/2 transform -translate-y-1/2
 text-gray-500"
                  >
                    %
                  </span>
                </div>
              </div>
            </div>

            {/* First Property Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Property Type
              </label>
              <select
                value={strategy.first_property_type || "cash"}
                onChange={(e) =>
                  updateStrategy("first_property_type", e.target.value)
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              >
                <option value="cash">Cash</option>
                <option value="leveraged">Leveraged</option>
              </select>
            </div>
          </div>
        )}

        {/* Refinancing Options */}
        {(strategy.strategy_type === "leveraged" ||
          strategy.strategy_type === "mixed") && (
          <div className="space-y-4">
            {/* Enable Refinancing */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enable_refinancing"
                checked={strategy.enable_refinancing}
                onChange={(e) =>
                  updateStrategy("enable_refinancing", e.target.checked)
                }
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <label
                htmlFor="enable_refinancing"
                className="ml-2 text-sm text-gray-700"
              >
                Enable Refinancing
              </label>
            </div>

            {strategy.enable_refinancing && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Refinance Frequency */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Refinance Frequency
                  </label>
                  <select
                    value={strategy.refinance_frequency}
                    onChange={(e) =>
                      updateStrategy(
                        "refinance_frequency",
                        e.target.value as RefineFrequency,
                      )
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  >
                    <option value="never">Never</option>
                    <option value="annually">Annually</option>
                    <option value="bi_annually">Bi-annually</option>
                    <option value="quarterly">Quarterly</option>
                  </select>
                </div>

                {/* Target Refinance LTV */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Refinance LTV
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={
                        strategy.target_refinance_ltv
                          ? strategy.target_refinance_ltv * 100
                          : 60
                      }
                      onChange={(e) =>
                        updateStrategy(
                          "target_refinance_ltv",
                          Number(e.target.value) / 100,
                        )
                      }
                      className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                      placeholder="60"
                      min="0"
                      max="99"
                      step="1"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                      %
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Reinvest Cashflow */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="reinvest_cashflow"
            checked={strategy.reinvest_cashflow}
            onChange={(e) =>
              updateStrategy("reinvest_cashflow", e.target.checked)
            }
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
          <label
            htmlFor="reinvest_cashflow"
            className="ml-2 text-sm text-gray-700"
          >
            Reinvest Cash Flow
          </label>
        </div>

        {/* Add Strategy Button */}
        <button
          onClick={addStrategy}
          disabled={!strategy.name.trim()}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Add Strategy to Simulation
        </button>
      </div>
    </div>
  );
}
