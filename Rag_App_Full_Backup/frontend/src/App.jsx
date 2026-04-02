import React, { useState, useMemo } from 'react';
import Header from './components/Header';
import HeroSlider from './components/HeroSlider';
import FeaturedProducts from './components/FeaturedProducts';
import ChatNegotiator from './components/ChatNegotiator';
import SidebarFilters from './components/SidebarFilters';
import ProductGrid from './components/ProductGrid';
import ProductModal from './components/ProductModal';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // App UI State: 'chat' | 'results'
  const [appState, setAppState] = useState('chat');
  
  // Filters
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedPrice, setSelectedPrice] = useState('Any');

  const handleSearchComplete = async (query) => {
    setAppState('results');
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        setProducts(data.results);
      } else {
        setProducts([]);
      }
    } catch (error) {
      console.error("Error fetching AI recommendations:", error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  // Derive categories dynamically from search results
  const categories = useMemo(() => {
    const rawCategories = products.map(p => p.category).filter(Boolean);
    return [...new Set(rawCategories)];
  }, [products]);

  // Apply quick frontend filters
  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      // Category filter
      if (selectedCategory !== 'All' && p.category !== selectedCategory) return false;
      
      // Price filter implementation (extract numbers roughly)
      if (selectedPrice !== 'Any') {
        const pStr = String(p.price).replace(/[^0-9.]/g, '');
        const priceNum = parseFloat(pStr);
        if (!isNaN(priceNum)) {
          if (selectedPrice === '<50' && priceNum >= 50) return false;
          if (selectedPrice === '50-200' && (priceNum < 50 || priceNum > 200)) return false;
          if (selectedPrice === '>200' && priceNum <= 200) return false;
        }
      }
      return true;
    });
  }, [products, selectedCategory, selectedPrice]);

  return (
    <div className="app-container">
      <Header setChatMode={() => setAppState('chat')} />
      
      <main className="main-content">
        {appState === 'chat' ? (
          <>
            <HeroSlider />
            <FeaturedProducts />
            <ChatNegotiator onSearchComplete={handleSearchComplete} />
          </>
        ) : (
          <div className="layout-grid">
            <SidebarFilters 
              categories={categories}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              selectedPrice={selectedPrice}
              setSelectedPrice={setSelectedPrice}
            />
            
            <section className="products-section">
              <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Your Personalized Recommendations</h2>
                <span style={{ color: 'var(--text-muted)' }}>{filteredProducts.length} Results</span>
              </div>
              
              <ProductGrid 
                products={filteredProducts} 
                loading={loading} 
                onViewDetails={setSelectedProduct} 
              />
            </section>
          </div>
        )}
      </main>

      {selectedProduct && (
        <ProductModal 
          product={selectedProduct} 
          onClose={() => setSelectedProduct(null)} 
        />
      )}
    </div>
  );
}

export default App;
