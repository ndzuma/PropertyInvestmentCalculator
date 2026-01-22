"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, Upload } from "lucide-react";
import { toast } from "sonner";
import LoadSimulationDialog from "./LoadSimulationDialog";
import DownloadSimulationDialog from "./DownloadSimulationDialog";
import { SimulationPreset } from "../types/api";

interface SimulationButtonsProps {
  onLoadSimulation: (preset: SimulationPreset) => void;
  currentSimulationData: SimulationPreset;
}

const handleLoadSuccess = (
  preset: SimulationPreset,
  onLoadSimulation: (preset: SimulationPreset) => void,
) => {
  onLoadSimulation(preset);
  toast.success("Simulation loaded successfully", {
    description: `Loaded "${preset.name}" with ${preset.strategies.length} strategies`,
  });
};

const handleLoadError = (error: string) => {
  toast.error("Failed to load simulation", {
    description: error,
  });
};

export default function SimulationButtons({
  onLoadSimulation,
  currentSimulationData,
}: SimulationButtonsProps) {
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showDownloadDialog, setShowDownloadDialog] = useState(false);

  return (
    <>
      <div className="flex gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowLoadDialog(true)}
          className="flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          Load Simulation
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowDownloadDialog(true)}
          className="flex items-center gap-2"
        >
          <Download className="h-4 w-4" />
          Download Simulation
        </Button>
      </div>

      <LoadSimulationDialog
        open={showLoadDialog}
        onOpenChange={setShowLoadDialog}
        onLoadSimulation={(preset: SimulationPreset) =>
          handleLoadSuccess(preset, onLoadSimulation)
        }
        onLoadError={handleLoadError}
      />

      <DownloadSimulationDialog
        open={showDownloadDialog}
        onOpenChange={setShowDownloadDialog}
        simulationData={currentSimulationData}
      />
    </>
  );
}
