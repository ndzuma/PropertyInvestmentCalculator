"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StrategyResult } from "../types/api";
import SimulationResultsData from "./SimulationResultsData";
import SimulationResultsCharts from "./SimulationResultsCharts";

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

  return (
    <div className="bg-white p-8 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
        Simulation Results
      </h3>

      <Tabs defaultValue="data" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="data">Data</TabsTrigger>
          <TabsTrigger value="charts">Charts</TabsTrigger>
        </TabsList>

        <TabsContent value="data" className="mt-6">
          <SimulationResultsData results={results} currency={currency} />
        </TabsContent>

        <TabsContent value="charts" className="mt-6">
          <SimulationResultsCharts results={results} currency={currency} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
