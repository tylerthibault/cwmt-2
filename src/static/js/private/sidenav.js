document.addEventListener('DOMContentLoaded', function() {
    console.log('Sidenav script loaded');
    
    // Load saved state and sync with html class
    loadSidenavState();
    
    // Remove preload class and html override class to enable transitions
    const sidenav = document.querySelector('.sidenav');
    if (sidenav) {
        setTimeout(() => {
            sidenav.classList.remove('preload');
            document.documentElement.classList.remove('sidenav-expanded');
        }, 100);
    }
    
    const toggleButton = document.querySelector('.sidenav-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            console.log('Toggle button clicked');
            toggleSidenav();
        });
    }

    // Role Switcher functionality
    const roleSwitcher = document.getElementById('roleSwitcher');
    if (roleSwitcher) {
        // Listen for role changes - navigate to role-specific dashboard
        roleSwitcher.addEventListener('change', function() {
            const selectedRole = this.value;
            // Map role to dashboard endpoint
            const dashboardMap = {
                'student': '/student/dashboard',
                'instructor': '/instructor/dashboard',
                'admin': '/admin/dashboard',
                'superuser': '/super/dashboard'
            };
            const dashboardPath = dashboardMap[selectedRole];
            if (dashboardPath) {
                window.location.href = dashboardPath;
            }
        });
    }

    function toggleSidenav() {
        const sidenav = document.querySelector('.sidenav');
        const toggleButton = document.querySelector('.sidenav-toggle');
        const isCollapsed = sidenav.classList.toggle('collapsed');
        
        // Update ARIA attribute
        if (toggleButton) {
            toggleButton.setAttribute('aria-expanded', !isCollapsed);
        }
        
        saveSidenavState();
    }

    function closeSidenav() {
        document.querySelector('.sidenav').classList.add('collapsed');
        saveSidenavState();
    }

    function openSidenav() {
        document.querySelector('.sidenav').classList.remove('collapsed');
        saveSidenavState();
    }

    function saveSidenavState() {
        const sidenav = document.querySelector('.sidenav');
        const isCollapsed = sidenav.classList.contains('collapsed');
        localStorage.setItem('sidenav-collapsed', isCollapsed);
    }

    function loadSidenavState() {
        const isCollapsed = localStorage.getItem('sidenav-collapsed') === 'true';
        const sidenav = document.querySelector('.sidenav');
        const toggleButton = document.querySelector('.sidenav-toggle');
        
        if (isCollapsed) {
            sidenav.classList.add('collapsed');
        } else {
            sidenav.classList.remove('collapsed');
        }
        
        // Update ARIA attribute to match state
        if (toggleButton) {
            toggleButton.setAttribute('aria-expanded', !isCollapsed);
        }
    }
});