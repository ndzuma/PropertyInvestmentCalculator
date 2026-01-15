"use client";

interface SettingsBarProps {
  availableCapital: number;
  setAvailableCapital: (value: number) => void;
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
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                {currency}
              </span>
              <input
                type="number"
                value={availableCapital}
                onChange={(e) => setAvailableCapital(Number(e.target.value))}
                className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                placeholder="500000"
                min="0"
              />
            </div>
          </div>

          {/* Simulation Years */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Simulation Period
            </label>
            <div className="relative">
              <input
                type="number"
                value={simulationYears}
                onChange={(e) => setSimulationYears(Number(e.target.value))}
                className="w-full px-4 py-2 pr-16 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                placeholder="10"
                min="1"
                max="50"
              />
              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                years
              </span>
            </div>
          </div>

          {/* Currency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Currency
            </label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            >
              <option value="R">ZAR (R)</option>
              <option value="$">USD ($)</option>
              <option value="€">EUR (€)</option>
              <option value="£">GBP (£)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
