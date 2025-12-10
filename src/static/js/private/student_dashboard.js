/**
 * Student Dashboard Scripts
 */
document.addEventListener('DOMContentLoaded', function() {
  // Filter functionality
  const courseTypeFilter = document.getElementById('courseTypeFilter');
  const locationFilter = document.getElementById('locationFilter');
  const applyFiltersBtn = document.getElementById('applyFilters');
  const resetFiltersBtn = document.getElementById('resetFilters');
  const courseRows = document.querySelectorAll('.course-row');
  
  // Apply filters (client-side filtering)
  function filterCourses() {
    const courseTypeValue = courseTypeFilter.value;
    const locationValue = locationFilter.value.toLowerCase();
    
    let visibleCount = 0;
    
    courseRows.forEach(row => {
      const rowTemplateId = row.dataset.templateId;
      const rowLocation = (row.dataset.location || '').toLowerCase();
      
      let showRow = true;
      
      // Filter by course type
      if (courseTypeValue && rowTemplateId !== courseTypeValue) {
        showRow = false;
      }
      
      // Filter by location
      if (locationValue && rowLocation !== locationValue) {
        showRow = false;
      }
      
      // Show/hide row
      if (showRow) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });
    
    // Show "no results" message if no courses match
    const calendarDiv = document.getElementById('classCalendar');
    const noResultsMsg = document.getElementById('noResultsMessage');
    
    if (visibleCount === 0 && courseRows.length > 0) {
      if (!noResultsMsg) {
        const tableContainer = calendarDiv.querySelector('.table-responsive');
        if (tableContainer) {
          tableContainer.style.display = 'none';
        }
        
        const msg = document.createElement('div');
        msg.id = 'noResultsMessage';
        msg.className = 'text-center py-5';
        msg.innerHTML = `
          <i class="fas fa-search fa-3x text-muted mb-3"></i>
          <p class="text-muted mb-2">No classes match your filters</p>
          <p class="text-muted small">Try adjusting your search criteria</p>
        `;
        calendarDiv.appendChild(msg);
      }
    } else if (noResultsMsg) {
      noResultsMsg.remove();
      const tableContainer = calendarDiv.querySelector('.table-responsive');
      if (tableContainer) {
        tableContainer.style.display = '';
      }
    }
  }
  
  // Apply filters button
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', filterCourses);
  }
  
  // Reset filters
  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', function() {
      courseTypeFilter.value = '';
      locationFilter.value = '';
      
      // Show all rows
      courseRows.forEach(row => {
        row.style.display = '';
      });
      
      // Remove no results message
      const noResultsMsg = document.getElementById('noResultsMessage');
      if (noResultsMsg) {
        noResultsMsg.remove();
      }
      
      const tableContainer = document.getElementById('classCalendar').querySelector('.table-responsive');
      if (tableContainer) {
        tableContainer.style.display = '';
      }
    });
  }
  
  // Enter key support for filters
  [courseTypeFilter, locationFilter].forEach(filter => {
    if (filter) {
      filter.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
          filterCourses();
        }
      });
      
      // Auto-filter on change
      filter.addEventListener('change', filterCourses);
    }
  });
  
  // Enroll button functionality
  document.querySelectorAll('.enroll-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const courseId = this.dataset.courseId;
      
      if (confirm('Are you sure you want to enroll in this class?')) {
        // Create a form and submit it
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/user/enroll/${courseId}`;
        document.body.appendChild(form);
        form.submit();
      }
    });
  });
});
