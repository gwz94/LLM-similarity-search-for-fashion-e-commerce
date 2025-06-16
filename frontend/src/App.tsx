import React from 'react';
import SearchForm from './components/SearchForm';
import './App.css';

function App() {
  const handleSearch = (query: string) => {
    console.log('Searching for:', query);
    // Add your search logic here
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Product Search</h1>
        <SearchForm onSearch={handleSearch} />
      </div>
    </div>
  );
}

export default App; 