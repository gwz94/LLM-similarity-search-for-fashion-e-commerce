"use client";

import React from "react";
import { Product } from "@/types/product";
import { ProductCard } from "./ui/product-card";
import { RatingStars } from "./ui/rating-stars";

interface SearchResultsProps {
  products: Product[];
  isLoading: boolean;
  title: string;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  products,
  isLoading,
  title,
}) => {
  if (isLoading) {
    return <SearchResultsSkeleton />;
  }

  if (products.length === 0) {
    return <NoResultsFound />;
  }

  return (
    <div className="p-8">
      <h2 className="text-3xl font-semibold text-gray-800 mb-6">{title}</h2>
      <div className="flex overflow-x-auto pb-4 gap-6">
        {products.map((product, index) => (
          <ProductCard key={`${product.id}-${index}`} product={product}>
            {product.average_rating && (
              <div className="mb-3">
                <RatingStars 
                  rating={product.average_rating} 
                  numRatings={product.rating_number}
                />
              </div>
            )}
          </ProductCard>
        ))}
      </div>
    </div>
  );
};

const SearchResultsSkeleton: React.FC = () => {
  return (
    <div className="flex overflow-x-auto pb-4 gap-6" data-testid="skeleton">
      {[...Array(3)].map((_, index) => (
        <div
          key={index}
          className="flex-none w-[300px] bg-white rounded-lg shadow-md overflow-hidden"
        >
          <div className="h-48 bg-gray-200 animate-pulse" />
          <div className="p-4 space-y-3">
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
          </div>
        </div>
      ))}
    </div>
  );
};

const NoResultsFound: React.FC = () => {
  return (
    <div className="text-center py-8">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        No products found
      </h3>
      <p className="text-gray-500">
        Try adjusting your search criteria or filters
      </p>
    </div>
  );
};

export default SearchResults;
