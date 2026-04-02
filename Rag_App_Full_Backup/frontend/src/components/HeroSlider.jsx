import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Zap } from 'lucide-react';

const SLIDES = [
  {
    id: 1,
    title: "Next-Gen Tech Essentials",
    subtitle: "Precision engineered for the modern professional.",
    image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&q=80&w=1600",
    color: "#4F46E5"
  },
  {
    id: 2,
    title: "Elite Fitness Gear",
    subtitle: "Push your limits with elite-level training equipment.",
    image: "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?auto=format&fit=crop&q=80&w=1600",
    color: "#ec4899"
  },
  {
    id: 3,
    title: "Artisanal Kitchenware",
    subtitle: "Elevate your culinary experience with precision tools.",
    image: "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&q=80&w=1600",
    color: "#10b981"
  }
];

const HeroSlider = () => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (!SLIDES || SLIDES.length === 0) return;
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  if (!SLIDES || SLIDES.length === 0) return null;

  return (
    <div className="hero-slider glass-panel">
      {SLIDES.map((slide, index) => (
        <div 
          key={slide.id}
          className={`slide ${index === current ? 'active' : ''}`}
          style={{ backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.6)), url(${slide.image})` }}
        >
          <div className="slide-content">
            <div className="badge" style={{ background: slide.color }}>
              <Zap size={14} fill="white" /> New Arrivals
            </div>
            <h1>{slide.title}</h1>
            <p>{slide.subtitle}</p>
            <button className="btn-primary" style={{ marginTop: '1rem' }}>
              Explore Collection
            </button>
          </div>
        </div>
      ))}
      
      <div className="slider-controls">
        <button onClick={() => setCurrent((prev) => (prev - 1 + SLIDES.length) % SLIDES.length)}>
          <ChevronLeft size={20} />
        </button>
        <button onClick={() => setCurrent((prev) => (prev + 1) % SLIDES.length)}>
          <ChevronRight size={20} />
        </button>
      </div>

      <div className="slider-dots">
        {SLIDES.map((_, i) => (
          <div 
            key={i} 
            className={`dot ${i === current ? 'active' : ''}`}
            onClick={() => setCurrent(i)}
          />
        ))}
      </div>
    </div>
  );
};

export default HeroSlider;
