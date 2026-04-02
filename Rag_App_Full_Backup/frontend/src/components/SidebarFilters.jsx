import React from 'react';

const SidebarFilters = ({ categories, selectedCategory, setSelectedCategory, selectedPrice, setSelectedPrice }) => {
  return (
    <aside className="glass-panel" style={{ padding: '1.5rem', height: 'fit-content' }}>
      <div className="sidebar-section">
        <h3>Categories</h3>
        <button 
          className={`filter-btn ${selectedCategory === 'All' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('All')}
        >
          All Products
        </button>
        {categories.map(cat => (
          <button 
            key={cat}
            className={`filter-btn ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="sidebar-section">
        <h3>Price Range</h3>
        {[
          { label: 'Any Price', val: 'Any' },
          { label: 'Under $50', val: '<50' },
          { label: '$50 to $200', val: '50-200' },
          { label: 'Over $200', val: '>200' }
        ].map(range => (
          <button 
            key={range.val}
            className={`filter-btn ${selectedPrice === range.val ? 'active' : ''}`}
            onClick={() => setSelectedPrice(range.val)}
          >
            {range.label}
          </button>
        ))}
      </div>
    </aside>
  );
};

export default SidebarFilters;
