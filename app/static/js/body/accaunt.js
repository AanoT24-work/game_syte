// Элементы для модального окна аватара
const openAvatarButton = document.getElementById('openAvatarModal');
const photoContainer = document.getElementById('photoContainer');
const closeAvatarButton = document.getElementById('closeAvatarButton');
const cancelAvatarButton = document.getElementById('cancelAvatarButton');
const deleteButton = document.getElementById('deleteButton');
const overlay = document.getElementById('overlay');
const fileInput = document.getElementById('fileInput');
const fileInputLabel = document.getElementById('fileInputLabel');
const avatarPreview = document.getElementById('avatarPreview');
const fileInputText = document.getElementById('fileInputText');
const avatarForm = document.getElementById('avatarForm');

// Элементы для модального окна поста
const openPostButton = document.getElementById('openPostModal');
const postContainer = document.getElementById('postContainer');
const closePostButton = document.getElementById('closePostButton');
const cancelPostButton = document.getElementById('cancelPostButton');
const postForm = document.getElementById('postForm');
const postInput = document.getElementById('postInput');
const postInputLabel = document.getElementById('postInputLabel');
const postPreview = document.getElementById('postPreview');
const postInputText = document.querySelector('.post-input-text');

// Функция для проверки наличия аватара у пользователя
function userHasAvatar() {
    const userAvatar = document.querySelector('.user-avatar img');
    const userAvatarSpan = document.querySelector('.user-avatar span');
    
    return userAvatar && !userAvatarSpan;
}

// Функция для получения текущего аватара пользователя
function getCurrentUserAvatar() {
    const userAvatar = document.querySelector('.user-avatar img');
    if (userAvatar && userAvatar.src) {
        return userAvatar.src;
    }
    return null;
}

// Функция инициализации превью аватара
function initAvatarPreview() {
    if (!avatarPreview || !fileInputText || !fileInputLabel) return;
    
    const hasAvatar = userHasAvatar();
    const currentAvatar = getCurrentUserAvatar();
    
    if (hasAvatar && currentAvatar) {
        avatarPreview.src = currentAvatar;
        avatarPreview.style.display = 'block';
        fileInputText.style.display = 'none';
        fileInputLabel.classList.add('has-image');
    } else {
        avatarPreview.style.display = 'none';
        fileInputText.style.display = 'block';
        fileInputLabel.classList.remove('has-image');
        avatarPreview.src = '';
    }
}

// Функция инициализации превью поста
function initPostPreview() {
    if (!postPreview || !postInputText || !postInputLabel) return;
    
    postPreview.style.display = 'none';
    postInputText.style.display = 'block';
    postInputLabel.classList.remove('has-image');
    postPreview.src = '';
}

// Проверяем что все элементы существуют
if (openAvatarButton && photoContainer && overlay && closeAvatarButton && cancelAvatarButton) {

    // Инициализация при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        initAvatarPreview();
        initPostPreview();
    });

    // Также инициализируем когда все ресурсы загружены
    window.addEventListener('load', function() {
        initAvatarPreview();
        initPostPreview();
    });

    // Открытие модального окна аватара
    openAvatarButton.addEventListener('click', function() {
        initAvatarPreview();
        openModal(photoContainer);
    });

    // Открытие модального окна поста
    if (openPostButton && postContainer) {
        openPostButton.addEventListener('click', function() {
            resetPostForm();
            openModal(postContainer);
        });
    }

    // Функция открытия модального окна
    function openModal(modal) {
        overlay.style.display = 'block';
        modal.style.display = 'flex';
        
        setTimeout(() => {
            overlay.classList.add('show');
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }, 10);
    }

    // Плавное закрытие модального окна
    function closeModal() {
        const openModals = document.querySelectorAll('.photo-container.show, .post-container.show');
        
        openModals.forEach(modal => {
            modal.classList.remove('show');
        });
        overlay.classList.remove('show');
        
        setTimeout(() => {
            document.querySelectorAll('.photo-container, .post-container').forEach(modal => {
                modal.style.display = 'none';
            });
            overlay.style.display = 'none';
            document.body.style.overflow = '';
            
            resetAvatarForm();
            resetPostForm();
        }, 300);
    }

    // Закрытие по кнопкам
    closeAvatarButton.addEventListener('click', closeModal);
    cancelAvatarButton.addEventListener('click', closeModal);
    
    if (closePostButton) {
        closePostButton.addEventListener('click', closeModal);
    }
    if (cancelPostButton) {
        cancelPostButton.addEventListener('click', closeModal);
    }
    
    // Закрытие по клику на оверлей
    overlay.addEventListener('click', closeModal);

    // Закрытие по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Обработка выбора файла для аватара
    if (fileInput && avatarPreview && fileInputLabel && fileInputText) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.type.startsWith('image/')) {
                    fileInput.value = '';
                    return;
                }
                
                if (file.size > 5 * 1024 * 1024) {
                    fileInput.value = '';
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    avatarPreview.src = e.target.result;
                    avatarPreview.style.display = 'block';
                    fileInputText.style.display = 'none';
                    fileInputLabel.classList.add('has-image');
                }
                
                reader.readAsDataURL(file);
            }
        });
    }

    // Обработка выбора файла для поста
    if (postInput && postPreview && postInputLabel && postInputText) {
        postInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.type.startsWith('image/')) {
                    postInput.value = '';
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) {
                    postInput.value = '';
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    postPreview.src = e.target.result;
                    postPreview.style.display = 'block';
                    postInputText.style.display = 'none';
                    postInputLabel.classList.add('has-image');
                }
                
                reader.readAsDataURL(file);
            }
        });
    }

    // Удаление аватара
    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите удалить аватар?')) {
                const originalText = deleteButton.textContent;
                deleteButton.textContent = 'Удаление...';
                deleteButton.disabled = true;
                
                fetch('/delete-avatar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        const userAvatar = document.getElementById('openAvatarModal');
                        if (userAvatar) {
                            userAvatar.innerHTML = '<span>👤</span>';
                        }
                        
                        initAvatarPreview();
                        
                        setTimeout(() => {
                            closeModal();
                        }, 500);
                        
                    } else {
                        throw new Error(data.error || 'Unknown error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    deleteButton.textContent = originalText;
                    deleteButton.disabled = false;
                });
            }
        });
    }

    // Отправка формы аватара
    if (avatarForm && fileInput) {
        avatarForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!fileInput.files[0]) {
                return;
            }
            
            const submitButton = avatarForm.querySelector('.save_button');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Загрузка...';
            submitButton.disabled = true;
            
            const formData = new FormData();
            formData.append('avatar', fileInput.files[0]);
            
            fetch('/upload-avatar', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const timestamp = '?t=' + new Date().getTime();
                    const userAvatar = document.getElementById('openAvatarModal');
                    
                    if (userAvatar) {
                        userAvatar.innerHTML = `<img src="${data.avatar_url}${timestamp}" alt="Аватар">`;
                    }
                    
                    initAvatarPreview();
                    
                    setTimeout(() => {
                        closeModal();
                    }, 500);
                    
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
    }

    // Отправка формы поста
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const content = postForm.querySelector('textarea[name="content"]').value.trim();
            const imageFile = postInput.files[0];
            
            if (!content && !imageFile) {
                return;
            }
            
            const submitButton = postForm.querySelector('.save_button');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Публикация...';
            submitButton.disabled = true;
            
            const formData = new FormData();
            formData.append('content', content);
            if (imageFile) {
                formData.append('image', imageFile);
            }
            
            fetch('/post/create-ajax', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
    }

    // Сброс формы аватара
    function resetAvatarForm() {
        if (fileInput) fileInput.value = '';
        setTimeout(() => {
            initAvatarPreview();
        }, 100);
    }

    // Сброс формы поста
    function resetPostForm() {
        if (postInput) postInput.value = '';
        if (postForm) {
            const textarea = postForm.querySelector('textarea[name="content"]');
            if (textarea) textarea.value = '';
        }
        initPostPreview();
    }

} else {
    console.error('Не найдены необходимые элементы для модального окна');
}

// Предотвращаем закрытие при клике на само модальное окно
document.addEventListener('click', function(e) {
    if (e.target.closest('.photo-content') || e.target.closest('.post-content')) {
        e.stopPropagation();
    }
});