"use client";

import React, { useState, useEffect, useCallback } from "react";
import { debounce } from "lodash";

interface SearchFormProps {
  prompt: string;
  setPrompt: (value: string) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  isLoading?: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ prompt, setPrompt, handleSubmit, isLoading = false }) => {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validate input
  const validateInput = (input: string): string | null => {
    if (!input.trim()) {
      return "Search query cannot be empty";
    }
    if (input.length < 2) {
      return "Search query must be at least 2 characters long";
    }
    if (input.length > 100) {
      return "Search query must be less than 100 characters";
    }
    // Check for potentially harmful content
    const harmfulPatterns = [
      /<script>/i,
      /javascript:/i,
      /on\w+=/i,
      /eval\(/i,
      /document\./i,
      /window\./i,
      /\b(gun|bomb|kill|murder|shoot|attack|weapon|explosive|bullet|acid|sniper|grenade|terror|assault|execute|behead|poison|cyanide|sarin|anthrax|suicide\s*bomber|arson|sabotage|molotov|lynch|genocide|riot|vandalism|rape|slaughter|firearm|extremist|burn\s*down|hate\s*crime|abuse|threaten)\b/i
    ];
    if (harmfulPatterns.some((pattern) => pattern.test(input))) {
      return "Search query contains potentially harmful content";
    }
    return null;
  };

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((searchQuery: string) => {
      if (isSubmitting) {
        const validationError = validateInput(searchQuery);
        if (validationError) {
          setError(validationError);
          return;
        }
        setError(null);
      }
    }, 500),
    [isSubmitting]
  );

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setPrompt(newQuery);
    if (isSubmitting) {
      const validationError = validateInput(newQuery);
      setError(validationError);
    }
    debouncedSearch(newQuery);
  };

  // Handle form submission
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    const validationError = validateInput(prompt);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    await handleSubmit(e);
  };

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

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
};

export default SearchForm; 