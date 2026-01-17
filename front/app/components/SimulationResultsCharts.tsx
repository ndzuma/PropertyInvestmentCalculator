"use client";

import { useState } from "react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { StrategyResult } from "../types/api";

interface SimulationResultsChartsProps {
  results: StrategyResult[];
  currency: string;
}

type MetricKey =
  | "total_property_value"
  | "total_equity"
  | "monthly_cashflow"
  | "cash_available"
  | "property_count"
  | "total_debt"
  | "total_cash_invested"
  | "rental_yield"
  | "cash_on_cash_return"
  | "return_on_investment";

interface ChartMetric {
  label: string;
  title: string;
  description: string;
  formatType: "currency" | "percentage" | "number";
}

const chartMetrics: Record<MetricKey, ChartMetric> = {
  total_property_value: {
    label: "Portfolio Value",
    title: "Portfolio Value Over Time",
    description: "Total property portfolio value progression",
    formatType: "currency",
  },
  total_equity: {
    label: "Total Equity",
    title: "Total Equity Over Time",
    description: "Portfolio equity growth comparison across strategies",
    formatType: "currency",
  },
  monthly_cashflow: {
    label: "Monthly Cashflow",
    title: "Monthly Cashflow Over Time",
    description: "Monthly cash generation comparison",
    formatType: "currency",
  },
  cash_available: {
    label: "Cash Available",
    title: "Cash Available Over Time",
    description: "Available cash reserves progression",
    formatType: "currency",
  },
  property_count: {
    label: "Property Count",
    title: "Property Count Over Time",
    description: "Number of properties acquired by strategy",
    formatType: "number",
  },
  total_debt: {
    label: "Total Debt",
    title: "Total Debt Over Time",
    description: "Portfolio debt levels comparison",
    formatType: "currency",
  },
  total_cash_invested: {
    label: "Cash Invested",
    title: "Total Cash Invested Over Time",
    description: "Cumulative cash investment progression",
    formatType: "currency",
  },
  rental_yield: {
    label: "Rental Yield",
    title: "Rental Yield Over Time",
    description: "Portfolio rental yield performance",
    formatType: "percentage",
  },
  cash_on_cash_return: {
    label: "Cash on Cash Return",
    title: "Cash on Cash Return Over Time",
    description: "Cash return on investment performance",
    formatType: "percentage",
  },
  return_on_investment: {
    label: "Return on Investment",
    title: "Return on Investment Over Time",
    description: "Total return on investment comparison",
    formatType: "percentage",
  },
};

export default function SimulationResultsCharts({
  results,
  currency,
}: SimulationResultsChartsProps) {
  const [selectedMetric, setSelectedMetric] = useState<MetricKey>(
    "total_property_value",
  );
  const currentMetric = chartMetrics[selectedMetric];

  // Transform snapshots data into chart format
  const transformDataForChart = () => {
    if (results.length === 0) return [];

    // Get all unique periods across all strategies
    const allPeriods = new Set<number>();
    results.forEach((result) => {
      result.snapshots.forEach((snapshot) => {
        if (typeof snapshot.period === "number" && !isNaN(snapshot.period)) {
          allPeriods.add(snapshot.period);
        }
      });
    });

    const sortedPeriods = Array.from(allPeriods).sort((a, b) => a - b);

    // Create chart data with period as x-axis and strategy equity as y-values
    return sortedPeriods.map((period) => {
      const dataPoint: Record<string, number> = { period };

      results.forEach((result) => {
        // Find exact snapshot for this period
        const snapshot = result.snapshots.find((s) => s.period === period);
        if (snapshot && typeof snapshot[selectedMetric] === "number") {
          dataPoint[result.strategy_name] = snapshot[selectedMetric];
        } else {
          // Set to 0 for missing data points
          dataPoint[result.strategy_name] = 0;
        }
      });

      return dataPoint;
    });
  };

  // Create dynamic chart config based on strategy names
  const createChartConfig = (): ChartConfig => {
    const config: ChartConfig = {};
    const chartColors = [
      "var(--chart-1)",
      "var(--chart-2)",
      "var(--chart-3)",
      "var(--chart-4)",
      "var(--chart-5)",
    ];

    results.forEach((result, index) => {
      config[result.strategy_name] = {
        label: result.strategy_name,
        color: chartColors[index % chartColors.length],
      };
    });

    return config;
  };

  const formatCurrency = (amount: number) => {
    return `${currency}${amount.toLocaleString()}`;
  };

  const formatValue = (value: number) => {
    switch (currentMetric.formatType) {
      case "currency":
        return formatCurrency(value);
      case "percentage":
        return `${(value * 100).toFixed(1)}%`;
      case "number":
        return value.toString();
      default:
        return value.toString();
    }
  };

  const formatYAxisValue = (value: number) => {
    switch (currentMetric.formatType) {
      case "currency":
        if (value >= 1000000) {
          return `${currency}${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
          return `${currency}${(value / 1000).toFixed(0)}K`;
        }
        return `${currency}${value.toLocaleString()}`;
      case "percentage":
        return `${(value * 100).toFixed(0)}%`;
      case "number":
        return value.toString();
      default:
        return value.toString();
    }
  };

  const formatPeriod = (period: number) => {
    if (isNaN(period) || period < 0) return "Start";
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

  const chartData = transformDataForChart();
  const chartConfig = createChartConfig();

  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-500">No data available for charting.</p>
      </div>
    );
  }

  // Find the maximum value for better Y-axis scaling
  const maxValue = Math.max(
    ...chartData.flatMap((dataPoint) =>
      Object.keys(dataPoint)
        .filter((key) => key !== "period")
        .map((key) => dataPoint[key] || 0),
    ),
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{currentMetric.title}</CardTitle>
              <CardDescription>{currentMetric.description}</CardDescription>
            </div>
            <Select
              value={selectedMetric}
              onValueChange={(value: MetricKey) => setSelectedMetric(value)}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(chartMetrics).map(([key, metric]) => (
                  <SelectItem key={key} value={key}>
                    {metric.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="min-h-[150px] max-h-100 w-full">
            <LineChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 20,
                right: 20,
                top: 20,
                bottom: 20,
              }}
            >
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis
                dataKey="period"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => formatPeriod(Number(value))}
                interval="preserveStartEnd"
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={formatYAxisValue}
                domain={[0, maxValue * 1.1]}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              {results.map((result, index) => {
                const chartColors = [
                  "var(--chart-1)",
                  "var(--chart-2)",
                  "var(--chart-3)",
                  "var(--chart-4)",
                  "var(--chart-5)",
                ];
                const color = chartColors[index % chartColors.length];

                return (
                  <Line
                    key={result.strategy_name}
                    dataKey={result.strategy_name}
                    type="monotone"
                    stroke={color}
                    strokeWidth={3}
                    dot={false}
                    activeDot={{
                      r: 5,
                      fill: color,
                      strokeWidth: 2,
                      stroke: "var(--background)",
                    }}
                    connectNulls={false}
                  />
                );
              })}
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Chart Summary */}
      {results.length > 1 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((result) => {
            const finalSnapshot = result.snapshots[result.snapshots.length - 1];
            const initialSnapshot = result.snapshots[0];
            const finalValue = finalSnapshot[selectedMetric];
            const initialValue = initialSnapshot[selectedMetric];
            const growth = finalValue - initialValue;
            const growthPercentage =
              initialValue > 0 ? (growth / initialValue) * 100 : 0;

            return (
              <Card key={result.strategy_name}>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          chartConfig[result.strategy_name]?.color,
                      }}
                    />
                    <h4 className="font-semibold text-sm">
                      {result.strategy_name}
                    </h4>
                  </div>
                  <div className="mt-3 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">
                        Final {currentMetric.label}:
                      </span>
                      <span className="text-sm font-medium">
                        {formatValue(finalValue)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">Growth:</span>
                      <span
                        className={`text-sm font-medium ${
                          growth >= 0 ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {growth >= 0 ? "+" : ""}
                        {formatValue(growth)} (
                        {growthPercentage >= 0 ? "+" : ""}
                        {growthPercentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
