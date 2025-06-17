export interface Product {
  id: string;
  title: string;
  price: number;
  currency: string;
  images: Record<string, string | ImageVariant>;
  average_rating?: number;
  rating_number?: number;
  reason?: string;
  details?: Record<string, string | number | boolean>;
}

interface ImageVariant {
  large?: string;
  thumb?: string;
  hi_res?: string;
  variant?: string;
}
