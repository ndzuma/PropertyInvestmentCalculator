"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SettingsBarProps {
  availableCapital: number | undefined;
  setAvailableCapital: (value: number | undefined) => void;
  simulationMonths: number;
  setSimulationMonths: (value: number) => void;
  currency: string;
  setCurrency: (value: string) => void;
  appreciationRate: number;
  setAppreciationRate: (value: number) => void;
}

export default function SettingsBar({
  availableCapital,
  setAvailableCapital,
  simulationMonths,
  setSimulationMonths,
  currency,
  setCurrency,
  appreciationRate,
  setAppreciationRate,
}: SettingsBarProps) {
  const [periodUnit, setPeriodUnit] = useState<"months" | "years">("years");

  const getPeriodValue = () => {
    if (periodUnit === "years") {
      return Math.round(simulationMonths / 12);
    }
    return simulationMonths;
  };

  const setPeriodValue = (value: number) => {
    if (periodUnit === "years") {
      setSimulationMonths(value * 12);
    } else {
      setSimulationMonths(value);
    }
  };
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex flex-col gap-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Simulation Settings
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Available Capital */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Available Capital
            </label>
            <InputGroup>
              <InputGroupAddon>{currency}</InputGroupAddon>
              <InputGroupInput
                type="number"
                value={availableCapital || ""}
                onChange={(e) =>
                  setAvailableCapital(
                    e.target.value ? Number(e.target.value) : undefined,
                  )
                }
                min="0"
              />
            </InputGroup>
          </div>

          {/* Simulation Period */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Simulation Period
            </label>
            <div className="space-y-2">
              <Select
                value={periodUnit}
                onValueChange={setPeriodUnit as (value: string) => void}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="months">Months</SelectItem>
                  <SelectItem value="years">Years</SelectItem>
                </SelectContent>
              </Select>
              <InputGroup>
                <InputGroupInput
                  type="number"
                  value={getPeriodValue()}
                  onChange={(e) => setPeriodValue(Number(e.target.value))}
                  min="1"
                  max={periodUnit === "years" ? 50 : 600}
                />
                <InputGroupAddon align="inline-end">
                  {periodUnit}
                </InputGroupAddon>
              </InputGroup>
            </div>
          </div>

          {/* Currency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Currency
            </label>
            <Select value={currency} onValueChange={setCurrency}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="R">ZAR (R)</SelectItem>
                <SelectItem value="$">USD ($)</SelectItem>
                <SelectItem value="€">EUR (€)</SelectItem>
                <SelectItem value="£">GBP (£)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Estimated Asset Appreciation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Asset Appreciation Rate
            </label>
            <InputGroup>
              <InputGroupInput
                type="number"
                value={appreciationRate * 100}
                onChange={(e) =>
                  setAppreciationRate(Number(e.target.value) / 100)
                }
                min="0"
                max="50"
                step="0.1"
              />
              <InputGroupAddon align="inline-end">%</InputGroupAddon>
            </InputGroup>
            <p className="text-xs text-gray-500 mt-1">
              Annual property value appreciation rate
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
