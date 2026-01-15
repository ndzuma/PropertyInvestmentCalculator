"use client";

import { useState } from "react";
import {
  CapitalInjectionRequest,
  CapitalInjectionFrequency,
} from "../types/api";
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

interface CapitalInjectionsProps {
  capitalInjections: CapitalInjectionRequest[];
  setCapitalInjections: (injections: CapitalInjectionRequest[]) => void;
  currency: string;
}

export default function CapitalInjections({
  capitalInjections,
  setCapitalInjections,
  currency,
}: CapitalInjectionsProps) {
  const [newInjection, setNewInjection] = useState<CapitalInjectionRequest>({
    amount: undefined,
    frequency: "monthly",
    start_period: 1,
    end_period: undefined,
    specific_periods: undefined,
  });

  const [, setShowSpecificPeriods] = useState(false);
  const [specificPeriodsInput, setSpecificPeriodsInput] = useState("");

  const addInjection = () => {
    if (!newInjection.amount || newInjection.amount <= 0) return;

    const injection: CapitalInjectionRequest = {
      ...newInjection,
      specific_periods:
        newInjection.frequency === "one_time"
          ? specificPeriodsInput
              .split(",")
              .map((p) => parseInt(p.trim()))
              .filter((p) => !isNaN(p))
          : undefined,
    };

    setCapitalInjections([...capitalInjections, injection]);

    // Reset form
    setNewInjection({
      amount: undefined,
      frequency: "monthly",
      start_period: 1,
      end_period: undefined,
      specific_periods: undefined,
    });
    setSpecificPeriodsInput("");
    setShowSpecificPeriods(false);
  };

  const removeInjection = (index: number) => {
    setCapitalInjections(capitalInjections.filter((_, i) => i !== index));
  };

  const formatFrequency = (frequency: CapitalInjectionFrequency) => {
    switch (frequency) {
      case "monthly":
        return "Monthly";
      case "quarterly":
        return "Quarterly";
      case "yearly":
        return "Yearly";
      case "five_yearly":
        return "Every 5 Years";
      case "one_time":
        return "One-time";
      default:
        return frequency;
    }
  };

  const formatInjectionDescription = (injection: CapitalInjectionRequest) => {
    let description = `${currency}${injection.amount?.toLocaleString() || 0} - ${formatFrequency(injection.frequency)}`;

    if (injection.frequency === "one_time" && injection.specific_periods) {
      description += ` (Periods: ${injection.specific_periods.join(", ")})`;
    } else {
      description += ` (Period ${injection.start_period}`;
      if (injection.end_period) {
        description += ` to ${injection.end_period}`;
      } else {
        description += ` onwards`;
      }
      description += `)`;
    }

    return description;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Capital Injections
      </h3>

      {/* Add New Injection Form */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount
            </label>
            <InputGroup>
              <InputGroupAddon>{currency}</InputGroupAddon>
              <InputGroupInput
                type="number"
                value={newInjection.amount || ""}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    amount: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                min="0"
              />
            </InputGroup>
          </div>

          {/* Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <Select
              value={newInjection.frequency}
              onValueChange={(value: CapitalInjectionFrequency) => {
                setNewInjection({ ...newInjection, frequency: value });
                setShowSpecificPeriods(value === "one_time");
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
                <SelectItem value="five_yearly">Every 5 Years</SelectItem>
                <SelectItem value="one_time">One-time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Period Configuration */}
        {newInjection.frequency === "one_time" ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Periods (comma-separated)
            </label>
            <Input
              type="text"
              value={specificPeriodsInput}
              onChange={(e) => setSpecificPeriodsInput(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Example: 24, 48 (for periods 24 and 48)
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Start Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Period
              </label>
              <Input
                type="number"
                value={newInjection.start_period}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    start_period: Number(e.target.value),
                  })
                }
                min="1"
              />
            </div>

            {/* End Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Period (Optional)
              </label>
              <Input
                type="number"
                value={newInjection.end_period || ""}
                onChange={(e) =>
                  setNewInjection({
                    ...newInjection,
                    end_period: e.target.value
                      ? Number(e.target.value)
                      : undefined,
                  })
                }
                min="1"
              />
            </div>
          </div>
        )}

        <Button
          onClick={addInjection}
          disabled={!newInjection.amount || newInjection.amount <= 0}
          variant="default"
        >
          Add Capital Injection
        </Button>
      </div>

      {/* Existing Injections List */}
      {capitalInjections.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-3">
            Added Capital Injections
          </h4>
          <div className="space-y-2">
            {capitalInjections.map((injection, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <span className="text-sm text-gray-700">
                  {formatInjectionDescription(injection)}
                </span>
                <Button
                  onClick={() => removeInjection(index)}
                  variant="destructive"
                  size="sm"
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>

          {/* Total Summary */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <strong>
                Total Ongoing Injections: {currency}
                {capitalInjections
                  .filter((inj) => inj.frequency !== "one_time")
                  .reduce((sum, inj) => sum + (inj.amount || 0), 0)
                  .toLocaleString()}{" "}
                per period
              </strong>
            </div>
            {capitalInjections.some((inj) => inj.frequency === "one_time") && (
              <div className="text-sm text-gray-600">
                <strong>
                  One-time Injections: {currency}
                  {capitalInjections
                    .filter((inj) => inj.frequency === "one_time")
                    .reduce(
                      (sum, inj) =>
                        sum +
                        (inj.amount || 0) * (inj.specific_periods?.length || 1),
                      0,
                    )
                    .toLocaleString()}
                </strong>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
