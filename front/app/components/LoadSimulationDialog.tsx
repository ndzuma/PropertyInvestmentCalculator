"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { SimulationPreset, SimulationPresetIndex } from "../types/api";

interface LoadSimulationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onLoadSimulation: (preset: SimulationPreset) => void;
}

export default function LoadSimulationDialog({
  open,
  onOpenChange,
  onLoadSimulation,
}: LoadSimulationDialogProps) {
  const [presets, setPresets] = useState<SimulationPresetIndex["simulations"]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [uploadError, setUploadError] = useState<string>();
  const [selectedPreset, setSelectedPreset] = useState<string>();

  useEffect(() => {
    if (open) {
      loadPresets();
    }
  }, [open]);

  const loadPresets = async () => {
    try {
      setLoading(true);
      setError(undefined);
      const response = await fetch("/simulations/index.json");
      if (!response.ok) {
        throw new Error("Failed to load simulation presets");
      }
      const data: SimulationPresetIndex = await response.json();
      setPresets(data.simulations);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadPreset = async (filename: string) => {
    try {
      setLoading(true);
      setError(undefined);
      const response = await fetch(`/simulations/${filename}`);
      if (!response.ok) {
        throw new Error("Failed to load simulation preset");
      }
      const preset: SimulationPreset = await response.json();
      onLoadSimulation(preset);
      onOpenChange(false);
      setSelectedPreset(undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load preset");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadError(undefined);

    if (file.type !== "application/json") {
      setUploadError("Please select a valid JSON file");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const preset: SimulationPreset = JSON.parse(content);

        // Basic validation
        if (!preset.settings || !preset.property || !preset.operating || !preset.strategies) {
          throw new Error("Invalid simulation file format");
        }

        onLoadSimulation(preset);
        onOpenChange(false);
        setSelectedPreset(undefined);
      } catch (err) {
        setUploadError(err instanceof Error ? err.message : "Invalid JSON file");
      }
    };
    reader.readAsText(file);

    // Reset input
    event.target.value = "";
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Load Simulation</DialogTitle>
          <DialogDescription>
            Choose from predefined simulations or upload your own
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Predefined Simulations */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Predefined Simulations</h3>
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="grid gap-3">
                {presets.map((preset) => (
                  <Card
                    key={preset.id}
                    className={`p-4 cursor-pointer transition-colors hover:bg-gray-50 ${
                      selectedPreset === preset.id ? "ring-2 ring-blue-500" : ""
                    }`}
                    onClick={() => setSelectedPreset(preset.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{preset.name}</h4>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                            {preset.currency}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {preset.description}
                        </p>
                        <div className="flex gap-4 text-xs text-gray-500">
                          <span>Capital: {preset.currency}{preset.available_capital.toLocaleString()}</span>
                          <span>Property: {preset.preview.property_price}</span>
                          <span>{preset.preview.strategies} strategies</span>
                          <span>{preset.preview.timeframe}</span>
                        </div>
                      </div>
                      {selectedPreset === preset.id && (
                        <Button
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLoadPreset(preset.filename);
                          }}
                          disabled={loading}
                        >
                          Load
                        </Button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* File Upload */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-3">Upload Custom Simulation</h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
              <div className="text-center">
                <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <div className="mb-2">
                  <label htmlFor="simulation-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-500">
                      Choose a JSON file
                    </span>
                    <span className="text-gray-500"> or drag and drop</span>
                  </label>
                  <input
                    id="simulation-upload"
                    type="file"
                    accept=".json"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Upload a previously downloaded simulation file
                </p>
                {uploadError && (
                  <p className="text-xs text-red-600 mt-2">{uploadError}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
