document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Lógica do Menu Mobile ---
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // --- 2. Lógica de Fechar Mensagens ---
    const closeButtons = document.querySelectorAll('.close-message');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // --- 3. Máscara de Telefone ---
    const phoneInputs = document.querySelectorAll('.phone-mask');

    phoneInputs.forEach(input => {
        input.addEventListener('input', function (e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    });

});