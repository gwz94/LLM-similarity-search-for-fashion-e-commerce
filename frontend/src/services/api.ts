import { Product } from '../types/product';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface SearchParams {
  prompt: string;
  gender: string;
  ageRange: string;
  colorStyle: string;
}

interface SearchResponse {
  status: string;
  recommended_products: Product[];
}

export const searchProducts = async (params: SearchParams): Promise<Product[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: params.prompt,
        top_k: 5,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: SearchResponse = await response.json();
    return data.recommended_products;
  } catch (error) {
    console.error('Error searching products:', error);
    throw error;
  }
};

// Health check function
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}; 