"use client";

import { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Globe, AlertTriangle } from "lucide-react";
import { CountryIndex, CountryData, CountrySettings } from "../types/api";

interface CountrySelectorProps {
  onSettingsApply: (settings: CountrySettings, investorType: "local" | "international") => void;
  selectedInvestorType: "local" | "international";
  onInvestorTypeChange: (type: "local" | "international") => void;
}

export default function CountrySelector({
  onSettingsApply,
  selectedInvestorType,
  onInvestorTypeChange,
}: CountrySelectorProps) {
  const [countries, setCountries] = useState<CountryIndex["countries"]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [selectedCity, setSelectedCity] = useState<string>("");
  const [selectedSuburb, setSelectedSuburb] = useState<string>("");

  const [countryData, setCountryData] = useState<CountryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  // Load countries list on mount
  useEffect(() => {
    const loadCountries = async () => {
      try {
        const response = await fetch("/country-settings/index.json");
        if (!response.ok) throw new Error("Failed to load countries");
        const data: CountryIndex = await response.json();
        setCountries(data.countries);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load countries");
      }
    };

    loadCountries();
  }, []);

  // Load country data when country is selected
  useEffect(() => {
    if (!selectedCountry) return;

    const loadCountryData = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const country = countries.find(c => c.id === selectedCountry);
        if (!country) throw new Error("Country not found");

        const response = await fetch(`/country-settings/${country.filename}`);
        if (!response.ok) throw new Error("Failed to load country data");
        const data: CountryData = await response.json();
        setCountryData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load country data");
        setCountryData(null);
      } finally {
        setLoading(false);
      }
    };

    loadCountryData();
  }, [selectedCountry, countries]);

  // Reset selections when parent selection changes
  useEffect(() => {
    setSelectedRegion("");
    setSelectedCity("");
    setSelectedSuburb("");
  }, [selectedCountry]);

  useEffect(() => {
    setSelectedCity("");
    setSelectedSuburb("");
  }, [selectedRegion]);

  useEffect(() => {
    setSelectedSuburb("");
  }, [selectedCity]);

  const getCurrentSettings = (): CountrySettings | null => {
    if (!countryData) return null;

    // Get the most specific settings available
    if (selectedSuburb && selectedCity && selectedRegion) {
      const region = countryData.regions.find(r => r.id === selectedRegion);
      const city = region?.cities.find(c => c.id === selectedCity);
      const suburb = city?.suburbs.find(s => s.id === selectedSuburb);
      if (suburb) return suburb.settings;
    }

    if (selectedCity && selectedRegion) {
      const region = countryData.regions.find(r => r.id === selectedRegion);
      const city = region?.cities.find(c => c.id === selectedCity);
      if (city) return city.settings;
    }

    if (selectedRegion) {
      const region = countryData.regions.find(r => r.id === selectedRegion);
      if (region) return region.settings;
    }

    return countryData.settings;
  };

  const applySettings = () => {
    const settings = getCurrentSettings();
    if (settings) {
      onSettingsApply(settings, selectedInvestorType);
    }
  };

  const getSelectedRegion = () => countryData?.regions.find(r => r.id === selectedRegion);
  const getSelectedCity = () => getSelectedRegion()?.cities.find(c => c.id === selectedCity);

  const hasLtvRestriction = () => {
    const settings = getCurrentSettings();
    if (!settings || selectedInvestorType === "local") return false;
    return settings.investor_type_settings.international.mortgage.max_ltv !== null;
  };

  const getLtvRestriction = () => {
    const settings = getCurrentSettings();
    if (!settings || selectedInvestorType === "local") return null;
    return settings.investor_type_settings.international.mortgage.max_ltv;
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <Globe className="h-4 w-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Location:</span>
      </div>

      {/* Country Selection */}
      <Select value={selectedCountry} onValueChange={setSelectedCountry}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Country" />
        </SelectTrigger>
        <SelectContent>
          {countries.map((country) => (
            <SelectItem key={country.id} value={country.id}>
              <span className="flex items-center gap-2">
                <span>{country.flag}</span>
                <span>{country.name}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Region Selection */}
      {countryData && countryData.regions.length > 0 && (
        <Select value={selectedRegion} onValueChange={setSelectedRegion}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Region" />
          </SelectTrigger>
          <SelectContent>
            {countryData.regions.map((region) => (
              <SelectItem key={region.id} value={region.id}>
                {region.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {/* City Selection */}
      {getSelectedRegion() && getSelectedRegion()!.cities.length > 0 && (
        <Select value={selectedCity} onValueChange={setSelectedCity}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="City" />
          </SelectTrigger>
          <SelectContent>
            {getSelectedRegion()!.cities.map((city) => (
              <SelectItem key={city.id} value={city.id}>
                {city.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {/* Suburb Selection */}
      {getSelectedCity() && getSelectedCity()!.suburbs.length > 0 && (
        <Select value={selectedSuburb} onValueChange={setSelectedSuburb}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Area" />
          </SelectTrigger>
          <SelectContent>
            {getSelectedCity()!.suburbs.map((suburb) => (
              <SelectItem key={suburb.id} value={suburb.id}>
                {suburb.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {/* Investor Type Selection */}
      {getCurrentSettings() && (
        <Select value={selectedInvestorType} onValueChange={onInvestorTypeChange}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="local">Local</SelectItem>
            <SelectItem value="international">International</SelectItem>
          </SelectContent>
        </Select>
      )}

      {/* LTV Warning */}
      {hasLtvRestriction() && (
        <div className="flex items-center gap-1 text-amber-600">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-xs">
            Max LTV: {(getLtvRestriction()! * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {/* Apply Button */}
      {getCurrentSettings() && (
        <Button
          size="sm"
          onClick={applySettings}
          disabled={loading}
          className="flex items-center gap-1"
        >
          Apply Settings
        </Button>
      )}

      {/* Error Display */}
      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
    </div>
  );
}
