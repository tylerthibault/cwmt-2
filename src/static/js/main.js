// Intersection Observer for scroll-triggered animations
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('[class*="animate-"]');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in-view');
                // Optionally unobserve after animation triggers once
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
});
