const openButton = document.querySelector('.user-avatar');
const photoContainer = document.querySelector('.photo-container')
const closeButton = document.querySelector('.close-button')

const cancelButton = document.querySelector('.cancel-button')
const deleateButton = document.querySelector('.deleate-Button')


// Проверяем, есть ли изображение при загрузке страницы
checkButtonState();

// Открытие модального окна
openButton.addEventListener('click', function() {
    photoContainer.classList.add('show');
    updateDeleteButtonState();
});

function closeModal() {
    photoContainer.classList.remove('show');
    resetForm();
}

closeButton.addEventListener('click', closeModal);
cancelButton.addEventListener('click', closeModal);

// Закрытие по клику на оверлей
photoContainer.addEventListener('click', function(e) {
    if (e.target === photoContainer) {
        closeModal();
    }
});

