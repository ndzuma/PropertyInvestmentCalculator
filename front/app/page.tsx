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
} from "./types/api";
import SettingsBar from "./components/SettingsBar";
import PropertyDetails from "./components/PropertyDetails";
import OperatingExpenses from "./components/OperatingExpenses";
import CapitalInjections from "./components/CapitalInjections";
import StrategyBuilder from "./components/StrategyBuilder";
import StrategyList from "./components/StrategyList";
import SimulationResults from "./components/SimulationResults";
import { Button } from "@/components/ui/button";

export default function Home() {
  // Settings state
  const [availableCapital, setAvailableCapital] = useState<number | undefined>(
    undefined,
  );
  const [simulationYears, setSimulationYears] = useState(10);
  const [currency, setCurrency] = useState("R");

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
    // Override simulation years with global setting
    const strategyWithYears = {
      ...strategy,
      simulation_years: simulationYears,
    };
    setStrategies([...strategies, strategyWithYears]);
  };

  const removeStrategy = (index: number) => {
    setStrategies(strategies.filter((_, i) => i !== index));
  };

  const runSimulation = async () => {
    if (strategies.length === 0) {
      alert("Please add at least one strategy to simulate");
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
      };

      const response = await fetch("http://localhost:8001/simulate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: SimulationResponse = await response.json();

      if (data.success) {
        setSimulationResults(data.results);
      } else {
        setSimulationError(data.error || "Simulation failed");
      }
    } catch (error) {
      console.error("Simulation error:", error);
      setSimulationError(
        error instanceof Error ? error.message : "Failed to run simulation",
      );
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Property Investment Calculator
        </h1>
        <p className="text-gray-600 mt-2">
          Compare investment strategies and simulate portfolio growth
        </p>
      </div>

      {/* Settings Bar */}
      <div className="mb-8">
        <SettingsBar
          availableCapital={availableCapital}
          setAvailableCapital={setAvailableCapital}
          simulationYears={simulationYears}
          setSimulationYears={setSimulationYears}
          currency={currency}
          setCurrency={setCurrency}
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
          <StrategyBuilder onAddStrategy={addStrategy} />
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
