"use client";

import { PropertyRequest } from "../types/api";

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
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Property Details
      </h3>

      <div className="space-y-4">
        {/* Purchase Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Purchase Price
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={property.purchase_price}
              onChange={(e) =>
                updateProperty("purchase_price", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="1000000"
              min="0"
            />
          </div>
        </div>

        {/* Transfer Duty */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transfer Duty
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={property.transfer_duty}
              onChange={(e) =>
                updateProperty("transfer_duty", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="10000"
              min="0"
            />
          </div>
        </div>

        {/* Conveyancing Fees */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Conveyancing Fees
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={property.conveyancing_fees}
              onChange={(e) =>
                updateProperty("conveyancing_fees", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="15000"
              min="0"
            />
          </div>
        </div>

        {/* Bond Registration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bond Registration
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={property.bond_registration}
              onChange={(e) =>
                updateProperty("bond_registration", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="15000"
              min="0"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Set to 0 for cash purchases
          </p>
        </div>

        {/* Furnishing Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Furnishing Cost (Optional)
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {currency}
            </span>
            <input
              type="number"
              value={property.furnishing_cost || 0}
              onChange={(e) =>
                updateProperty("furnishing_cost", Number(e.target.value))
              }
              className="w-full pl-12 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              placeholder="50000"
              min="0"
            />
          </div>
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
