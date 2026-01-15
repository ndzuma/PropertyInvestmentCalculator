"use client";

import { OperatingRequest } from "../types/api";

interface OperatingExpensesProps {
  operating: OperatingRequest;
  setOperating: (operating: OperatingRequest) => void;
  currency: string;
}

export default function OperatingExpenses({
  operating,
  setOperating,
  currency,
}: OperatingExpensesProps) {
  const updateOperating = (field: keyof OperatingRequest, value: number) => {
    setOperating({
      ...operating,
      [field]: value,
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Operating Expenses
      </h3>

      <div className="space-y-4">
        {/* Monthly Rental Income */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Rental Income
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={operating.monthly_rental_income}
              onChange={(e) =>
                updateOperating("monthly_rental_income", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="12000"
              min="0"
            />
          </div>
        </div>

        {/* Vacancy Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vacancy Rate
          </label>
          <div className="relative">
            <input
              type="number"
              value={operating.vacancy_rate * 100}
              onChange={(e) =>
                updateOperating("vacancy_rate", Number(e.target.value) / 100)
              }
              className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="5"
              min="0"
              max="100"
              step="0.1"
            />
            <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              %
            </span>
          </div>
        </div>

        {/* Monthly Levies */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Levies
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={operating.monthly_levies}
              onChange={(e) =>
                updateOperating("monthly_levies", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="1500"
              min="0"
            />
          </div>
        </div>

        {/* Property Management Fee Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Property Management Fee
          </label>
          <div className="relative">
            <input
              type="number"
              value={operating.property_management_fee_rate * 100}
              onChange={(e) =>
                updateOperating(
                  "property_management_fee_rate",
                  Number(e.target.value) / 100,
                )
              }
              className="w-full px-4 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="8"
              min="0"
              max="100"
              step="0.1"
            />
            <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              %
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Percentage of rental income
          </p>
        </div>

        {/* Monthly Insurance */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Insurance
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={operating.monthly_insurance}
              onChange={(e) =>
                updateOperating("monthly_insurance", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="600"
              min="0"
            />
          </div>
        </div>

        {/* Monthly Maintenance Reserve */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Maintenance Reserve
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={operating.monthly_maintenance_reserve}
              onChange={(e) =>
                updateOperating(
                  "monthly_maintenance_reserve",
                  Number(e.target.value),
                )
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="800"
              min="0"
            />
          </div>
        </div>

        {/* Monthly Furnishing Repair Costs */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Furnishing/Repair Costs (Optional)
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={operating.monthly_furnishing_repair_costs || 0}
              onChange={(e) =>
                updateOperating(
                  "monthly_furnishing_repair_costs",
                  Number(e.target.value),
                )
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="300"
              min="0"
            />
          </div>
        </div>

        {/* Summary */}
        <div className="pt-4 border-t border-gray-200">
          <div className="space-y-2 text-sm text-gray-600">
            <div>
              <strong>
                Effective Monthly Rental: {currency}
                {(
                  operating.monthly_rental_income *
                  (1 - operating.vacancy_rate)
                ).toLocaleString()}
              </strong>
            </div>
            <div>
              <strong>
                Total Monthly Expenses: {currency}
                {(
                  operating.monthly_levies +
                  operating.monthly_rental_income *
                    (1 - operating.vacancy_rate) *
                    operating.property_management_fee_rate +
                  operating.monthly_insurance +
                  operating.monthly_maintenance_reserve +
                  (operating.monthly_furnishing_repair_costs || 0)
                ).toLocaleString()}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
