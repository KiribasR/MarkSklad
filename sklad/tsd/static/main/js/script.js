// Получаем элементы DOM
const popup = document.getElementById('popup');
const openPopupButton = document.getElementById('openPopup');
const closePopupButton = document.getElementById('closePopup');

// Открываем всплывающее окно
openPopupButton.addEventListener('click', () => {
    popup.style.display = 'block';
});

// Закрываем всплывающее окно
closePopupButton.addEventListener('click', () => {
    popup.style.display = 'none';
});

// Закрываем окно при клике вне его области
window.addEventListener('click', (event) => {
    if (event.target === popup) {
        popup.style.display = 'none';
    }
});