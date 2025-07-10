export const validateSearchInput = (input: string): string | null => {
  if (!input.trim()) {
    return "Search query cannot be empty";
  }

  // To prevent the backend from freezing up, we limit the search query to 100 characters.
  if (input.length > 100) {
    return "Search query cannot be longer than 100 characters";
  }

  // First remove all spaces
  const trimmedInput = input.replace(/\s+/g, '');
  
  // Check if query contains only numbers
  if (/^\d+$/.test(trimmedInput)) {
    return "Query cannot contain only numbers";
  }

  // Check if query contains only symbols (no letters or numbers)
  if (trimmedInput && !/[a-zA-Z0-9]/.test(trimmedInput)) {
    return "Query cannot contain only symbols";
  }

  // Check for harmful content
  const harmfulWords = [
    "gun", "bomb", "kill", "murder", "shoot", "attack", "weapon", "explosive",
    "bullet", "acid", "sniper", "grenade", "terror", "assault", "execute",
    "behead", "poison", "cyanide", "sarin", "anthrax", "suicide bomber",
    "arson", "sabotage", "molotov", "lynch", "genocide", "riot", "vandalism",
    "rape", "slaughter", "firearm", "extremist", "burn down", "hate crime",
    "abuse", "threaten"
  ];

  if (harmfulWords.some(word => input.toLowerCase().includes(word))) {
    return "Query contains inappropriate words";
  }

  // Check for invalid characters
  if (/[<>{}[\]\\]/.test(input)) {
    return "Query contains invalid characters";
  }

  return null;
}; 