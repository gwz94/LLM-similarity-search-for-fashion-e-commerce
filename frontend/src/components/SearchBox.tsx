"use client";

import React, { useState } from "react";
import FilterOptions from "./FilterOptions";
import SearchForm from "./SearchForm";
import SearchResults from "./SearchResults";
import { Product } from '../types/product';
import API_ENDPOINTS from '../config/endpoints';
import { buildSearchQuery } from '../utils/queryBuilder';
import { SEARCH_CONFIG, API_CONFIG } from '../config/constants';
import { Skeleton } from "@/components/ui/skeleton";

export default function SearchBox() {
  const [prompt, setPrompt] = useState("");
  const [gender, setGender] = useState(SEARCH_CONFIG.DEFAULT_FILTERS.gender);
  const [ageRange, setAgeRange] = useState(SEARCH_CONFIG.DEFAULT_FILTERS.ageRange);
  const [colorStyle, setColorStyle] = useState(SEARCH_CONFIG.DEFAULT_FILTERS.colorStyle);
  const [inStockProducts, setInStockProducts] = useState<Product[]>([]);
  const [outOfStockProducts, setOutOfStockProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Starting search with query:', query);

      const combinedQuery = buildSearchQuery(query, {
        gender,
        ageRange,
        colorStyle
      });

      console.log('Making request to backend...');
      const response = await fetch(API_ENDPOINTS.SEARCH, {
        method: 'POST',
        headers: API_CONFIG.DEFAULT_HEADERS,
        body: JSON.stringify({
          query: combinedQuery,
          top_k: SEARCH_CONFIG.TOP_K,
        }),
      });

      console.log('Got response:', response.status);
      const data = await response.json();
      console.log('Parsed response data:', data);

      setInStockProducts(data.recommended_in_stock_products);
      setOutOfStockProducts(data.recommended_out_of_stock_products);
    } catch (err) {
      console.error('Search failed:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setInStockProducts([]);
      setOutOfStockProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleSearch(prompt);
  };

  return (
    <div
      className={`flex flex-col ${
        ((inStockProducts?.length || 0) > 0 || (outOfStockProducts?.length || 0) > 0)
          ? "h-[calc(100vh-4rem)]"
          : "h-auto"
      } w-full max-w-7xl mx-auto bg-gradient-to-b from-white to-gray-50 rounded-2xl shadow-xl`}
    >
      <div className="p-8 space-y-6">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          Discover Your Style
        </h1>

        <FilterOptions
          gender={gender}
          setGender={setGender}
          ageRange={ageRange}
          setAgeRange={setAgeRange}
          colorStyle={colorStyle}
          setColorStyle={setColorStyle}
        />

        <SearchForm
          prompt={prompt}
          setPrompt={setPrompt}
          handleSubmit={handleSubmit}
          isLoading={loading}
        />

        {error && <div className="text-red-500 text-center mt-4">{error}</div>}
      </div>
      {loading ? (
        <div className="p-8 space-y-6">
          <Skeleton className="h-8 w-1/3 mx-auto" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      ) : ((inStockProducts?.length || 0) > 0 || (outOfStockProducts?.length || 0) > 0) && (
        <div className="flex-1 overflow-y-auto">
          <SearchResults
            products={inStockProducts || []}
            isLoading={loading}
            title="Recommended Items"
          />
          <SearchResults
            products={outOfStockProducts || []}
            isLoading={loading}
            title="Recommended but Out of Stock"
          />
        </div>
      )}
    </div>
  );
}

