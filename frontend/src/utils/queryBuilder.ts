interface FilterOptions {
  gender: string;
  ageRange: string;
  colorStyle: string;
}

export const buildSearchQuery = (query: string, filters: FilterOptions): string => {
  const filterParts = [];

  if (filters.gender !== "all") {
    filterParts.push(`preference: gender:${filters.gender}`);
  }
  if (filters.ageRange !== "all") {
    filterParts.push(`age:${filters.ageRange}`);
  }
  if (filters.colorStyle !== "all") {
    filterParts.push(`color:${filters.colorStyle}`);
  }

  const filterString = filterParts.length > 0 ? `, ${filterParts.join(", ")}` : "";
  return `${filterString}${query}`;
}; 