"use client";

import React from "react";

interface FilterOptionsProps {
  gender: string;
  setGender: (value: string) => void;
  ageRange: string;
  setAgeRange: (value: string) => void;
  colorStyle: string;
  setColorStyle: (value: string) => void;
}

const FilterOptions = ({ gender, setGender, ageRange, setAgeRange, colorStyle, setColorStyle }: FilterOptionsProps) => {
  return (
    <div className="flex gap-4 justify-center mb-6">
      <div className="flex items-center gap-2">
        <label className="text-gray-700 font-medium">Gender:</label>
        <select 
          value={gender} 
          onChange={(e) => setGender(e.target.value)}
          className="px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-pink-300 focus:ring-2 focus:ring-pink-200"
        >
          <option value="all">All</option>
          <option value="men">Men</option>
          <option value="women">Women</option>
          <option value="unisex">Unisex</option>
        </select>
      </div>
      
      <div className="flex items-center gap-2">
        <label className="text-gray-700 font-medium">Age Range:</label>
        <select 
          value={ageRange} 
          onChange={(e) => setAgeRange(e.target.value)}
          className="px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-pink-300 focus:ring-2 focus:ring-pink-200"
        >
          <option value="all">All Ages</option>
          <option value="kids">Kids (0-12)</option>
          <option value="teens">Teens (13-19)</option>
          <option value="young-adults">Young Adults (20-29)</option>
          <option value="adults">Adults (30-49)</option>
          <option value="seniors">Seniors (50+)</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-gray-700 font-medium">Color Style:</label>
        <select 
          value={colorStyle} 
          onChange={(e) => setColorStyle(e.target.value)}
          className="px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-pink-300 focus:ring-2 focus:ring-pink-200"
        >
          <option value="all">All colors</option>
          <option value="neutral">Neutral colors</option>
          <option value="warm">Warm colors</option>
          <option value="cool">Cool colors</option>
          <option value="Pastels&Bright">Pastels & Brights</option>
        </select>
      </div>

    </div>
  );
};

export default FilterOptions; 