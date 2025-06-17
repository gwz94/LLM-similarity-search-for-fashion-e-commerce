"use client";

import React, { useState } from "react";
import { validateSearchInput } from "../utils/validation";

interface SearchFormProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  isLoading: boolean;
}

export default function SearchForm({
  prompt,
  setPrompt,
  handleSubmit,
  isLoading,
}: SearchFormProps) {
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPrompt(value);
    // Remove validation from input change
    setError(null); // Clear any previous errors
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validateSearchInput(prompt);
    if (validationError) {
      setError(validationError);
      return;
    }
    await handleSubmit(e);
  };

  return (
    <form onSubmit={onSubmit} className="w-full max-w-4xl mx-auto">
      <div className="relative">
        <input
          type="text"
          value={prompt}
          onChange={handleInputChange}
          placeholder="Key in your next fashion inspiration..."
          className={`w-full px-6 py-4 text-lg text-gray-700 bg-white border rounded-full focus:outline-none focus:border-blue-500 ${
            error ? "border-red-500" : "border-gray-300"
          }`}
        />
        <button
          type="submit"
          disabled={isLoading}
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 px-6 py-2 text-l font-medium text-white rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            isLoading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'animate-gradient bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 hover:from-pink-600 hover:via-purple-600 hover:to-blue-600 bg-[length:200%_auto]'
          }`}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </form>
  );
}
