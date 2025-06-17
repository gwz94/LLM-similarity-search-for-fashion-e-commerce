const getBaseUrl = (): string => {
  
  // Use env var first (works both server and client side)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  console.log("API_URL", process.env.NEXT_PUBLIC_API_URL);


  if (typeof window !== 'undefined') {
    // Ensure we're returning a clean URL without any encoding issues
    return `${window.location.protocol}//${window.location.hostname}:8001`;
  }

  return 'http://localhost:8001';
};

export default getBaseUrl;
  