"use client";

import { PropertyRequest } from "../types/api";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Button } from "@/components/ui/button";

interface PropertyDetailsProps {
  property: PropertyRequest;
  setProperty: (property: PropertyRequest) => void;
  currency: string;
}

export default function PropertyDetails({
  property,
  setProperty,
  currency,
}: PropertyDetailsProps) {
  const updateProperty = (field: keyof PropertyRequest, value: number) => {
    setProperty({
      ...property,
      [field]: value,
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Property Details
        </h3>
        <Button variant="outline" size="sm">
          Add
        </Button>
      </div>

      <div className="space-y-4">
        {/* Purchase Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Purchase Price
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={property.purchase_price}
              onChange={(e) =>
                updateProperty("purchase_price", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Transfer Duty */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transfer Duty
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={property.transfer_duty}
              onChange={(e) =>
                updateProperty("transfer_duty", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Conveyancing Fees */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Conveyancing Fees
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={property.conveyancing_fees}
              onChange={(e) =>
                updateProperty("conveyancing_fees", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Bond Registration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bond Registration
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={property.bond_registration}
              onChange={(e) =>
                updateProperty("bond_registration", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
          <p className="text-xs text-gray-500 mt-1">
            Set to 0 for cash purchases
          </p>
        </div>

        {/* Furnishing Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Furnishing Cost (Optional)
          </label>
          <InputGroup>
            <InputGroupAddon>{currency}</InputGroupAddon>
            <InputGroupInput
              type="number"
              value={property.furnishing_cost || 0}
              onChange={(e) =>
                updateProperty("furnishing_cost", Number(e.target.value))
              }
              min="0"
            />
          </InputGroup>
        </div>

        {/* Total Cost Display */}
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <strong>
              Total Property Cost: {currency}
              {(
                property.purchase_price +
                property.transfer_duty +
                property.conveyancing_fees +
                property.bond_registration +
                (property.furnishing_cost || 0)
              ).toLocaleString()}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}
