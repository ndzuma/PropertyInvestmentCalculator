"use client";

import { useState, useEffect } from "react";
import {
  StrategyRequest,
  StrategyType,
  RefineFrequency,
  StrategyPreset,
} from "../types/api";
import { apiRequest } from "@/lib/api-config";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { AlertTriangle } from "lucide-react";

interface StrategyBuilderProps {
  onAddStrategy: (strategy: StrategyRequest) => void;
  simulationMonths: number;
  currentLtvRestriction: number | null;
  selectedInvestorType: "local" | "international";
  defaultInterestRate?: number;
}

export default function StrategyBuilder({
  onAddStrategy,
  simulationMonths,
  currentLtvRestriction,
  selectedInvestorType,
  defaultInterestRate,
}: StrategyBuilderProps) {
  const [strategy, setStrategy] = useState<StrategyRequest>({
    name: "",
    strategy_type: "cash_only",
    simulation_months: simulationMonths,
    reinvest_cashflow: false,
    enable_refinancing: false,
    refinance_frequency: "never",
    custom_refinance_months: undefined,
    interest_rate: defaultInterestRate,
  });

  const [presets, setPresets] = useState<StrategyPreset[]>([]);
  const [loadingPresets, setLoadingPresets] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string>("");

  // Load presets from API
  useEffect(() => {
    const loadPresets = async () => {
      setLoadingPresets(true);
      try {
        const data = await apiRequest<StrategyPreset[]>("strategyPresets");
        setPresets(data);
      } catch (error) {
        console.error("Failed to load presets:", error);
      }
      setLoadingPresets(false);
    };

    loadPresets();
  }, []);

  // Update strategy interest rate when default changes
  useEffect(() => {
    if (defaultInterestRate && strategy.strategy_type !== "cash_only") {
      // Use setTimeout to avoid cascading renders
      const timer = setTimeout(() => {
        setStrategy((prev) => ({
          ...prev,
          interest_rate: defaultInterestRate,
        }));
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [defaultInterestRate, strategy.strategy_type]);

  const updateStrategy = (
    field: keyof StrategyRequest,
    value: string | number | boolean | undefined,
  ) => {
    setStrategy((prev) => {
      const updated = {
        ...prev,
        [field]: value,
      };

      // Clear custom_refinance_months if refinance_frequency changes to non-other
      if (field === "refinance_frequency" && value !== "other") {
        updated.custom_refinance_months = undefined;
      }

      // Set default interest rate when strategy type changes to leveraged/mixed
      if (
        field === "strategy_type" &&
        (value === "leveraged" || value === "mixed") &&
        defaultInterestRate
      ) {
        updated.interest_rate = defaultInterestRate;
      }

      // Check LTV restriction for international investors
      if (
        field === "ltv_ratio" &&
        typeof value === "number" &&
        currentLtvRestriction &&
        selectedInvestorType === "international" &&
        value > currentLtvRestriction
      ) {
        toast.warning("LTV exceeds investor limit", {
          description: `International investors are limited to ${(currentLtvRestriction * 100).toFixed(0)}% LTV in this location`,
        });
      }

      return updated;
    });
  };

  const loadPreset = (presetName: string) => {
    const preset = presets.find((p) => p.name === presetName);
    if (preset) {
      const baseStrategy: StrategyRequest = {
        name: preset.name,
        strategy_type: preset.strategy_type,
        simulation_months: simulationMonths,
        reinvest_cashflow: false,
        enable_refinancing: false,
        refinance_frequency: "never",
        custom_refinance_months: undefined,
      };

      // Apply preset config
      const strategyData = {
        ...baseStrategy,
        ...preset.config,
      } as StrategyRequest;

      // Override preset interest rate with country default if available
      if (
        defaultInterestRate &&
        (strategyData.strategy_type === "leveraged" ||
          strategyData.strategy_type === "mixed")
      ) {
        strategyData.interest_rate = defaultInterestRate;
      }

      setStrategy(strategyData);
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
        toast.error("Invalid LTV ratio", {
          description: "LTV ratio must be between 0.01 and 0.99 (1% to 99%)",
        });
        return;
      }
      if (!strategy.interest_rate || strategy.interest_rate <= 0) {
        toast.error("Invalid interest rate", {
          description: "Interest rate must be greater than 0%",
        });
        return;
      }
    }

    if (strategy.strategy_type === "mixed") {
      if (!strategy.leveraged_property_ratio || !strategy.cash_property_ratio) {
        toast.error("Missing property ratios", {
          description:
            "Mixed strategy requires both leveraged and cash property ratios",
        });
        return;
      }
      if (
        Math.abs(
          strategy.leveraged_property_ratio + strategy.cash_property_ratio,
        ) !== 1.0
      ) {
        toast.error("Invalid property ratios", {
          description: "Leveraged and cash property ratios must sum to 100%",
        });
        return;
      }
    }

    onAddStrategy(strategy);

    // Reset form
    setStrategy({
      name: "",
      strategy_type: "cash_only",
      simulation_months: simulationMonths,
      reinvest_cashflow: false,
      enable_refinancing: false,
      refinance_frequency: "never",
      custom_refinance_months: undefined,
      interest_rate: defaultInterestRate,
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
          <Select
            value={selectedPreset}
            onValueChange={handlePresetChange}
            disabled={loadingPresets}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {presets.map((preset) => (
                <SelectItem key={preset.name} value={preset.name}>
                  {preset.name} - {preset.description}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Strategy Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy Name
          </label>
          <Input
            type="text"
            value={strategy.name}
            onChange={(e) => updateStrategy("name", e.target.value)}
          />
        </div>

        {/* Strategy Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy Type
          </label>
          <Select
            value={strategy.strategy_type}
            onValueChange={(value: StrategyType) =>
              updateStrategy("strategy_type", value)
            }
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="cash_only">Cash Only</SelectItem>
              <SelectItem value="leveraged">Leveraged</SelectItem>
              <SelectItem value="mixed">Mixed Portfolio</SelectItem>
            </SelectContent>
          </Select>
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
                <InputGroup>
                  <InputGroupInput
                    type="number"
                    value={strategy.ltv_ratio || ""}
                    onChange={(e) =>
                      updateStrategy(
                        "ltv_ratio",
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    min="0"
                    max="0.99"
                    step="0.01"
                  />
                  <InputGroupAddon align="inline-end">%</InputGroupAddon>
                </InputGroup>
              </div>

              {/* Interest Rate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interest Rate
                </label>
                <InputGroup>
                  <InputGroupInput
                    type="number"
                    value={
                      strategy.interest_rate ? strategy.interest_rate * 100 : ""
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "interest_rate",
                        e.target.value
                          ? Number(e.target.value) / 100
                          : undefined,
                      )
                    }
                    min="0"
                    step="0.1"
                  />
                  <InputGroupAddon align="inline-end">%</InputGroupAddon>
                </InputGroup>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Loan Term */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loan Term
                </label>
                <InputGroup>
                  <InputGroupInput
                    type="number"
                    value={strategy.loan_term_years || ""}
                    onChange={(e) =>
                      updateStrategy(
                        "loan_term_years",
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    min="1"
                    max="50"
                  />
                  <InputGroupAddon align="inline-end">years</InputGroupAddon>
                </InputGroup>
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
                <InputGroup>
                  <InputGroupInput
                    type="number"
                    value={
                      strategy.leveraged_property_ratio
                        ? strategy.leveraged_property_ratio * 100
                        : ""
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "leveraged_property_ratio",
                        e.target.value
                          ? Number(e.target.value) / 100
                          : undefined,
                      )
                    }
                    min="0"
                    max="100"
                    step="1"
                  />
                  <InputGroupAddon align="inline-end">%</InputGroupAddon>
                </InputGroup>
              </div>

              {/* Cash Property Ratio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cash Property Ratio
                </label>
                <InputGroup>
                  <InputGroupInput
                    type="number"
                    value={
                      strategy.cash_property_ratio
                        ? strategy.cash_property_ratio * 100
                        : ""
                    }
                    onChange={(e) =>
                      updateStrategy(
                        "cash_property_ratio",
                        e.target.value
                          ? Number(e.target.value) / 100
                          : undefined,
                      )
                    }
                    min="0"
                    max="100"
                    step="1"
                  />
                  <InputGroupAddon align="inline-end">%</InputGroupAddon>
                </InputGroup>
              </div>
            </div>

            {/* First Property Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Property Type
              </label>
              <Select
                value={strategy.first_property_type || "cash"}
                onValueChange={(value) =>
                  updateStrategy("first_property_type", value)
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">Cash</SelectItem>
                  <SelectItem value="leveraged">Leveraged</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        {/* Refinancing Options */}
        {(strategy.strategy_type === "leveraged" ||
          strategy.strategy_type === "mixed") && (
          <div className="space-y-4">
            {/* Enable Refinancing */}
            <div className="flex items-center space-x-2">
              <Switch
                id="enable_refinancing"
                checked={strategy.enable_refinancing}
                onCheckedChange={(checked) =>
                  updateStrategy("enable_refinancing", checked)
                }
              />
              <label
                htmlFor="enable_refinancing"
                className="text-sm text-gray-700"
              >
                Enable Refinancing
              </label>
            </div>

            {strategy.enable_refinancing && (
              <div className="space-y-4">
                {/* Refinance Frequency and Custom Period */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Refinance Frequency */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Refinance Frequency
                    </label>
                    <Select
                      value={strategy.refinance_frequency}
                      onValueChange={(value: RefineFrequency) =>
                        updateStrategy("refinance_frequency", value)
                      }
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="never">Never</SelectItem>
                        <SelectItem value="annually">Annually</SelectItem>
                        <SelectItem value="bi_annually">Bi-annually</SelectItem>
                        <SelectItem value="quarterly">Quarterly</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Custom Refinance Period */}
                  {strategy.refinance_frequency === "other" && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Custom Refinance Period
                      </label>
                      <InputGroup>
                        <InputGroupInput
                          type="number"
                          placeholder="e.g., 3, 18"
                          value={strategy.custom_refinance_months || ""}
                          onChange={(e) =>
                            updateStrategy(
                              "custom_refinance_months",
                              e.target.value
                                ? Number(e.target.value)
                                : undefined,
                            )
                          }
                          min="1"
                        />
                        <InputGroupAddon align="inline-end">
                          months
                        </InputGroupAddon>
                      </InputGroup>
                      <p className="text-xs text-gray-500 mt-1">
                        Specify refinancing interval in months (e.g., 3 for
                        quarterly, 18 for every 1.5 years)
                      </p>
                    </div>
                  )}
                </div>

                {/* Target Refinance LTV */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Refinance LTV
                  </label>
                  <InputGroup>
                    <InputGroupInput
                      type="number"
                      value={
                        strategy.target_refinance_ltv
                          ? strategy.target_refinance_ltv * 100
                          : ""
                      }
                      onChange={(e) =>
                        updateStrategy(
                          "target_refinance_ltv",
                          e.target.value
                            ? Number(e.target.value) / 100
                            : undefined,
                        )
                      }
                      min="0"
                      max="99"
                      step="1"
                    />
                    <InputGroupAddon align="inline-end">%</InputGroupAddon>
                  </InputGroup>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Reinvest Cashflow */}
        <div className="flex items-center space-x-2">
          <Switch
            id="reinvest_cashflow"
            checked={strategy.reinvest_cashflow}
            onCheckedChange={(checked) =>
              updateStrategy("reinvest_cashflow", checked)
            }
          />
          <label htmlFor="reinvest_cashflow" className="text-sm text-gray-700">
            Reinvest Cash Flow
          </label>
        </div>

        {/* Add Strategy Button */}
        <Button
          onClick={addStrategy}
          disabled={!strategy.name.trim()}
          className="w-full"
        >
          Add Strategy to Simulation
        </Button>
      </div>
    </div>
  );
}
