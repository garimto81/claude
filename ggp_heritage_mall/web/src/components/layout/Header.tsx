"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShoppingBag } from "lucide-react";
import { cn } from "@/lib/utils";
import { useCartStore } from "@/stores/cartStore";

export function Header() {
  const pathname = usePathname();
  const { items, maxItems, tierName } = useCartStore();
  const [isClient, setIsClient] = useState(false);

  // Handle hydration mismatch
  useEffect(() => {
    setIsClient(true);
  }, []);

  const selectedCount = isClient ? items.length : 0;

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/products", label: "Products" },
    { href: "/orders", label: "My Orders" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-[100] px-[60px] py-5 flex justify-between items-center bg-[rgba(10,10,10,0.95)] border-b border-[#2A2A2A] backdrop-blur-[10px]">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-[var(--color-gold)] to-[var(--color-gold-dark)] rounded-lg flex items-center justify-center font-heading font-bold text-[18px] text-[var(--color-background)]">
          GG
        </div>
        <span className="font-heading text-[20px] font-semibold tracking-[2px]">
          HERITAGE
        </span>
      </Link>

      {/* Navigation */}
      <nav className="flex gap-10">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "text-[13px] font-medium tracking-[1px] transition-colors duration-300",
              pathname === link.href
                ? "text-[var(--color-gold)]"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-gold)]"
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>

      {/* Right Section */}
      <div className="flex items-center gap-6">
        {/* Selection Indicator */}
        <div className="flex items-center gap-3 px-5 py-2.5 bg-[rgba(212,175,55,0.1)] border border-[var(--color-gold)] rounded-lg">
          <span className="text-[24px] font-semibold text-[var(--color-gold)]">
            {selectedCount}
          </span>
          <div className="text-[12px] text-[var(--color-text-secondary)] leading-tight">
            of <span className="text-[var(--color-text-primary)]">{maxItems}</span> items
            <br />
            <small>{tierName} Member</small>
          </div>
        </div>

        {/* Cart Button */}
        <Link
          href="/checkout"
          className="relative w-11 h-11 bg-[var(--color-surface)] border border-[#2A2A2A] rounded-full flex items-center justify-center transition-all duration-300 hover:border-[var(--color-gold)]"
        >
          <ShoppingBag className="w-5 h-5 text-[var(--color-text-primary)]" />
          {selectedCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-[var(--color-gold)] rounded-full text-[11px] font-semibold text-[var(--color-background)] flex items-center justify-center">
              {selectedCount}
            </span>
          )}
        </Link>
      </div>
    </header>
  );
}
