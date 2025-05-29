// Slide navigation and interaction functionality

let currentSlide = 1;
const totalSlides = 10; // Update this when adding more slides

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateSlideCounter();
    updateNavigationButtons();
});

// Navigate to next slide
function nextSlide() {
    if (currentSlide < totalSlides) {
        document.getElementById(`slide-${currentSlide}`).classList.remove('active');
        currentSlide++;
        document.getElementById(`slide-${currentSlide}`).classList.add('active');
        updateSlideCounter();
        updateNavigationButtons();
        scrollToTop();
    }
}

// Navigate to previous slide
function previousSlide() {
    if (currentSlide > 1) {
        document.getElementById(`slide-${currentSlide}`).classList.remove('active');
        currentSlide--;
        document.getElementById(`slide-${currentSlide}`).classList.add('active');
        updateSlideCounter();
        updateNavigationButtons();
        scrollToTop();
    }
}

// Update slide counter display
function updateSlideCounter() {
    document.querySelector('.slide-counter').textContent = `${currentSlide} / ${totalSlides}`;
}

// Update navigation button states
function updateNavigationButtons() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    
    prevButton.disabled = currentSlide === 1;
    nextButton.disabled = currentSlide === totalSlides;
}

// Toggle deep dive sections
function toggleDeepDive(sectionId) {
    const section = document.getElementById(sectionId);
    const button = event.target;
    
    if (section.classList.contains('active')) {
        section.classList.remove('active');
        button.textContent = button.textContent.replace('↑', '↓');
    } else {
        section.classList.add('active');
        button.textContent = button.textContent.replace('↓', '↑');
    }
}

// Scroll to top of slide
function scrollToTop() {
    const activeSlide = document.querySelector('.slide.active');
    if (activeSlide) {
        activeSlide.scrollTop = 0;
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        previousSlide();
    } else if (e.key === 'Escape') {
        // Close all deep dives
        document.querySelectorAll('.deep-dive.active').forEach(section => {
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
    if (!touchStartX) return;
    
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