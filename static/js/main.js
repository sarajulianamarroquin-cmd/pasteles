document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (flash) {
        setTimeout(function () { flash.style.opacity = '0'; flash.style.transition = 'opacity 0.3s ease'; }, 2500);
    });
});
