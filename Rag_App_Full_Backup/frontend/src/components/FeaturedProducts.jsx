import React from 'react';
import { Star } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/images';

const FEATURED = [
  { id: 1, name: "ASUS Vivobook", price: "$499.00", image: `${API_BASE}/41Ucsh-mw%2BL._SL500_.jpg`, tag: "Elite Computing" },
  { id: 2, name: "Premium Speaker", price: "$299.00", image: `${API_BASE}/download%20(1).jpg`, tag: "Best Seller" },
  { id: 3, name: "Smart Device", price: "$450.00", image: `${API_BASE}/download%20(2).jpg`, tag: "Pro Choice" },
  { id: 4, name: "Industrial Tech", price: "$320.00", image: `${API_BASE}/download%20(3).jpg`, tag: "Exclusive" },
  { id: 5, name: "Modern Gear", price: "$149.00", image: `${API_BASE}/download%20(4).jpg`, tag: "Newest" },
  { id: 6, name: "Sleek Gadget", price: "$199.95", image: `${API_BASE}/images%20(3).jpg`, tag: "Minimalist" }
];

const FeaturedProducts = () => {
  return (
    <div className="featured-section">
      <div className="section-header">
        <h2>🔥 Trending Now</h2>
        <p>Hand-picked premium selections for our elite members.</p>
      </div>

      <div className="featured-grid">
        {FEATURED.map((item) => (
          <div key={item.id} className="featured-card glass-panel">
            <div className="featured-image-container">
              <img src={item.image} alt={item.name} />
              <div className="featured-tag">{item.tag}</div>
            </div>
            <div className="featured-info">
              <div className="rating">
                {[...Array(5)].map((_, i) => <Star key={i} size={12} fill="#fbbf24" color="#fbbf24" />)}
              </div>
              <h4>{item.name}</h4>
              <div className="featured-price">{item.price}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeaturedProducts;
