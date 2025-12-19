"use client";

import { useState } from "react";
import { User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export interface ShippingAddress {
  fullName: string;
  phone: string;
  zipCode: string;
  streetAddress: string;
  cityState: string;
  notes: string;
}

interface ShippingFormProps {
  initialData?: Partial<ShippingAddress>;
  onChange: (data: ShippingAddress) => void;
}

export function ShippingForm({ initialData, onChange }: ShippingFormProps) {
  const [isEditing, setIsEditing] = useState(!initialData?.fullName);
  const [formData, setFormData] = useState<ShippingAddress>({
    fullName: initialData?.fullName || "",
    phone: initialData?.phone || "",
    zipCode: initialData?.zipCode || "",
    streetAddress: initialData?.streetAddress || "",
    cityState: initialData?.cityState || "",
    notes: initialData?.notes || "",
  });

  const handleChange = (field: keyof ShippingAddress, value: string) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onChange(newData);
  };

  const hasSavedData = initialData?.fullName && initialData?.streetAddress;

  return (
    <div className="flex-1 p-[60px] border-r border-[#2A2A2A]">
      {/* Header */}
      <div className="mb-10">
        <h1 className="font-heading text-[32px] font-normal mb-2">
          Shipping Information
        </h1>
        <p className="text-[14px] text-[var(--color-text-secondary)]">
          Please review your saved shipping information and update if needed.
        </p>
      </div>

      {/* Saved Address Card */}
      {hasSavedData && !isEditing && (
        <div className="p-6 bg-[#151515] border border-[#2A2A2A] rounded-xl mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="flex items-center gap-2 text-[12px] font-medium tracking-[1px] text-[var(--color-gold)] uppercase">
              <User className="w-4 h-4" />
              Saved Information
            </span>
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-transparent border border-[#2A2A2A] rounded text-[12px] font-medium text-[var(--color-text-secondary)] hover:border-[var(--color-gold)] hover:text-[var(--color-gold)] transition-all"
            >
              Edit
            </button>
          </div>
          <div className="leading-[1.8]">
            <strong className="font-semibold">{formData.fullName}</strong>
            <br />
            {formData.phone}
            <br />
            {formData.streetAddress}
            <br />
            {formData.cityState} {formData.zipCode}
          </div>
        </div>
      )}

      {/* Form Sections */}
      {(isEditing || !hasSavedData) && (
        <>
          {/* Recipient Information */}
          <div className="mb-10">
            <h3 className="text-[14px] font-semibold tracking-[1px] text-[var(--color-gold)] uppercase mb-6 pb-3 border-b border-[#2A2A2A]">
              Recipient Information
            </h3>
            <div className="grid grid-cols-2 gap-5">
              <div className="space-y-2">
                <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                  Full Name *
                </Label>
                <Input
                  value={formData.fullName}
                  onChange={(e) => handleChange("fullName", e.target.value)}
                  className="px-5 py-4 bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)]"
                  placeholder="Enter your full name"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                  Phone Number *
                </Label>
                <Input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleChange("phone", e.target.value)}
                  className="px-5 py-4 bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)]"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
          </div>

          {/* Shipping Address */}
          <div className="mb-10">
            <h3 className="text-[14px] font-semibold tracking-[1px] text-[var(--color-gold)] uppercase mb-6 pb-3 border-b border-[#2A2A2A]">
              Shipping Address
            </h3>
            <div className="space-y-5">
              <div className="space-y-2 max-w-[150px]">
                <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                  ZIP Code *
                </Label>
                <Input
                  value={formData.zipCode}
                  onChange={(e) => handleChange("zipCode", e.target.value)}
                  className="px-5 py-4 bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)]"
                  placeholder="12345"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                  Street Address *
                </Label>
                <Input
                  value={formData.streetAddress}
                  onChange={(e) => handleChange("streetAddress", e.target.value)}
                  className="px-5 py-4 bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)]"
                  placeholder="123 Main Street, Apt 4B"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                  City, State *
                </Label>
                <Input
                  value={formData.cityState}
                  onChange={(e) => handleChange("cityState", e.target.value)}
                  className="px-5 py-4 bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)]"
                  placeholder="Las Vegas, NV"
                />
              </div>
            </div>
          </div>

          {/* Delivery Notes */}
          <div className="mb-10">
            <h3 className="text-[14px] font-semibold tracking-[1px] text-[var(--color-gold)] uppercase mb-6 pb-3 border-b border-[#2A2A2A]">
              Delivery Notes
            </h3>
            <div className="space-y-2">
              <Label className="text-[13px] font-medium text-[var(--color-text-secondary)]">
                Special Instructions (Optional)
              </Label>
              <Textarea
                value={formData.notes}
                onChange={(e) => handleChange("notes", e.target.value)}
                className="px-5 py-4 min-h-[100px] bg-[var(--color-surface)] border-[#2A2A2A] rounded-lg text-[15px] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:border-[var(--color-gold)] focus:ring-[3px] focus:ring-[rgba(212,175,55,0.1)] resize-y"
                placeholder="Enter any delivery instructions here..."
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
