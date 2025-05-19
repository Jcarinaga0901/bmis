document.addEventListener('DOMContentLoaded', function() {
    // Set up theme switching
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    
    // Function to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else if (theme === 'light') {
            htmlElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        } else if (theme === 'system') {
            localStorage.setItem('theme', 'system');
            // Use system preference
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                htmlElement.setAttribute('data-theme', 'dark');
            } else {
                htmlElement.setAttribute('data-theme', 'light');
            }
        }
    }
    
    // Initialize theme
    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'system';
        
        // Update radio buttons if they exist
        const themeRadios = document.querySelectorAll('input[name="theme"]');
        if (themeRadios.length) {
            themeRadios.forEach(radio => {
                if (radio.value === savedTheme) {
                    radio.checked = true;
                }
            });
        }
        
        setTheme(savedTheme);
    }
    
    // Watch for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        const currentTheme = localStorage.getItem('theme') || 'system';
        if (currentTheme === 'system') {
            setTheme('system');
        }
    });
    
    // Set up theme toggle functionality
    const themeOptions = document.querySelectorAll('input[name="theme"]');
    themeOptions.forEach(option => {
        option.addEventListener('change', function() {
            if (this.checked) {
                setTheme(this.value);
                
                // Save preference to server if user is logged in
                fetch('/settings/theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ theme: this.value })
                });
            }
        });
    });
    
    // Initialize theme on page load
    initTheme();
    
    // Font size accessibility
    const fontSizeOptions = document.querySelectorAll('input[name="font_size"]');
    fontSizeOptions.forEach(option => {
        option.addEventListener('change', function() {
            if (this.checked) {
                htmlElement.setAttribute('data-font-size', this.value);
                localStorage.setItem('fontSize', this.value);
            }
        });
    });
    
    // Initialize font size
    const savedFontSize = localStorage.getItem('fontSize') || 'medium';
    htmlElement.setAttribute('data-font-size', savedFontSize);
    
    // High contrast toggle
    const highContrastToggle = document.getElementById('high_contrast');
    if (highContrastToggle) {
        highContrastToggle.addEventListener('change', function() {
            htmlElement.setAttribute('data-high-contrast', this.checked);
            localStorage.setItem('highContrast', this.checked ? 'true' : 'false');
        });
        
        // Initialize high contrast
        const savedHighContrast = localStorage.getItem('highContrast') === 'true';
        highContrastToggle.checked = savedHighContrast;
        htmlElement.setAttribute('data-high-contrast', savedHighContrast);
    }
});
