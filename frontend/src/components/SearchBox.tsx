"use client";

import React, { useState, useEffect } from "react";
import FilterOptions from "./FilterOptions";
import SearchForm from "./SearchForm";
import SearchResults from "./SearchResults";
import { searchProducts } from '../services/api';
import { Product } from '../types/product';

// Initial state for products
const initialProducts: Product[] = [];

export default function SearchBox() {
  const [isClient, setIsClient] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [gender, setGender] = useState("all");
  const [ageRange, setAgeRange] = useState("all");
  const [colorStyle, setColorStyle] = useState("all");
  const [inStockProducts, setInStockProducts] = useState<Product[]>([]);
  const [outOfStockProducts, setOutOfStockProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedGender, setSelectedGender] = useState<string>("all");
  const [selectedAgeRange, setSelectedAgeRange] = useState<string>("all");
  const [selectedColorStyle, setSelectedColorStyle] = useState<string>("all");

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Starting search with query:', query);
      
      const combinedQuery = `${selectedGender !== "all" ? `, preference: gender:${selectedGender}` : ""}${selectedAgeRange !== "all" ? `, age:${selectedAgeRange}` : ""}${selectedColorStyle !== "all" ? `, color:${selectedColorStyle}` : ""}${query}`;
      
      console.log('Making request to backend...');
      const response = await fetch(`http://localhost:8000/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: combinedQuery,
          top_k: 5,
          gender: selectedGender,
          ageRange: selectedAgeRange,
          colorStyle: selectedColorStyle
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

  if (!isClient) {
    return (
      <div className="flex flex-col h-[calc(100vh+200px)] mx-[10%] my-[5%] w-[80%] bg-gradient-to-b from-white to-gray-50 rounded-2xl shadow-xl animate-pulse">
        <div className="p-8 space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col ${(inStockProducts.length > 0 || outOfStockProducts.length > 0) ? 'h-[calc(100vh-4rem)]' : 'h-auto'} w-full max-w-7xl mx-auto bg-gradient-to-b from-white to-gray-50 rounded-2xl shadow-xl`}>
      <div className="p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">Discover Your Style</h1>
        
        <FilterOptions 
          gender={gender}
          setGender={(value) => {
            setGender(value);
            setSelectedGender(value);
          }}
          ageRange={ageRange}
          setAgeRange={(value) => {
            setAgeRange(value);
            setSelectedAgeRange(value);
          }}
          colorStyle={colorStyle}
          setColorStyle={(value) => {
            setColorStyle(value);
            setSelectedColorStyle(value);
          }}
        />

        <SearchForm 
          prompt={prompt}
          setPrompt={setPrompt}
          handleSubmit={handleSubmit}
          isLoading={loading}
        />

        {error && (
          <div className="text-red-500 text-center mt-4">
            {error}
          </div>
        )}
      </div>
        {(inStockProducts.length > 0 || outOfStockProducts.length > 0) && ( 
        <div className="flex-1 overflow-y-auto">
          <SearchResults 
            products={inStockProducts} 
            isLoading={loading} 
            title="Recommended Items"
          />
          <SearchResults 
            products={outOfStockProducts} 
            isLoading={loading} 
            title="Recommended but Out of Stock"
          />
          </div>
        )}
    </div>
  );
}

