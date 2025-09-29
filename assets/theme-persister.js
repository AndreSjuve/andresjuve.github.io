document.addEventListener('DOMContentLoaded', () => {
    // 1. DEFINE YOUR CUSTOM TOGGLE'S ID/CLASS
    // Replace 'my-custom-dark-mode-toggle' with the actual ID or class of your button/element
    const toggleElement = document.getElementById('my-custom-dark-mode-toggle');

    const body = document.body;
    const THEME_KEY = 'website-theme';

    // --- Core Functions ---

    // A. Function to apply the theme CSS class
    function applyTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark');
        } else {
            body.classList.remove('dark');
        }
    }

    // B. Load stored theme immediately on page load
    const savedTheme = localStorage.getItem(THEME_KEY);

    // Default logic: If no preference is saved, respect the system preference (optional)
    if (savedTheme) {
        applyTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // If the user's system preference is dark, use that as a starting point
        applyTheme('dark');
    }
    // If no saved theme and no system preference, it defaults to the 'light' class from Quarto

    // --- Toggle Listener ---

    if (toggleElement) {
        toggleElement.addEventListener('click', () => {
            // Determine the new theme
            const currentTheme = body.classList.contains('dark') ? 'dark' : 'light';
            const newTheme = (currentTheme === 'light') ? 'dark' : 'light';

            // 1. Apply the new theme to the body
            applyTheme(newTheme);

            // 2. Save the new preference to local storage
            localStorage.setItem(THEME_KEY, newTheme);
        });
    }
});
