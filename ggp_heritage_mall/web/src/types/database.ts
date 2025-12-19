export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type VipTier = "silver" | "gold";
export type RegistrationType = "email_invite" | "qr_code";
export type OrderStatus = "pending" | "processing" | "shipped" | "delivered" | "cancelled";
export type VerificationStatus = "pending" | "approved" | "rejected";

export interface Database {
  public: {
    Tables: {
      vips: {
        Row: {
          id: string;
          email: string;
          name: string | null;
          tier: VipTier;
          reg_type: RegistrationType;
          invite_token: string;
          shipping_address: Json | null;
          is_active: boolean;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          email: string;
          name?: string | null;
          tier?: VipTier;
          reg_type?: RegistrationType;
          invite_token?: string;
          shipping_address?: Json | null;
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          email?: string;
          name?: string | null;
          tier?: VipTier;
          reg_type?: RegistrationType;
          invite_token?: string;
          shipping_address?: Json | null;
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
      };
      verification_codes: {
        Row: {
          id: string;
          vip_id: string;
          code: string;
          status: VerificationStatus;
          approved_by: string | null;
          created_at: string;
          expires_at: string;
        };
        Insert: {
          id?: string;
          vip_id: string;
          code: string;
          status?: VerificationStatus;
          approved_by?: string | null;
          created_at?: string;
          expires_at?: string;
        };
        Update: {
          id?: string;
          vip_id?: string;
          code?: string;
          status?: VerificationStatus;
          approved_by?: string | null;
          created_at?: string;
          expires_at?: string;
        };
      };
      categories: {
        Row: {
          id: string;
          name: string;
          slug: string;
          description: string | null;
          image_url: string | null;
          sort_order: number;
          is_active: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          slug: string;
          description?: string | null;
          image_url?: string | null;
          sort_order?: number;
          is_active?: boolean;
          created_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          slug?: string;
          description?: string | null;
          image_url?: string | null;
          sort_order?: number;
          is_active?: boolean;
          created_at?: string;
        };
      };
      products: {
        Row: {
          id: string;
          name: string;
          description: string | null;
          category_id: string | null;
          tier_required: VipTier;
          images: string[];
          is_active: boolean;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          description?: string | null;
          category_id?: string | null;
          tier_required?: VipTier;
          images?: string[];
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          description?: string | null;
          category_id?: string | null;
          tier_required?: VipTier;
          images?: string[];
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
      };
      inventory: {
        Row: {
          id: string;
          product_id: string;
          size: string;
          quantity: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          product_id: string;
          size: string;
          quantity?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          product_id?: string;
          size?: string;
          quantity?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      orders: {
        Row: {
          id: string;
          vip_id: string;
          status: OrderStatus;
          shipping_address: Json;
          tracking_number: string | null;
          carrier: string | null;
          notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          vip_id: string;
          status?: OrderStatus;
          shipping_address: Json;
          tracking_number?: string | null;
          carrier?: string | null;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          vip_id?: string;
          status?: OrderStatus;
          shipping_address?: Json;
          tracking_number?: string | null;
          carrier?: string | null;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      order_items: {
        Row: {
          id: string;
          order_id: string;
          product_id: string;
          size: string;
          quantity: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          order_id: string;
          product_id: string;
          size: string;
          quantity?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          order_id?: string;
          product_id?: string;
          size?: string;
          quantity?: number;
          created_at?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      vip_tier: VipTier;
      registration_type: RegistrationType;
      order_status: OrderStatus;
      verification_status: VerificationStatus;
    };
  };
}
