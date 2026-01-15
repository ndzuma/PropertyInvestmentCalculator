"use client";

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
  simulationYears: number;
  setSimulationYears: (value: number) => void;
  currency: string;
  setCurrency: (value: string) => void;
}

export default function SettingsBar({
  availableCapital,
  setAvailableCapital,
  simulationYears,
  setSimulationYears,
  currency,
  setCurrency,
}: SettingsBarProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex flex-col gap-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Simulation Settings
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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

          {/* Simulation Years */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Simulation Period
            </label>
            <InputGroup>
              <InputGroupInput
                type="number"
                value={simulationYears}
                onChange={(e) => setSimulationYears(Number(e.target.value))}
                min="1"
                max="50"
              />
              <InputGroupAddon align="inline-end">years</InputGroupAddon>
            </InputGroup>
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
        </div>
      </div>
    </div>
  );
}
