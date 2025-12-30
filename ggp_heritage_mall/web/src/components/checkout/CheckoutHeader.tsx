"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";

interface Step {
  number: number;
  label: string;
  status: "completed" | "active" | "pending";
}

interface CheckoutHeaderProps {
  currentStep: number;
}

export function CheckoutHeader({ currentStep }: CheckoutHeaderProps) {
  const steps: Step[] = [
    { number: 1, label: "Select Items", status: currentStep > 1 ? "completed" : currentStep === 1 ? "active" : "pending" },
    { number: 2, label: "Shipping Info", status: currentStep > 2 ? "completed" : currentStep === 2 ? "active" : "pending" },
    { number: 3, label: "Complete", status: currentStep === 3 ? "active" : "pending" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-[100] px-[60px] py-5 flex justify-between items-center bg-[rgba(10,10,10,0.95)] border-b border-[#2A2A2A] backdrop-blur-[10px]">
      <Link href="/" className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-[var(--color-gold)] to-[var(--color-gold-dark)] rounded-lg flex items-center justify-center font-heading font-bold text-[18px] text-[var(--color-background)]">
          GG
        </div>
        <span className="font-heading text-[20px] font-semibold tracking-[2px]">
          HERITAGE
        </span>
      </Link>

      <div className="flex items-center gap-4">
        {steps.map((step, index) => (
          <div key={step.number} className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-semibold border-2 transition-all",
                  step.status === "completed" &&
                    "bg-[var(--color-gold)] border-[var(--color-gold)] text-[var(--color-background)]",
                  step.status === "active" &&
                    "border-[var(--color-gold)] text-[var(--color-gold)]",
                  step.status === "pending" &&
                    "border-[#2A2A2A] text-[var(--color-text-secondary)]"
                )}
              >
                {step.number}
              </div>
              <span
                className={cn(
                  "text-[13px]",
                  step.status === "active"
                    ? "text-[var(--color-text-primary)]"
                    : "text-[var(--color-text-secondary)]"
                )}
              >
                {step.label}
              </span>
            </div>

            {index < steps.length - 1 && (
              <div
                className={cn(
                  "w-10 h-0.5",
                  step.status === "completed"
                    ? "bg-[var(--color-gold)]"
                    : "bg-[#2A2A2A]"
                )}
              />
            )}
          </div>
        ))}
      </div>

      <div className="w-[100px]" />
    </header>
  );
}
