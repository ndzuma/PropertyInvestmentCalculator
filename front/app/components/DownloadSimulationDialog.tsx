"use client";

import { useState } from "react";
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
import { Download, AlertCircle, CheckCircle } from "lucide-react";
import { SimulationPreset } from "../types/api";

interface DownloadSimulationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  simulationData: SimulationPreset;
}

export default function DownloadSimulationDialog({
  open,
  onOpenChange,
  simulationData,
}: DownloadSimulationDialogProps) {
  const [filename, setFilename] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownload = () => {
    if (!filename.trim()) {
      return;
    }

    setIsDownloading(true);

    try {
      // Create the download data with current timestamp
      const downloadData = {
        ...simulationData,
        name: filename,
        created_date: new Date().toISOString().split("T")[0],
        id: filename.toLowerCase().replace(/[^a-z0-9]/g, "-"),
      };

      // Create blob and download
      const blob = new Blob([JSON.stringify(downloadData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${filename.replace(/[^a-z0-9]/gi, "-").toLowerCase()}.json`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      setTimeout(() => {
        setDownloadSuccess(false);
        onOpenChange(false);
        setFilename("");
      }, 1500);
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleClose = () => {
    if (!isDownloading) {
      onOpenChange(false);
      setFilename("");
      setDownloadSuccess(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Download Simulation</DialogTitle>
          <DialogDescription>
            Save your current simulation configuration as a JSON file
          </DialogDescription>
        </DialogHeader>

        {downloadSuccess ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
              <p className="text-lg font-medium text-green-600">
                Download Successful!
              </p>
              <p className="text-sm text-gray-600">
                Your simulation has been saved
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Current Configuration Summary */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Current Configuration</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p>
                  Available Capital: {simulationData.settings.currency}
                  {simulationData.settings.availableCapital.toLocaleString()}
                </p>
                <p>
                  Property Price: {simulationData.settings.currency}
                  {simulationData.property.purchase_price.toLocaleString()}
                </p>
                <p>Strategies: {simulationData.strategies.length}</p>
                <p>
                  Capital Injections: {simulationData.capitalInjections.length}
                </p>
                <p>
                  Simulation Period: {simulationData.settings.simulationMonths}{" "}
                  months
                </p>
              </div>
            </div>

            {/* Warning Message */}
            <div className="flex items-start gap-2 text-amber-700 bg-amber-50 p-3 rounded-lg">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
              <div className="text-sm">
                <p className="font-medium">Save your work</p>
                <p>
                  This will download your complete simulation configuration. You
                  can load it later to restore all settings.
                </p>
              </div>
            </div>

            {/* Filename Input */}
            <div>
              <label
                htmlFor="filename"
                className="block text-sm font-medium mb-2"
              >
                Simulation Name
              </label>
              <Input
                id="filename"
                type="text"
                placeholder="e.g., My Property Strategy"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                className="w-full"
                disabled={isDownloading}
                maxLength={50}
              />
              <p className="text-xs text-gray-500 mt-1">
                This will be saved as:{" "}
                {filename
                  ? `${filename.replace(/[^a-z0-9]/gi, "-").toLowerCase()}.json`
                  : "filename.json"}
              </p>
            </div>
          </div>
        )}

        <DialogFooter>
          {!downloadSuccess && (
            <>
              <Button
                variant="outline"
                onClick={handleClose}
                disabled={isDownloading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleDownload}
                disabled={!filename.trim() || isDownloading}
                className="flex items-center gap-2"
              >
                {isDownloading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    Download
                  </>
                )}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
