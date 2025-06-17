"use client";

import React from "react";

interface FilterOption {
  value: string;
  label: string;
}

interface FilterSelectProps {
  label: string;
  value: string;
  options: readonly FilterOption[];
  onChange: (value: string) => void;
}

const FilterSelect: React.FC<FilterSelectProps> = ({
  label,
  value,
  options,
  onChange,
}) => (
  <div className="flex items-center gap-2">
    <label className="text-gray-700 font-medium">{label}:</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-pink-300 focus:ring-2 focus:ring-pink-200"
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </div>
);

const FILTER_OPTIONS = {
  gender: [
    { value: "all", label: "All" },
    { value: "men", label: "Men" },
    { value: "women", label: "Women" },
    { value: "unisex", label: "Unisex" },
  ],
  ageRange: [
    { value: "all", label: "All Ages" },
    { value: "kids", label: "Kids (0-12)" },
    { value: "teens", label: "Teens (13-19)" },
    { value: "young-adults", label: "Young Adults (20-29)" },
    { value: "adults", label: "Adults (30-49)" },
    { value: "seniors", label: "Seniors (50+)" },
  ],
  colorStyle: [
    { value: "all", label: "All colors" },
    { value: "neutral", label: "Neutral colors" },
    { value: "warm", label: "Warm colors" },
    { value: "cool", label: "Cool colors" },
    { value: "Pastels&Bright", label: "Pastels & Brights" },
  ],
} as const;

interface FilterOptionsProps {
  gender: string;
  setGender: (value: string) => void;
  ageRange: string;
  setAgeRange: (value: string) => void;
  colorStyle: string;
  setColorStyle: (value: string) => void;
}

const FilterOptions: React.FC<FilterOptionsProps> = ({
  gender,
  setGender,
  ageRange,
  setAgeRange,
  colorStyle,
  setColorStyle,
}) => {
  return (
    <div className="flex flex-wrap gap-4 justify-center mb-6">
      <FilterSelect
        label="Gender"
        value={gender}
        options={FILTER_OPTIONS.gender}
        onChange={setGender}
      />
      <FilterSelect
        label="Age Range"
        value={ageRange}
        options={FILTER_OPTIONS.ageRange}
        onChange={setAgeRange}
      />
      <FilterSelect
        label="Color Style"
        value={colorStyle}
        options={FILTER_OPTIONS.colorStyle}
        onChange={setColorStyle}
      />
    </div>
  );
};

export default FilterOptions;
