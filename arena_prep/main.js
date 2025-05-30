// Slide navigation and interaction functionality
let currentSlide = 1;
const totalSlides = 8;
let slidesLoaded = false;

// Slide file mapping
const slideFiles = {
    1: 'slides/slide-1-title.html',
    2: 'slides/slide-2-overview.html',
    3: 'slides/slide-3-claude4.html',
    4: 'slides/slide-4-windows11.html',
    5: 'slides/slide-5-openai-hardware.html',
    6: 'slides/slide-6-codex.html',
    7: 'slides/slide-7-google-io.html',
    8: 'slides/slide-8-geo.html'
};

// Load all slides on page load
async function loadAllSlides() {
    const container = document.getElementById('presentation-container');
    
    try {
        for (let i = 1; i <= totalSlides; i++) {
            const response = await fetch(slideFiles[i]);
            if (!response.ok) {
                throw new Error(`Failed to load slide ${i}: ${response.status}`);
            }
            const slideContent = await response.text();
            container.innerHTML += slideContent;
        }
        
        // Show first slide
        document.getElementById('slide-1').classList.add('active');
        slidesLoaded = true;
        updateSlideCounter();
        updateNavigationButtons();
        
        console.log('All slides loaded successfully');
    } catch (error) {
        console.error('Error loading slides:', error);
        container.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: #dc2626;">
                <h2>Error Loading Presentation</h2>
                <p>Could not load slide files. Please ensure you're running a local server.</p>
                <p>Try: <code>python3 -m http.server 8000</code></p>
                <p>Or use the standalone version: <code>index-complete.html</code></p>
            </div>
        `;
    }
}

// Navigate to next slide
function nextSlide() {
    if (!slidesLoaded || currentSlide >= totalSlides) return;
    
    document.getElementById(`slide-${currentSlide}`).classList.remove('active');
    currentSlide++;
    document.getElementById(`slide-${currentSlide}`).classList.add('active');
    updateSlideCounter();
    updateNavigationButtons();
    scrollToTop();
}

// Navigate to previous slide
function previousSlide() {
    if (!slidesLoaded || currentSlide <= 1) return;
    
    document.getElementById(`slide-${currentSlide}`).classList.remove('active');
    currentSlide--;
    document.getElementById(`slide-${currentSlide}`).classList.add('active');
    updateSlideCounter();
    updateNavigationButtons();
    scrollToTop();
}

// Update slide counter display
function updateSlideCounter() {
    const counter = document.querySelector('.slide-counter');
    if (counter) {
        counter.textContent = `${currentSlide} / ${totalSlides}`;
    }
}

// Update navigation button states
function updateNavigationButtons() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    
    if (prevButton) prevButton.disabled = currentSlide === 1;
    if (nextButton) nextButton.disabled = currentSlide === totalSlides;
}

// Toggle deep dive sections
function toggleDeepDive(sectionId, button) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    
    if (section.style.display === 'none' || !section.style.display) {
        section.style.display = 'block';
        button.textContent = 'Hide Details ↑';
    } else {
        section.style.display = 'none';
        button.textContent = 'Deep Dive →';
    }
}

// Toggle inline expand sections
function toggleExpand(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (element.classList.contains('active')) {
        element.classList.remove('active');
    } else {
        element.classList.add('active');
    }
}

// Scroll to top of slide
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (!slidesLoaded) return;
    
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        previousSlide();
    } else if (e.key === 'Escape') {
        // Close all deep dives
        document.querySelectorAll('.deep-dive').forEach(section => {
            section.style.display = 'none';
        });
        document.querySelectorAll('.deep-dive-button').forEach(button => {
            button.textContent = 'Deep Dive →';
        });
        // Close all expand sections
        document.querySelectorAll('.expand-content').forEach(section => {
            section.classList.remove('active');
        });
    }
});

// Touch navigation for tablets
let touchStartX = null;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
});

document.addEventListener('touchend', function(e) {
    if (!touchStartX || !slidesLoaded) return;
    
    const touchEndX = e.changedTouches[0].clientX;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > 50) { // Minimum swipe distance
        if (diff > 0) {
            nextSlide(); // Swipe left
        } else {
            previousSlide(); // Swipe right
        }
    }
    
    touchStartX = null;
});

// Initialize presentation
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading slides...');
    loadAllSlides();
});

// Export functions for global access
window.nextSlide = nextSlide;
window.previousSlide = previousSlide;
window.toggleDeepDive = toggleDeepDive;
window.toggleExpand = toggleExpand; 