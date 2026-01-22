"use client";

import { useState } from "react";
import {
  PropertyRequest,
  OperatingRequest,
  CapitalInjectionRequest,
  StrategyRequest,
  SimulationRequest,
  SimulationResponse,
  StrategyResult,
  SimulationPreset,
} from "./types/api";
import { apiRequest } from "@/lib/api-config";
import SettingsBar from "./components/SettingsBar";
import PropertyDetails from "./components/PropertyDetails";
import OperatingExpenses from "./components/OperatingExpenses";
import CapitalInjections from "./components/CapitalInjections";
import StrategyBuilder from "./components/StrategyBuilder";
import StrategyList from "./components/StrategyList";
import SimulationResults from "./components/SimulationResults";
import { Button } from "@/components/ui/button";
import SimulationButtons from "./components/SimulationButtons";
import CountrySelector from "./components/CountrySelector";
import { CountrySettings } from "./types/api";
import { toast } from "sonner";

export default function Home() {
  // Settings state
  const [availableCapital, setAvailableCapital] = useState<number | undefined>(
    undefined,
  );
  const [simulationMonths, setSimulationMonths] = useState(120); // 10 years = 120 months
  const [currency, setCurrency] = useState("R");
  const [appreciationRate, setAppreciationRate] = useState(0.06); // Default 6% annual

  // Country settings state
  const [selectedInvestorType, setSelectedInvestorType] = useState<
    "local" | "international"
  >("local");
  const [currentLtvRestriction, setCurrentLtvRestriction] = useState<
    number | null
  >(null);
  const [defaultInterestRate, setDefaultInterestRate] = useState<number>();

  // Property state
  const [property, setProperty] = useState<PropertyRequest>({
    purchase_price: 0,
    transfer_duty: 0,
    conveyancing_fees: 0,
    bond_registration: 0,
    furnishing_cost: 0,
  });

  // Operating state
  const [operating, setOperating] = useState<OperatingRequest>({
    monthly_rental_income: 0,
    vacancy_rate: 0,
    monthly_levies: 0,
    property_management_fee_rate: 0,
    monthly_insurance: 0,
    monthly_maintenance_reserve: 0,
    monthly_furnishing_repair_costs: 0,
  });

  // Capital injections state
  const [capitalInjections, setCapitalInjections] = useState<
    CapitalInjectionRequest[]
  >([]);

  // Strategies state
  const [strategies, setStrategies] = useState<StrategyRequest[]>([]);

  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResults, setSimulationResults] = useState<StrategyResult[]>(
    [],
  );
  const [simulationError, setSimulationError] = useState<string>();

  const addStrategy = (strategy: StrategyRequest) => {
    // Override simulation months with global setting
    const strategyWithMonths = {
      ...strategy,
      simulation_months: simulationMonths,
    };
    setStrategies([...strategies, strategyWithMonths]);
  };

  const removeStrategy = (index: number) => {
    setStrategies(strategies.filter((_, i) => i !== index));
  };

  const loadSimulation = (preset: SimulationPreset) => {
    // Load all settings
    setAvailableCapital(preset.settings.availableCapital);
    setSimulationMonths(preset.settings.simulationMonths);
    setCurrency(preset.settings.currency);
    setAppreciationRate(preset.settings.appreciationRate);

    // Load property details
    setProperty(preset.property);

    // Load operating expenses
    setOperating(preset.operating);

    // Load capital injections
    setCapitalInjections(preset.capitalInjections);

    // Load strategies with proper simulation months and current interest rates
    const strategiesWithMonths = preset.strategies.map((strategy) => {
      const updatedStrategy = {
        ...strategy,
        simulation_months: preset.settings.simulationMonths,
      };

      // Fix custom_refinance_months: convert empty arrays to undefined
      if (
        Array.isArray(updatedStrategy.custom_refinance_months) &&
        updatedStrategy.custom_refinance_months.length === 0
      ) {
        updatedStrategy.custom_refinance_months = undefined;
      }

      // Override preset interest rate with current country default if available
      if (
        defaultInterestRate &&
        (strategy.strategy_type === "leveraged" ||
          strategy.strategy_type === "mixed")
      ) {
        updatedStrategy.interest_rate = defaultInterestRate;
      }

      return updatedStrategy;
    });
    setStrategies(strategiesWithMonths);

    // Clear any existing results
    setSimulationResults([]);
    setSimulationError(undefined);
  };

  const getCurrentSimulationData = (): SimulationPreset => {
    return {
      id: "current",
      name: "Current Simulation",
      description: "Current simulation configuration",
      created_date: new Date().toISOString().split("T")[0],
      settings: {
        availableCapital: availableCapital || 0,
        simulationMonths,
        currency,
        appreciationRate,
      },
      property,
      operating,
      capitalInjections,
      strategies,
    };
  };

  const applyCountrySettings = (
    settings: CountrySettings,
    investorType: "local" | "international",
  ) => {
    // Apply currency
    setCurrency(settings.currency);

    // Apply market settings
    setAppreciationRate(settings.market.appreciation_rate);

    // Apply property settings (operating expenses)
    setOperating((prev) => ({
      ...prev,
      vacancy_rate: settings.market.vacancy_rate,
      property_management_fee_rate:
        settings.market.property_management_fee_rate,
      monthly_insurance: settings.fees.insurance_rate
        ? ((property.purchase_price || 1000000) *
            settings.fees.insurance_rate) /
          12
        : prev.monthly_insurance,
    }));

    // Apply property costs
    setProperty((prev) => ({
      ...prev,
      transfer_duty: settings.fees.transfer_duty_rate
        ? (prev.purchase_price || 1000000) * settings.fees.transfer_duty_rate
        : settings.fees.conveyancing_fees || prev.transfer_duty,
      conveyancing_fees:
        settings.fees.conveyancing_fees || prev.conveyancing_fees,
      bond_registration:
        settings.fees.bond_registration || prev.bond_registration,
    }));

    // Set LTV restriction for international investors
    const investorSettings = settings.investor_type_settings[investorType];
    setCurrentLtvRestriction(investorSettings.mortgage.max_ltv);

    // Set default interest rate for new strategies
    setDefaultInterestRate(investorSettings.mortgage.default_interest_rate);

    // Override ALL existing strategy interest rates with country default rates
    // This ensures that loaded presets/simulations use local interest rates
    setStrategies((prevStrategies) =>
      prevStrategies.map((strategy) => ({
        ...strategy,
        interest_rate:
          strategy.strategy_type !== "cash_only"
            ? investorSettings.mortgage.default_interest_rate
            : strategy.interest_rate,
      })),
    );
  };

  const runSimulation = async () => {
    if (strategies.length === 0) {
      toast.error("No strategies to simulate", {
        description:
          "Please add at least one strategy before running simulation",
      });
      return;
    }

    setIsSimulating(true);
    setSimulationError(undefined);

    try {
      const request: SimulationRequest = {
        property,
        operating,
        available_capital: availableCapital || 0,
        capital_injections: capitalInjections,
        strategies,
        appreciation_rate: appreciationRate,
      };

      const data = await apiRequest<SimulationResponse>("simulate", {
        method: "POST",
        body: JSON.stringify(request),
      });

      if (data.success) {
        setSimulationResults(data.results);
      } else {
        const errorMsg = data.error || "Simulation failed";
        setSimulationError(errorMsg);
        toast.error("Simulation failed", {
          description: errorMsg,
        });
      }
    } catch (error) {
      console.error("Simulation error:", error);
      const errorMsg =
        error instanceof Error ? error.message : "Failed to run simulation";

      // Check for specific error types
      if (errorMsg.includes("429") || errorMsg.includes("rate limit")) {
        toast.error("Rate limit exceeded", {
          description: "Please wait a moment before running another simulation",
        });
      } else if (errorMsg.includes("timeout")) {
        toast.error("Simulation timeout", {
          description:
            "The simulation took too long to complete. Try reducing complexity.",
        });
      } else {
        toast.error("Connection error", {
          description: errorMsg,
        });
      }

      setSimulationError(errorMsg);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <SimulationButtons
            onLoadSimulation={loadSimulation}
            currentSimulationData={getCurrentSimulationData()}
          />
          <CountrySelector
            onSettingsApply={applyCountrySettings}
            selectedInvestorType={selectedInvestorType}
            onInvestorTypeChange={setSelectedInvestorType}
          />
        </div>
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Property Investment Calculator
          </h1>
          <p className="text-gray-600 mt-2">
            Compare investment strategies and simulate portfolio growth
          </p>
        </div>
      </div>

      {/* Settings Bar */}
      <div className="mb-8">
        <SettingsBar
          availableCapital={availableCapital}
          setAvailableCapital={setAvailableCapital}
          simulationMonths={simulationMonths}
          setSimulationMonths={setSimulationMonths}
          currency={currency}
          setCurrency={setCurrency}
          appreciationRate={appreciationRate}
          setAppreciationRate={setAppreciationRate}
        />
      </div>

      {/* Configuration Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <PropertyDetails
          property={property}
          setProperty={setProperty}
          currency={currency}
        />
        <OperatingExpenses
          operating={operating}
          setOperating={setOperating}
          currency={currency}
        />
        <CapitalInjections
          capitalInjections={capitalInjections}
          setCapitalInjections={setCapitalInjections}
          currency={currency}
        />
      </div>

      {/* Strategies Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 text-center mb-6">
          Strategies
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StrategyBuilder
            onAddStrategy={addStrategy}
            simulationMonths={simulationMonths}
            currentLtvRestriction={currentLtvRestriction}
            selectedInvestorType={selectedInvestorType}
            defaultInterestRate={defaultInterestRate}
          />
          <StrategyList
            strategies={strategies}
            onRemoveStrategy={removeStrategy}
          />
        </div>
      </div>

      {/* Simulate Button */}
      <div className="text-center mb-8">
        <Button
          onClick={runSimulation}
          disabled={isSimulating || strategies.length === 0}
          size="lg"
          className="px-8 py-4 text-lg font-semibold shadow-lg bg-green-600 hover:bg-green-700"
        >
          {isSimulating ? (
            <span className="flex items-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              Simulating...
            </span>
          ) : (
            `Simulate ${strategies.length} Strateg${
              strategies.length === 1 ? "y" : "ies"
            }`
          )}
        </Button>
        {strategies.length === 0 && (
          <p className="text-gray-500 text-sm mt-2">
            Add at least one strategy to enable simulation
          </p>
        )}
      </div>

      {/* Results Section */}
      {(simulationResults.length > 0 || isSimulating || simulationError) && (
        <>
          <div className="border-t-2 border-gray-300 my-8"></div>
          <SimulationResults
            results={simulationResults}
            currency={currency}
            isLoading={isSimulating}
            error={simulationError}
          />
        </>
      )}
    </div>
  );
}
