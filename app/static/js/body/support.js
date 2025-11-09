document.addEventListener('DOMContentLoaded', function() {
    // Параллакс эффект для фоновых элементов
    document.addEventListener('mousemove', function(e) {
        const orbs = document.querySelectorAll('.orb');
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        orbs.forEach((orb, index) => {
            const speed = (index + 1) * 0.5;
            const xMove = (x - 0.5) * speed * 20;
            const yMove = (y - 0.5) * speed * 20;
            
            orb.style.transform = `translate(${xMove}px, ${yMove}px)`;
        });
    });

    // Анимация появления карточек
    const cards = document.querySelectorAll('.support-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });

    // Интерактивные элементы
    const contactItems = document.querySelectorAll('.contact-item');
    const statusItems = document.querySelectorAll('.status-item');
    const helpItems = document.querySelectorAll('.help-item');
    
    // Добавляем микровзаимодействия
    [...contactItems, ...statusItems, ...helpItems].forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });

    // Анимация иконок при наведении на карточку
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });
});