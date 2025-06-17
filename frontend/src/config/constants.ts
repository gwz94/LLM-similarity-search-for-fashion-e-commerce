type FilterValue = "all" | string;

export const SEARCH_CONFIG = {
  TOP_K: 5,
  DEFAULT_FILTERS: {
    gender: "all" as FilterValue,
    ageRange: "all" as FilterValue,
    colorStyle: "all" as FilterValue
  }
} as const;

export const API_CONFIG = {
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  }
} as const; 