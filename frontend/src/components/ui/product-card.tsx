import React from "react";
import { Product } from "@/types/product";
import { ProductCarousel } from "./product-carousel";
import { AIInsight } from "./ai-insight";

interface ProductCardProps {
  product: Product;
  children?: React.ReactNode;
}

export function ProductCard({ product, children }: ProductCardProps) {
  return (
    <div className="flex-none w-80 bg-white rounded-lg shadow-md overflow-hidden flex flex-col">
      <ProductCarousel images={product.images} />
      <div className="p-4 flex flex-col flex-1">
        <h3 className="text-lg font-semibold mb-2">{product.title}</h3>
        {children}
        {product.reason && <AIInsight reason={product.reason} />}
        <div className="mt-auto text-xl font-bold text-blue-600">
          {product.price ? (
            `$${product.price.toFixed(2)}`
          ) : (
            <span className="underline">Get Restock Notification</span>
          )}
        </div>
      </div>
    </div>
  );
} 