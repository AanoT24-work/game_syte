// Элементы
const openButton = document.getElementById('openAvatarModal');
const photoContainer = document.getElementById('photoContainer');
const closeButton = document.getElementById('closeButton');
const cancelButton = document.getElementById('cancelButton');
const deleteButton = document.getElementById('deleteButton');
const overlay = document.getElementById('overlay');
const fileInput = document.getElementById('fileInput');
const fileInputLabel = document.getElementById('fileInputLabel');
const avatarPreview = document.getElementById('avatarPreview');
const avatarForm = document.getElementById('avatarForm');
const userAvatar = document.getElementById('openAvatarModal');

// Открытие модального окна
openButton.addEventListener('click', function() {
    photoContainer.classList.add('show');
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
});

// Закрытие модального окна
function closeModal() {
    photoContainer.classList.remove('show');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
    resetForm();
}

closeButton.addEventListener('click', closeModal);
cancelButton.addEventListener('click', closeModal);
overlay.addEventListener('click', closeModal);

// Обработка выбора файла
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            avatarPreview.src = e.target.result;
            fileInputLabel.classList.add('has-image');
        }
        
        reader.readAsDataURL(file);
    }
});

// Удаление аватара
deleteButton.addEventListener('click', function() {
    if (confirm('Вы уверены, что хотите удалить аватар?')) {
        // Отправка запроса на удаление
        fetch('/delete-avatar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновляем аватар в интерфейсе
                userAvatar.innerHTML = '<span>👤</span>';
                closeModal();
                alert('Аватар удален');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении аватара');
        });
    }
});

// Отправка формы
avatarForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('avatar', fileInput.files[0]);
    
    fetch('/upload-avatar', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем аватар в интерфейсе
            userAvatar.innerHTML = `<img src="${data.avatar_url}" alt="Аватар">`;
            closeModal();
            alert('Аватар обновлен');
        } else {
            alert('Ошибка при загрузке аватара: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при загрузке аватара');
    });
});

// Сброс формы
function resetForm() {
    fileInput.value = '';
    fileInputLabel.classList.remove('has-image');
    avatarPreview.src = '';
}

// Закрытие по ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Плавное открытие модального окна
openButton.addEventListener('click', function() {
    // Сначала показываем оверлей
    overlay.style.display = 'block';
    photoContainer.style.display = 'flex';
    
    // Даем время для отрисовки
    setTimeout(() => {
        overlay.classList.add('show');
        photoContainer.classList.add('show');
        document.body.style.overflow = 'hidden';
    }, 10);
});

// Плавное закрытие модального окна
function closeModal() {
    overlay.classList.remove('show');
    photoContainer.classList.remove('show');
    
    setTimeout(() => {
        overlay.style.display = 'none';
        photoContainer.style.display = 'none';
        document.body.style.overflow = '';
        resetForm();
    }, 300);
}