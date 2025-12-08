// main.js の内容
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true' || false;
            
            menuToggle.setAttribute('aria-expanded', !isExpanded);
            // styles.css の .main-nav.is-open クラスを切り替え
            mainNav.classList.toggle('is-open');
        });
    }
});