import React from 'react';
import { X, Check } from 'lucide-react';

const ProductModal = ({ product, onClose }) => {
  if (!product) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>

        <img 
          src={product.image} 
          alt={product.name} 
          className="modal-image" 
          onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=800'; }}
        />

        <div className="modal-details">
          <div>
            <span className="badge">{product.category}</span>
            {product.advantageTag && (
              <span className="badge" style={{ background: 'rgba(236, 72, 153, 0.2)', color: 'var(--secondary)' }}>
                {product.advantageTag}
              </span>
            )}
          </div>
          
          <h2 style={{ fontSize: '2rem', margin: '1rem 0 0.5rem', color: 'var(--text-main)' }}>
            {product.name}
          </h2>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
            {product.price}
          </div>

          <div className="pitch-box">
            <p style={{ margin: 0, fontSize: '1.1rem', fontStyle: 'italic', fontWeight: '500' }}>
              " {product.persuasivePitch || product.aiReason} "
            </p>
          </div>

          <div style={{ flex: 1 }}>
            <h4 style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>AI Insights & Advantages</h4>
            <p style={{ lineHeight: '1.6', color: '#e2e8f0' }}>{product.description}</p>
            
            {product.advantages && product.advantages.length > 0 && (
              <ul className="advantages-list">
                {product.advantages.map((adv, i) => (
                  <li key={i}>{adv}</li>
                ))}
              </ul>
            )}
          </div>

          <button className="btn-primary" style={{ width: '100%', padding: '1rem', fontSize: '1.1rem', marginTop: 'auto' }}>
            Add to Cart Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;
