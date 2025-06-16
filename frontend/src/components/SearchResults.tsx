"use client";

import React from "react";
import { Product } from '../types/product';

interface SearchResultsProps {
  products: Product[];
  isLoading: boolean;
  title: string;
}

// Generate unique keys for skeleton items
const generateSkeletonKeys = () => {
  return Array.from({ length: 5 }, (_, i) => `skeleton-${i}`);
};

export default function SearchResults({ products, isLoading, title }: SearchResultsProps) {
  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex overflow-x-auto pb-4 gap-6">
          {generateSkeletonKeys().map((key) => (
            <div key={key} className="flex-none w-[300px] bg-white rounded-lg shadow-md p-4 animate-pulse">
              <div className="bg-gray-200 h-48 rounded-md mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      );
    }

    if (products.length === 0) {
      return (
        <div className="text-center text-gray-500 mt-8">
          No products found. Try adjusting your search criteria.
        </div>
      );
    }

    return (
      <div className="flex overflow-x-auto pb-4 gap-6">
        {products.map((product, index) => {
          console.log('Product images:', product.images);
          return (
            <div
              key={`${product.id}-${index}`}
              className="flex-none w-[300px] bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col"
            >
              <img
                src={Array.isArray(product.images) ? product.images[0]?.large : product.images?.large}
                alt={product.title}
                className="w-full h-72 object-contain bg-white"
                onError={(e) => {
                  console.error('Image failed to load:', e);
                  const target = e.target as HTMLImageElement;
                  target.src = 'https://m.media-amazon.com/images/I/71oiNsFPI3L._AC_UL1500_.jpg';
                }}
              />
              <div className="p-4 flex flex-col flex-1">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{product.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{product.reason}</p>

                <div className="mt-auto">
                  <p className="text-lg font-bold text-blue-600 truncate max-w-[200px]">
                    {product.price ? `$${product.price.toFixed(2)}` : <span className="underline">Restock Notification</span>}
                  </p>
                  {product.inventory_status === 'out_of_stock' && (
                    <span className="text-sm text-red-500 font-medium">Out of Stock</span>
                  )}
                  
                </div>
              </div>
            </div>
            
          );
        })}
      </div>

    );
  };

  return (
    <div className="p-8">
      <h2 className="text-3xl font-semibold text-gray-800 mb-6">{title}</h2>
      {renderContent()}
    </div>
  );
} 