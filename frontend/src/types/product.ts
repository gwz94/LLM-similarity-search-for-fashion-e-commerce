export interface Product {
  id: number;
  title: string;
  average_rating: number | null;
  rating_number: number | null;
  features: string[];
  description: string;
  price: number | null;
  images: Record<string, string>;
  store: string;
  categories: string[];
  details: Record<string, any>;
  similarity: number;
  inventory_status: "in_stock" | "out_of_stock";
  reason?: string;
} 