// Course Management Page JavaScript

// Current filter state
let currentFilter = 'active';

document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const closeMenu = document.getElementById('closeMenu');
    
    // Toggle dropdown menu
    if (menuToggle && dropdownMenu) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = dropdownMenu.style.display === 'block';
            dropdownMenu.style.display = isVisible ? 'none' : 'block';
        });
        
        // Close menu button
        if (closeMenu) {
            closeMenu.addEventListener('click', function(e) {
                e.stopPropagation();
                dropdownMenu.style.display = 'none';
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!menuToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    }
    
    // Apply default filter on page load
    filterCourses('active');
});

// Filter courses by status
function filterCourses(status) {
    currentFilter = status;
    const allCourseItems = document.querySelectorAll('.card[data-course-id]');
    let firstVisibleCourse = null;
    
    // Update button states
    document.getElementById('filterAll').className = status === 'all' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary';
    document.getElementById('filterActive').className = status === 'active' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary';
    document.getElementById('filterInactive').className = status === 'inactive' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary';
    
    // Filter course items
    allCourseItems.forEach(item => {
        const courseStatus = item.getAttribute('data-status');
        
        if (status === 'all' || courseStatus === status) {
            item.style.display = 'block';
            if (!firstVisibleCourse) {
                firstVisibleCourse = item;
            }
        } else {
            item.style.display = 'none';
        }
    });
    
    // Show the first visible course details
    if (firstVisibleCourse) {
        const courseId = firstVisibleCourse.getAttribute('data-course-id');
        showCourseDetails(courseId);
    } else {
        // Hide all course details if no courses match the filter
        const allDetails = document.querySelectorAll('.card[id^="course-"]');
        allDetails.forEach(detail => {
            detail.style.display = 'none';
        });
    }
}

// Show course details when clicking on sidebar item
function showCourseDetails(courseId) {
    // Hide all course details
    const allDetails = document.querySelectorAll('.card[id^="course-"]');
    allDetails.forEach(detail => {
        detail.style.display = 'none';
    });
    
    // Remove active class from all sidebar items
    const allItems = document.querySelectorAll('.card[data-course-id]');
    allItems.forEach(item => {
        item.classList.remove('card-gradient-primary');
    });
    
    // Show selected course details
    const selectedDetails = document.getElementById('course-' + courseId);
    if (selectedDetails) {
        selectedDetails.style.display = 'block';
    }
    
    // Add active class to clicked sidebar item
    const selectedItem = document.querySelector('.card[data-course-id="' + courseId + '"]');
    if (selectedItem) {
        selectedItem.classList.add('card-gradient-primary');
    }
}

// Edit course template
function editCourse(courseId) {
    const detailsBody = document.querySelector('#course-' + courseId + ' > .card-body');
    const editForm = document.getElementById('edit-form-' + courseId);
    
    if (detailsBody && editForm) {
        detailsBody.style.display = 'none';
        editForm.style.display = 'block';
    }
}

// Cancel edit
function cancelEdit(courseId) {
    const detailsBody = document.querySelector('#course-' + courseId + ' > .card-body');
    const editForm = document.getElementById('edit-form-' + courseId);
    
    if (detailsBody && editForm) {
        detailsBody.style.display = 'block';
        editForm.style.display = 'none';
    }
}
