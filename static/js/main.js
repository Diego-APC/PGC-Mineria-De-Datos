// Acordeones: toggle de apertura/cierre
document.addEventListener('DOMContentLoaded', function() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            
            if (content.classList.contains('open')) {
                content.classList.remove('open');
                content.style.maxHeight = null;
            } else {
                content.classList.add('open');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
});