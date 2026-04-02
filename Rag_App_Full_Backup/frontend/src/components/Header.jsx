import React from 'react';
import { ShoppingBag, Search } from 'lucide-react';

const Header = ({ setChatMode }) => {
  return (
    <header className="header">
      <div className="logo-text" onClick={() => setChatMode(true)} style={{ cursor: 'pointer' }}>
        <ShoppingBag size={28} />
        AuraStore AI
      </div>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button className="btn-icon" onClick={() => setChatMode(true)}>
          <Search size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
