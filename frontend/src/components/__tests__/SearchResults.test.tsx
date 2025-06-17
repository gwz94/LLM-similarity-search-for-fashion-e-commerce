import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchResults from '../SearchResults';
import { Product } from '@/types/product';

// Mock the ProductCard component since we don't need to test its internals
jest.mock('../ui/product-card', () => ({
  ProductCard: ({ product }: { product: Product }) => (
    <div data-testid="product-card">{product.title}</div>
  ),
}));

describe('SearchResults', () => {
  const mockProducts: Product[] = [
    {
      id: "1",
      title: 'Test Product 1',
      price: 99.99,
      currency: 'USD',
      images: { main: 'image1.jpg' },
      average_rating: 4.5,
      rating_number: 100,
      reason: 'Test reason 1',
      details: { color: 'red' }
    },
    {
      id: "2",
      title: 'Test Product 2',
      price: 149.99,
      currency: 'USD',
      images: { main: 'image2.jpg' },
      average_rating: 4.0,
      rating_number: 50,
      reason: 'Test reason 2',
      details: { color: 'blue' }
    },
  ];

  it('renders loading skeleton when isLoading is true', () => {
    render(<SearchResults products={[]} isLoading={true} title="Test Title" />);
    expect(screen.getByTestId('skeleton')).toBeInTheDocument();
  });

  it('renders no results message when products array is empty', () => {
    render(<SearchResults products={[]} isLoading={false} title="Test Title" />);
    expect(screen.getByText('No products found')).toBeInTheDocument();
  });

  it('renders products when data is available', () => {
    render(<SearchResults products={mockProducts} isLoading={false} title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getAllByTestId('product-card')).toHaveLength(2);
  });
}); 