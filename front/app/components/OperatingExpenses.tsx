"use client";

import { OperatingRequest } from "../types/api";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Button } from "@/components/ui/button";

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
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Operating Expenses
        </h3>
        <Button variant="outline" size="sm">
          Add
        </Button>
      </div>

      <div className="space-y-4">
        {/* Monthly Rental Income */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Rental Income
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={operating.monthly_rental_income}
              onChange={(e) =>
                updateOperating("monthly_rental_income", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Vacancy Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vacancy Rate
          </label>
          <InputGroup>
            <InputGroupInput
              type="number"
              value={operating.vacancy_rate * 100}
              onChange={(e) =>
                updateOperating("vacancy_rate", Number(e.target.value) / 100)
              }
              min="0"
              max="100"
              step="0.1"
            />
            <InputGroupAddon align="inline-end">%</InputGroupAddon>
          </InputGroup>
        </div>

        {/* Monthly Levies */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Levies
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={operating.monthly_levies}
              onChange={(e) =>
                updateOperating("monthly_levies", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Property Management Fee Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Property Management Fee
          </label>
          <InputGroup>
            <InputGroupInput
              type="number"
              value={operating.property_management_fee_rate * 100}
              onChange={(e) =>
                updateOperating(
                  "property_management_fee_rate",
                  Number(e.target.value) / 100,
                )
              }
              min="0"
              max="100"
              step="0.1"
            />
            <InputGroupAddon align="inline-end">%</InputGroupAddon>
          </InputGroup>
          <p className="text-xs text-gray-500 mt-1">
            Percentage of rental income
          </p>
        </div>

        {/* Monthly Insurance */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Insurance
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={operating.monthly_insurance}
              onChange={(e) =>
                updateOperating("monthly_insurance", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Monthly Maintenance Reserve */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Maintenance Reserve
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={operating.monthly_maintenance_reserve}
              onChange={(e) =>
                updateOperating(
                  "monthly_maintenance_reserve",
                  Number(e.target.value),
                )
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Monthly Furnishing Repair Costs */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Furnishing/Repair Costs (Optional)
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={operating.monthly_furnishing_repair_costs || 0}
              onChange={(e) =>
                updateOperating(
                  "monthly_furnishing_repair_costs",
                  Number(e.target.value),
                )
              }
              min="0"
            />
          </InputGroup>
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
