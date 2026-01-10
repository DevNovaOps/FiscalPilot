/**
 * Fiscal Pilot - Dynamic UI Animations
 * Scroll reveal, dynamic effects, and interactive animations
 */

(function() {
    'use strict';
    
    // Scroll Reveal Animation
    function initScrollReveal() {
        const elements = document.querySelectorAll('.scroll-reveal');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        elements.forEach(el => observer.observe(el));
    }
    
    // Animate numbers
    function animateNumber(element, target, duration = 2000) {
        const start = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
        const increment = (target - start) / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = formatCurrency(current);
        }, 16);
    }
    
    // Format currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    // Add hover effects to cards
    function initCardEffects() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }
    
    // Parallax effect for hero section
    function initParallax() {
        const hero = document.querySelector('.hero-section');
        if (!hero) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            hero.style.transform = `translateY(${scrolled * 0.5}px)`;
            hero.style.opacity = 1 - scrolled / 500;
        });
    }
    
    // Dynamic gradient on mouse move
    function initDynamicGradient() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const angleX = (y - centerY) / 10;
                const angleY = (centerX - x) / 10;
                
                this.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateY(-4px)`;
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
            });
        });
    }
    
    // Add loading shimmer effect
    function addShimmer(element) {
        if (!element) return;
        element.classList.add('shimmer');
    }
    
    // Remove shimmer effect
    function removeShimmer(element) {
        if (!element) return;
        element.classList.remove('shimmer');
    }
    
    // Animate progress bars
    function animateProgressBar(element, percentage) {
        if (!element) return;
        
        const bar = element.querySelector('.progress-bar-fill') || element;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = percentage + '%';
        }, 100);
    }
    
    // Initialize all animations
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initScrollReveal();
                initCardEffects();
                initParallax();
                initDynamicGradient();
            });
        } else {
            initScrollReveal();
            initCardEffects();
            initParallax();
            initDynamicGradient();
        }
    }
    
    // Export functions
    window.animations = {
        init: init,
        animateNumber: animateNumber,
        addShimmer: addShimmer,
        removeShimmer: removeShimmer,
        animateProgressBar: animateProgressBar,
        initScrollReveal: initScrollReveal
    };
    
    // Auto-initialize
    init();
})();
