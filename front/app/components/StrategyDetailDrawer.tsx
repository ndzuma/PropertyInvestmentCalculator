"use client";

import { useState } from "react";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

import { StrategyResult } from "../types/api";

interface StrategyDetailDrawerProps {
  strategy: StrategyResult;
  currency: string;
  trigger: React.ReactNode;
}

export default function StrategyDetailDrawer({
  strategy,
  currency,
  trigger,
}: StrategyDetailDrawerProps) {
  const [open, setOpen] = useState(false);

  const formatCurrency = (amount: number) => {
    return `${currency}${amount.toLocaleString()}`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatPeriod = (period: number) => {
    if (period === 0) return "Start";
    if (period === 1) return "1 mo";
    if (period < 12) return `${period} mo`;

    const years = Math.floor(period / 12);
    const months = period % 12;

    if (months === 0) {
      return years === 1 ? "1 yr" : `${years} yr`;
    } else {
      return `${years}y ${months}m`;
    }
  };

  // Analyze purchases for breakdown
  const purchaseAnalysis = {
    cash: strategy.events.property_purchases.filter(
      (p) => p.financing_type === "cash",
    ).length,
    leveraged: strategy.events.property_purchases.filter(
      (p) => p.financing_type !== "cash",
    ).length,
    total: strategy.events.property_purchases.length,
  };

  // Analyze refinances
  const uniquePropertiesRefinanced = new Set(
    strategy.events.refinancing_events.map((r) => r.property_id),
  ).size;

  // Get key snapshots
  const initialSnapshot = strategy.snapshots[0];
  const finalSnapshot = strategy.snapshots[strategy.snapshots.length - 1];
  const midSnapshot =
    strategy.snapshots[Math.floor(strategy.snapshots.length / 2)];

  // Calculate growth metrics
  const equityGrowth =
    finalSnapshot.total_equity - initialSnapshot.total_equity;
  const portfolioValueGrowth =
    finalSnapshot.total_property_value - initialSnapshot.total_property_value;
  const cashFlowGrowth =
    finalSnapshot.monthly_cashflow - initialSnapshot.monthly_cashflow;

  return (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerTrigger asChild>{trigger}</DrawerTrigger>
      <DrawerContent className="max-h-[95vh]">
        <DrawerHeader>
          <DrawerTitle>
            {strategy.strategy_name} - Detailed Analysis
          </DrawerTitle>
          <DrawerDescription>
            Comprehensive breakdown of strategy performance, timeline, and
            portfolio composition
          </DrawerDescription>
        </DrawerHeader>

        <div className="p-4 overflow-y-auto space-y-6">
          {/* Strategy Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Strategy Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Simulation Period
                  </h4>
                  <p className="text-lg font-semibold">
                    {formatPeriod(finalSnapshot.period)}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Final Status
                  </h4>
                  {strategy.summary.simulation_ended ? (
                    <Badge variant="destructive">
                      Ended Early: {strategy.summary.end_reason}
                    </Badge>
                  ) : (
                    <Badge variant="default">Completed Successfully</Badge>
                  )}
                </div>
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Out-of-Pocket Investment
                  </h4>
                  <p className="text-lg font-semibold">
                    {formatCurrency(
                      strategy.summary.initial_available_capital +
                        strategy.events.capital_injections.reduce(
                          (sum, injection) => sum + injection.amount,
                          0,
                        ),
                    )}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Total Reinvestment
                  </h4>
                  <p className="text-lg font-semibold">
                    {formatCurrency(
                      strategy.summary.total_cash_invested -
                        strategy.summary.initial_available_capital -
                        strategy.events.capital_injections.reduce(
                          (sum, injection) => sum + injection.amount,
                          0,
                        ),
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Financial Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Financial Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Portfolio Value Growth
                  </h4>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-500">
                      {formatCurrency(initialSnapshot.total_property_value)} →{" "}
                      {formatCurrency(finalSnapshot.total_property_value)}
                    </p>
                    <p
                      className={`text-lg font-semibold ${
                        portfolioValueGrowth >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      +{formatCurrency(portfolioValueGrowth)}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Equity Growth
                  </h4>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-500">
                      {formatCurrency(initialSnapshot.total_equity)} →{" "}
                      {formatCurrency(finalSnapshot.total_equity)}
                    </p>
                    <p
                      className={`text-lg font-semibold ${
                        equityGrowth >= 0 ? "text-green-600" : "text-red-600"
                      }`}
                    >
                      +{formatCurrency(equityGrowth)}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Monthly Cashflow
                  </h4>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-500">
                      {formatCurrency(initialSnapshot.monthly_cashflow)} →{" "}
                      {formatCurrency(finalSnapshot.monthly_cashflow)}
                    </p>
                    <p
                      className={`text-lg font-semibold ${
                        cashFlowGrowth >= 0 ? "text-green-600" : "text-red-600"
                      }`}
                    >
                      {cashFlowGrowth >= 0 ? "+" : ""}
                      {formatCurrency(cashFlowGrowth)}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Return on Investment
                  </h4>
                  <p className="text-lg font-semibold text-blue-600">
                    {formatPercentage(
                      strategy.summary.total_cash_invested > 0
                        ? (strategy.summary.final_equity -
                            strategy.summary.total_cash_invested) /
                            strategy.summary.total_cash_invested
                        : 0,
                    )}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Net Rental Yield
                  </h4>
                  <p className="text-lg font-semibold text-purple-600">
                    {formatPercentage(finalSnapshot.net_rental_yield || 0)}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Annual Cashflow
                  </h4>
                  <p className="text-lg font-semibold text-green-600">
                    {formatCurrency(finalSnapshot.annual_cashflow || 0)}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    LTV Ratio
                  </h4>
                  <p className="text-lg font-semibold text-orange-600">
                    {formatPercentage(
                      finalSnapshot.total_property_value > 0
                        ? finalSnapshot.total_debt /
                            finalSnapshot.total_property_value
                        : 0,
                    )}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Annual Income
                  </h4>
                  <p className="text-lg font-semibold text-indigo-600">
                    {formatCurrency(
                      finalSnapshot.properties?.reduce(
                        (sum, prop) => sum + prop.annual_rental_income,
                        0,
                      ) || 0,
                    )}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Annual Expenses
                  </h4>
                  <p className="text-lg font-semibold text-red-600">
                    {formatCurrency(
                      finalSnapshot.properties?.reduce(
                        (sum, prop) => sum + prop.annual_expenses,
                        0,
                      ) || 0,
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Portfolio Composition */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Portfolio Composition</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Portfolio Value Summary */}
                <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="text-lg font-semibold text-blue-900 mb-2">
                    Total Portfolio Value:{" "}
                    {formatCurrency(finalSnapshot.total_property_value)}
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-blue-700">Total Debt: </span>
                      <span className="font-medium">
                        {formatCurrency(finalSnapshot.total_debt)}
                      </span>
                    </div>
                    <div>
                      <span className="text-blue-700">Total Equity: </span>
                      <span className="font-medium">
                        {formatCurrency(finalSnapshot.total_equity)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-gray-900">
                      {finalSnapshot.property_count}
                    </p>
                    <p className="text-sm text-gray-600">Total Properties</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {formatCurrency(finalSnapshot.total_equity)}
                    </p>
                    <p className="text-sm text-gray-600">Total Equity</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-orange-600">
                      {formatCurrency(finalSnapshot.total_debt)}
                    </p>
                    <p className="text-sm text-gray-600">Total Debt</p>
                  </div>
                </div>

                {/* Property Details Table */}
                {finalSnapshot.properties &&
                  finalSnapshot.properties.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium text-sm text-gray-600 mb-3">
                        Individual Properties
                      </h4>
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs border-collapse">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left p-2">Property</th>
                              <th className="text-right p-2">Value</th>
                              <th className="text-right p-2">Debt</th>
                              <th className="text-right p-2">Equity</th>
                              <th className="text-right p-2">LTV%</th>
                              <th className="text-right p-2">Monthly Income</th>
                              <th className="text-right p-2">
                                Monthly Expenses
                              </th>
                              <th className="text-right p-2">Cost Basis</th>
                              <th className="text-right p-2">Cashflow</th>
                            </tr>
                          </thead>
                          <tbody>
                            {finalSnapshot.properties.map((property) => (
                              <tr
                                key={property.property_id}
                                className="border-b"
                              >
                                <td className="p-2">
                                  Property {property.property_id}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(property.current_value)}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(property.loan_amount)}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(
                                    property.current_value -
                                      property.loan_amount,
                                  )}
                                </td>
                                <td className="text-right p-2">
                                  {property.current_value > 0
                                    ? formatPercentage(
                                        property.loan_amount /
                                          property.current_value,
                                      )
                                    : "0%"}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(
                                    property.annual_rental_income / 12,
                                  )}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(
                                    property.annual_expenses / 12,
                                  )}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(property.cost_basis)}
                                </td>
                                <td className="text-right p-2">
                                  {formatCurrency(property.monthly_cashflow)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
              </div>
            </CardContent>
          </Card>

          {/* Activity Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Activity Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Property Purchases
                  </h4>
                  <div className="space-y-1">
                    <p className="text-lg font-semibold">
                      {purchaseAnalysis.total} total
                    </p>
                    <p className="text-sm text-gray-500">
                      {purchaseAnalysis.cash} cash, {purchaseAnalysis.leveraged}{" "}
                      leveraged
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Refinancing Activity
                  </h4>
                  <div className="space-y-1">
                    <p className="text-lg font-semibold">
                      {strategy.events.refinancing_events.length} events
                    </p>
                    <p className="text-sm text-gray-500">
                      {uniquePropertiesRefinanced} properties affected
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Capital Injections
                  </h4>
                  <div className="space-y-1">
                    <p className="text-lg font-semibold">
                      {strategy.events.capital_injections.length} injections
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatCurrency(
                        strategy.events.capital_injections.reduce(
                          (sum, injection) => sum + injection.amount,
                          0,
                        ),
                      )}{" "}
                      total
                    </p>
                  </div>
                </div>
              </div>

              {/* Timeline of major events */}
              {strategy.events.chronological_events &&
                strategy.events.chronological_events.length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium text-sm text-gray-600 mb-3">
                      Major Events Timeline (Chronological)
                    </h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {strategy.events.chronological_events.map(
                        (event, index) => (
                          <div
                            key={`event-${index}`}
                            className={`flex justify-between items-center text-xs p-2 rounded ${
                              event.type === "purchase"
                                ? "bg-green-50"
                                : event.type === "refinance"
                                  ? "bg-blue-50"
                                  : "bg-yellow-50"
                            }`}
                          >
                            <span>
                              <span className="font-medium text-gray-600">
                                {formatPeriod(event.period)}:
                              </span>{" "}
                              {event.type === "purchase" &&
                                `Purchased Property ${event.property_id}`}
                              {event.type === "refinance" &&
                                `Refinanced Property ${event.property_id}`}
                              {event.type === "capital_injection" &&
                                `Capital Injection`}
                            </span>
                            <span className="font-medium">
                              {event.type === "purchase" &&
                                formatCurrency(event.purchase_price as number)}
                              {event.type === "refinance" &&
                                `${formatCurrency(event.cash_extracted as number)} extracted`}
                              {event.type === "capital_injection" &&
                                formatCurrency(event.amount as number)}
                            </span>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                )}
            </CardContent>
          </Card>

          {/* Key Milestones */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Key Milestones</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-3 border rounded-lg">
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Start
                  </h4>
                  <p className="text-sm">
                    {formatCurrency(initialSnapshot.total_equity)} equity
                  </p>
                  <p className="text-xs text-gray-500">
                    {initialSnapshot.property_count} properties
                  </p>
                </div>

                {strategy.snapshots.length > 2 && (
                  <div className="text-center p-3 border rounded-lg">
                    <h4 className="font-medium text-sm text-gray-600 mb-2">
                      Mid-Point ({formatPeriod(midSnapshot.period)})
                    </h4>
                    <p className="text-sm">
                      {formatCurrency(midSnapshot.total_equity)} equity
                    </p>
                    <p className="text-xs text-gray-500">
                      {midSnapshot.property_count} properties
                    </p>
                  </div>
                )}

                <div className="text-center p-3 border rounded-lg">
                  <h4 className="font-medium text-sm text-gray-600 mb-2">
                    Final
                  </h4>
                  <p className="text-sm">
                    {formatCurrency(finalSnapshot.total_equity)} equity
                  </p>
                  <p className="text-xs text-gray-500">
                    {finalSnapshot.property_count} properties
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="p-4 border-t">
          <DrawerClose asChild>
            <Button variant="outline" className="w-full">
              Close Details
            </Button>
          </DrawerClose>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
