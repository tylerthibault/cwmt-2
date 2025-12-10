/**
 * User Management Page Scripts
 */
document.addEventListener('DOMContentLoaded', function() {
  // Create User Menu
  const createUserToggle = document.getElementById('createUserToggle');
  const createUserMenu = document.getElementById('createUserMenu');
  const closeCreateUserMenu = document.getElementById('closeCreateUserMenu');
  const createPassword = document.getElementById('createPassword');
  const createConfirmPassword = document.getElementById('createConfirmPassword');
  
  // Toggle create user dropdown menu
  if (createUserToggle && createUserMenu) {
    createUserToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      createUserMenu.classList.toggle('show');
      // Close the other menu if open
      if (dropdownMenu) dropdownMenu.classList.remove('show');
    });
    
    // Close create user menu button
    if (closeCreateUserMenu) {
      closeCreateUserMenu.addEventListener('click', function() {
        createUserMenu.classList.remove('show');
      });
    }
  }
  
  // Password validation for create user form
  if (createPassword && createConfirmPassword) {
    createConfirmPassword.addEventListener('input', function() {
      if (createPassword.value !== createConfirmPassword.value) {
        createConfirmPassword.setCustomValidity('Passwords do not match');
      } else {
        createConfirmPassword.setCustomValidity('');
      }
    });
    
    createPassword.addEventListener('input', function() {
      if (createConfirmPassword.value && createPassword.value !== createConfirmPassword.value) {
        createConfirmPassword.setCustomValidity('Passwords do not match');
      } else {
        createConfirmPassword.setCustomValidity('');
      }
    });
  }
  
  // Add to Role Menu
  const menuToggle = document.getElementById('menuToggle');
  const dropdownMenu = document.getElementById('dropdownMenu');
  const closeMenu = document.getElementById('closeMenu');
  const userSelect = document.getElementById('userSelect');
  const addUserBtn = document.getElementById('addUserBtn');
  
  // Toggle add to role dropdown menu
  if (menuToggle && dropdownMenu) {
    menuToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      dropdownMenu.classList.toggle('show');
      // Close the other menu if open
      if (createUserMenu) createUserMenu.classList.remove('show');
    });
    
    // Close menu button
    if (closeMenu) {
      closeMenu.addEventListener('click', function() {
        dropdownMenu.classList.remove('show');
      });
    }
  }
  
  // Close menus when clicking outside
  document.addEventListener('click', function(e) {
    if (dropdownMenu && !dropdownMenu.contains(e.target) && e.target !== menuToggle) {
      dropdownMenu.classList.remove('show');
    }
    if (createUserMenu && !createUserMenu.contains(e.target) && e.target !== createUserToggle) {
      createUserMenu.classList.remove('show');
    }
  });
  
  // Close menus on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (dropdownMenu) dropdownMenu.classList.remove('show');
      if (createUserMenu) createUserMenu.classList.remove('show');
    }
  });
  
  // Enable/disable button based on selection
  if (userSelect && addUserBtn) {
    userSelect.addEventListener('change', function() {
      addUserBtn.disabled = !this.value;
    });
  }
});
