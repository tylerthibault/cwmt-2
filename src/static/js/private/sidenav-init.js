/**
 * Sidenav Initialization - Runs immediately to prevent FOUC
 * This script must run before the page is rendered to avoid flash of unstyled content
 */
(function() {
  const isCollapsed = localStorage.getItem('sidenav-collapsed');
  if (isCollapsed === 'false') {
    document.documentElement.classList.add('sidenav-expanded');
  }
})();
