import { createClient } from "@/lib/supabase/server";

export interface OrderItem {
  product_id: string;
  size: string;
  quantity: number;
}

export interface ShippingAddress {
  recipient_name: string;
  phone: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface CreateOrderInput {
  items: OrderItem[];
  shipping_address: ShippingAddress;
  notes?: string;
}

export interface Order {
  id: string;
  status: string;
  created_at: string;
  items: OrderItem[];
  shipping_address: ShippingAddress;
}

export async function createOrder(input: CreateOrderInput): Promise<Order> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("orders")
    .insert({
      items: input.items,
      shipping_address: input.shipping_address,
      notes: input.notes,
      status: "pending",
    })
    .select()
    .single();

  if (error) {
    console.error("Error creating order:", error);
    throw new Error(error.message);
  }

  return data;
}

export async function getOrders(): Promise<Order[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("orders")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching orders:", error);
    return [];
  }

  return data;
}
