import React from 'react';

const ProductGrid = ({ products, loading, onViewDetails }) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
        <div style={{ animation: 'pulse 1.5s infinite', fontSize: '1.25rem' }}>
          Searching premium catalog...
        </div>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <h3>No Products Found</h3>
        <p style={{ color: 'var(--text-muted)' }}>Try adjusting your filters or chat again with the AI assistant.</p>
      </div>
    );
  }

  return (
    <div className="products-grid">
      {products.map((product) => (
        <div key={product.id} className="product-card glass-panel">
          {product.advantageTag && (
            <div className="product-tag">{product.advantageTag}</div>
          )}
          
          <div className="product-image-container">
            <img 
              src={product.image} 
              alt={product.name} 
              className="product-image" 
              onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=800'; }}
            />
          </div>
          
          <div className="product-details">
            <h3 className="product-title">{product.name}</h3>
            <div className="product-price">{product.price}</div>
            
            <p className="product-reason">{product.aiReason}</p>
            
            <button 
              className="btn-primary" 
              style={{ width: '100%', marginTop: 'auto' }}
              onClick={() => onViewDetails(product)}
            >
              Discover More
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProductGrid;
