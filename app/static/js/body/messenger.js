let currentChatUserId = null;
let searchTimeout;
let chatUpdateInterval;
let currentEditingMessageId = null;

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    console.log('Messenger initialized');
    loadChatsList();
    updateUnreadCount();
    
    // Инициализация обработчиков событий
    initEventListeners();
    
    // Запускаем автообновление списка чатов
    startChatsAutoUpdate();
});

function initEventListeners() {
    const userSearch = document.getElementById('userSearch');
    if (userSearch) {
        userSearch.addEventListener('input', handleUserSearch);
    }
    
    // Делегирование событий для всей страницы
    document.addEventListener('click', function(e) {
        // Кнопка редактирования сообщения
        if (e.target.closest('.message-edit-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const messageElement = e.target.closest('.message');
            if (messageElement) {
                const messageId = messageElement.getAttribute('data-message-id');
                const messageText = messageElement.querySelector('.message-text')?.textContent;
                
                console.log('✏️ Delegated edit click - Message ID:', messageId, 'Text:', messageText);
                
                if (messageId && messageText) {
                    editMessage(parseInt(messageId), messageText);
                }
            }
        }
        
        // Кнопка удаления сообщения
        if (e.target.closest('.message-delete-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const messageElement = e.target.closest('.message');
            if (messageElement) {
                const messageId = messageElement.getAttribute('data-message-id');
                
                console.log('🗑️ Delegated delete click - Message ID:', messageId);
                
                if (messageId) {
                    deleteMessage(parseInt(messageId));
                }
            }
        }
        
        // Закрываем результаты поиска при клике вне поиска
        if (!e.target.closest('.search-box')) {
            const results = document.getElementById('searchResults');
            if (results) results.style.display = 'none';
        }
    });
    
    // Обработчик отправки форм
    document.addEventListener('submit', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Закрываем по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const results = document.getElementById('searchResults');
            if (results) results.style.display = 'none';
            
            // Также закрываем модальное окно редактирования
            const overlay = document.getElementById('editMessageOverlay');
            if (overlay) {
                overlay.remove();
                currentEditingMessageId = null;
            }
        }
    });
}

// Функция для рендеринга аватарки
function renderAvatar(user, element) {
    if (!element) return;
    
    const userId = user.id || user.user_id;
    if (!user || !userId) {
        element.innerHTML = '<span>👤</span>';
        return;
    }
    
    element.innerHTML = '';
    
    if (user.avatar && user.avatar !== 'default_avatar.png' && user.avatar !== 'None') {
        const avatarUrl = `/avatar/${userId}`;
        console.log('✅ Using avatar URL (from feed):', avatarUrl);
        
        const img = document.createElement('img');
        img.src = avatarUrl;
        img.alt = 'Аватар';
        img.className = 'avatar-image';
        
        img.onerror = function() {
            console.log('❌ Avatar failed to load, using fallback');
            this.style.display = 'none';
            element.innerHTML = '<span>👤</span>';
        };
        
        element.appendChild(img);
    } else {
        console.log('ℹ️ Using default avatar (emoji)');
        element.innerHTML = '<span>👤</span>';
    }
}

// ПОИСК ПОЛЬЗОВАТЕЛЕЙ
function handleUserSearch(e) {
    const query = e.target.value.trim();
    let resultsContainer = document.getElementById('searchResults');
    
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'searchResults';
        resultsContainer.className = 'search-results';
        document.querySelector('.search-box').appendChild(resultsContainer);
    }
    
    clearTimeout(searchTimeout);
    
    if (query.length < 2) {
        resultsContainer.style.display = 'none';
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetch(`/search_users?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(users => {
                displaySearchResults(users);
            })
            .catch(error => {
                console.error('Search error:', error);
                resultsContainer.innerHTML = '<div class="no-results">Ошибка поиска</div>';
                resultsContainer.style.display = 'block';
            });
    }, 300);
}

function displaySearchResults(users) {
    const resultsContainer = document.getElementById('searchResults');
    const template = document.getElementById('searchResultTemplate');
    
    if (!resultsContainer || !template) return;
    
    if (!Array.isArray(users) || users.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">Пользователи не найдены</div>';
        resultsContainer.style.display = 'block';
        return;
    }
    
    resultsContainer.innerHTML = '';
    
    users.forEach(user => {
        const clone = template.content.cloneNode(true);
        const item = clone.querySelector('.search-result-item');
        const avatar = clone.querySelector('.result-avatar');
        const username = clone.querySelector('.result-username');
        const status = clone.querySelector('.result-chat-status');
        
        if (!item || !avatar || !username || !status) return;
        
        renderAvatar(user, avatar);
        username.textContent = user.username;
        status.textContent = user.has_chat ? '💬 Чат есть' : '➕ Новый чат';
        status.className = `result-chat-status ${user.has_chat ? 'has-chat' : 'new-chat'}`;
        
        const userId = user.id || user.user_id;
        if (userId) {
            item.addEventListener('click', () => startChat(userId));
        }
        
        resultsContainer.appendChild(clone);
    });
    
    resultsContainer.style.display = 'block';
}

// ЗАГРУЗКА СПИСКА ЧАТОВ
function loadChatsList() {
    fetch('/get_chats')
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(chats => {
            displayChatsList(chats);
        })
        .catch(error => {
            console.error('Error loading chats:', error);
            const chatsList = document.getElementById('chatsList');
            if (chatsList) {
                chatsList.innerHTML = `
                    <div class="no-chats">
                        <div>⚠️</div>
                        <div>Ошибка загрузки чатов</div>
                    </div>
                `;
            }
        });
}

function displayChatsList(chats) {
    const chatsList = document.getElementById('chatsList');
    const template = document.getElementById('chatItemTemplate');
    
    if (!chatsList) return;
    
    if (!chats || chats.length === 0) {
        chatsList.innerHTML = `
            <div class="no-chats">
                <div>💬</div>
                <div>Чатов пока нет</div>
                <div>Найдите пользователя чтобы начать общение</div>
            </div>
        `;
        return;
    }
    
    chatsList.innerHTML = '';
    
    chats.forEach(chat => {
        if (!template) return;
        
        const clone = template.content.cloneNode(true);
        const chatItem = clone.querySelector('.chat-item');
        const chatAvatar = clone.querySelector('.chat-avatar');
        const chatName = clone.querySelector('.chat-name');
        const lastMessage = clone.querySelector('.chat-last-message');
        const chatTime = clone.querySelector('.chat-time');
        const chatUnread = clone.querySelector('.chat-unread');
        const clearBtn = clone.querySelector('.chat-clear-btn');
        
        if (!chatItem || !chatAvatar || !chatName) return;
        
        const userId = chat.id || chat.user_id;
        chatItem.setAttribute('data-user-id', userId);
        
        renderAvatar(chat, chatAvatar);
        chatName.textContent = chat.username;
        
        if (lastMessage) {
            lastMessage.textContent = chat.last_message || 'Нет сообщений';
        }
        
        if (chatTime) {
            chatTime.textContent = formatTime(chat.last_message_time);
        }
        
        if (chatUnread && chat.unread_count > 0) {
            chatUnread.textContent = chat.unread_count;
            chatUnread.style.display = 'flex';
        }
        
        if (userId) {
            chatItem.addEventListener('click', () => openChat(userId));
            
            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    clearChat(userId);
                });
            }
        }
        
        chatsList.appendChild(clone);
    });
}

// ОТКРЫТИЕ ЧАТА ИЗ СПИСКА
function openChat(userId) {
    console.log('Opening chat with user:', userId);
    stopChatAutoUpdate();
    loadChat(userId);
    startChatAutoUpdate(userId);
}

// ЗАГРУЗКА КОНКРЕТНОГО ЧАТА
function loadChat(userId) {
    console.log('🔍 loadChat called for user:', userId);
    currentChatUserId = userId;
    
    fetch(`/get_messages/${userId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            console.log('📨 Chat data received:', {
                user: data.user,
                messagesCount: data.messages ? data.messages.length : 0,
                firstMessage: data.messages ? data.messages[0] : null
            });
            displayChat(data);
        })
        .catch(error => {
            console.error('❌ Error loading chat:', error);
            alert('Ошибка загрузки чата');
        });
}

// ОТОБРАЖЕНИЕ ЧАТА
function displayChat(chatData) {
    const messContainer = document.getElementById('messContainer');
    const template = document.getElementById('chatWindowTemplate');
    
    if (!messContainer || !template) return;
    
    messContainer.innerHTML = '';
    const clone = template.content.cloneNode(true);
    
    const avatar = clone.getElementById('chatHeaderAvatar');
    const name = clone.getElementById('chatHeaderName');
    const clearBtn = clone.getElementById('clearChatBtn');
    const messagesContainer = clone.getElementById('chatMessages');
    const chatInput = clone.getElementById('chatInput');
    const sendBtn = clone.getElementById('sendMessageBtn');
    const chatForm = clone.getElementById('chatForm');
    
    if (!avatar || !name || !messagesContainer) return;
    
    renderAvatar(chatData.user, avatar);
    name.textContent = chatData.user.username;
    
    if (chatData.messages && chatData.messages.length > 0) {
        chatData.messages.forEach(msg => {
            addMessageToContainer(messagesContainer, msg, chatData.user.id || chatData.user.user_id);
        });
    }
    
    const userId = chatData.user.id || chatData.user.user_id;
    if (clearBtn && userId) {
        clearBtn.addEventListener('click', () => clearChat(userId));
    }
    
    // Обработка отправки сообщений
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            sendMessage();
        });
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Обработка формы, если она есть
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
            return false;
        });
    }
    
    messContainer.appendChild(clone);
    
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
    
    if (chatInput) {
        chatInput.focus();
    }
}

// ФУНКЦИЯ ДОБАВЛЕНИЯ СООБЩЕНИЯ В КОНТЕЙНЕР
function addMessageToContainer(container, msg, chatUserId) {
    console.log('📝 addMessageToContainer:', msg.id, 'sender_id:', msg.sender_id, 'chatUserId:', chatUserId);
    
    const isIncoming = parseInt(msg.sender_id) === parseInt(chatUserId);
    console.log('📱 Message is incoming?', isIncoming);
    
    const template = document.getElementById('messageTemplate');
    if (!template) {
        console.error('❌ messageTemplate not found!');
        return;
    }
    
    const clone = template.content.cloneNode(true);
    
    const messageEl = clone.querySelector('.message');
    const textEl = clone.querySelector('.message-text');
    const timeEl = clone.querySelector('.message-time-text');
    const editedEl = clone.querySelector('.message-edited');
    const editBtn = clone.querySelector('.message-edit-btn');
    const deleteBtn = clone.querySelector('.message-delete-btn');
    
    if (!messageEl || !textEl) return;
    
    messageEl.setAttribute('data-message-id', msg.id);
    messageEl.classList.add(isIncoming ? 'message-in' : 'message-out');
    textEl.textContent = msg.text;
    
    if (timeEl) {
        timeEl.textContent = formatTime(msg.created_at);
    }
    
    if (editedEl) {
        if (msg.is_edited) {
            editedEl.style.display = 'inline';
            if (msg.edited_at) {
                editedEl.title = 'Отредактировано: ' + formatTime(msg.edited_at);
            }
        } else {
            editedEl.style.display = 'none';
        }
    }
    
    // Устанавливаем видимость кнопок
    if (isIncoming) {
        // Для входящих сообщений скрываем кнопки
        if (editBtn) editBtn.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';
    } else {
        // Для исходящих сообщений показываем кнопки
        if (editBtn) {
            const messageTime = new Date(msg.created_at);
            const now = new Date();
            const minutesDiff = (now - messageTime) / (1000 * 60);
            const canEdit = minutesDiff <= 15;
            
            if (canEdit) {
                editBtn.style.display = 'flex';
                editBtn.dataset.messageId = msg.id;
                editBtn.dataset.messageText = msg.text;
            } else {
                editBtn.style.display = 'none';
            }
        }
        
        if (deleteBtn) {
            deleteBtn.style.display = 'flex';
            deleteBtn.dataset.messageId = msg.id;
        }
    }
    
    container.appendChild(clone);
}

// ФУНКЦИЯ РЕДАКТИРОВАНИЯ СООБЩЕНИЯ
function editMessage(messageId, currentText) {
    console.log('📝 editMessage called for message:', messageId, 'Text:', currentText);
    
    if (currentEditingMessageId === messageId) {
        console.log('⚠️ Message already being edited');
        return;
    }
    
    currentEditingMessageId = messageId;
    
    // Создаем модальное окно
    const overlay = document.createElement('div');
    overlay.className = 'edit-message-overlay';
    overlay.id = 'editMessageOverlay';
    
    overlay.innerHTML = `
        <div class="edit-message-modal">
            <div class="edit-message-header">
                <h3>Редактирование сообщения</h3>
                <button class="close-edit-btn" id="closeEditBtn">&times;</button>
            </div>
            <div class="edit-message-content">
                <textarea class="edit-message-textarea" placeholder="Введите новый текст сообщения..." maxlength="2000">${currentText}</textarea>
                <div class="edit-message-history">
                    <div class="history-title">История изменений:</div>
                    <div class="history-items" id="historyItems">
                        <div class="history-item">Загрузка истории...</div>
                    </div>
                </div>
            </div>
            <div class="edit-message-actions">
                <button class="edit-cancel-btn" id="editCancelBtn">Отмена</button>
                <button class="edit-save-btn" id="editSaveBtn">Сохранить изменения</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    const textarea = overlay.querySelector('.edit-message-textarea');
    const historyContainer = overlay.querySelector('#historyItems');
    const closeBtn = overlay.querySelector('#closeEditBtn');
    const cancelBtn = overlay.querySelector('#editCancelBtn');
    const saveBtn = overlay.querySelector('#editSaveBtn');
    
    // Загружаем историю редактирования
    loadMessageHistory(messageId, historyContainer);
    
    // Функция закрытия модального окна
    function closeModal() {
        if (overlay && overlay.parentNode) {
            overlay.remove();
        }
        currentEditingMessageId = null;
    }
    
    // Обработчики событий
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeModal();
        }
    });
    
    saveBtn.addEventListener('click', () => {
        const newText = textarea.value.trim();
        if (!newText) {
            alert('Сообщение не может быть пустым');
            return;
        }
        
        if (newText === currentText) {
            alert('Сообщение не изменилось');
            return;
        }
        
        saveEditedMessage(messageId, newText, closeModal);
    });
    
    // Фокус на текстовом поле
    setTimeout(() => {
        textarea.focus();
        textarea.select();
    }, 100);
}

// ЗАГРУЗКА ИСТОРИИ РЕДАКТИРОВАНИЯ
function loadMessageHistory(messageId, container) {
    fetch(`/get_message_history/${messageId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            if (data.success && data.history && data.history.length > 0) {
                container.innerHTML = '';
                data.history.forEach((item, index) => {
                    const historyItem = document.createElement('div');
                    historyItem.className = 'history-item';
                    
                    const changeText = document.createElement('div');
                    changeText.textContent = `"${item.old_text}" → "${item.new_text}"`;
                    
                    const time = document.createElement('div');
                    time.className = 'history-time';
                    time.textContent = formatTime(item.edited_at);
                    
                    historyItem.appendChild(changeText);
                    historyItem.appendChild(time);
                    container.appendChild(historyItem);
                });
            } else {
                container.innerHTML = '<div class="history-item">История изменений отсутствует</div>';
            }
        })
        .catch(error => {
            console.error('Error loading message history:', error);
            container.innerHTML = '<div class="history-item">Ошибка загрузки истории</div>';
        });
}

// СОХРАНЕНИЕ ОТРЕДАКТИРОВАННОГО СООБЩЕНИЯ
function saveEditedMessage(messageId, newText, closeModalCallback) {
    fetch(`/edit_message/${messageId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: newText
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Обновляем сообщение в UI
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                const textEl = messageElement.querySelector('.message-text');
                const editedEl = messageElement.querySelector('.message-edited');
                const timeEl = messageElement.querySelector('.message-time-text');
                
                if (textEl) textEl.textContent = newText;
                if (editedEl) {
                    editedEl.style.display = 'inline';
                    editedEl.title = 'Отредактировано: ' + formatTime(data.edited_at);
                }
                if (timeEl) {
                    timeEl.textContent = formatTime(data.created_at || new Date().toISOString());
                }
            }
            
            // Обновляем список чатов
            updateChatsList();
            
            // Закрываем модальное окно
            if (closeModalCallback) {
                closeModalCallback();
            }
            
            alert('Сообщение успешно отредактировано!');
        } else {
            alert('Ошибка редактирования: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        console.error('Error saving edited message:', error);
        alert('Ошибка сохранения изменений: ' + error.message);
    });
}

// УДАЛЕНИЕ СООБЩЕНИЯ
function deleteMessage(messageId) {
    if (!confirm('Удалить это сообщение?')) {
        return;
    }
    
    fetch(`/delete_message/${messageId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (currentChatUserId) {
                loadChat(currentChatUserId);
            }
            loadChatsList();
        } else {
            alert('Ошибка удаления: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Delete message error:', error);
        alert('Ошибка удаления сообщения');
    });
}

// ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ (ИСПРАВЛЕННАЯ)
function sendMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const text = input.value.trim();
    if (!text || !currentChatUserId) return;
    
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            receiver_id: currentChatUserId,
            text: text
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            updateCurrentChat();
            updateChatsList();
        } else {
            alert('Ошибка отправки: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Send message error:', error);
        alert('Ошибка отправки сообщения');
    });
    
    return false;
}

// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
function startChat(userId) {
    fetch(`/start_chat/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success || data.chat_exists) {
                const results = document.getElementById('searchResults');
                if (results) results.style.display = 'none';
                
                const searchInput = document.getElementById('userSearch');
                if (searchInput) searchInput.value = '';
                
                openChat(data.chat_id || userId);
                updateChatsList();
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Start chat error:', error);
            alert('Ошибка при создании чата');
        });
}

function clearChat(userId, event = null) {
    if (event) {
        event.stopPropagation();
    }
    
    if (!confirm('Очистить всю переписку с этим пользователем? Это действие нельзя отменить.')) {
        return;
    }
    
    fetch(`/clear_chat/${userId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Удалено ${data.deleted_count} сообщений`);
            if (currentChatUserId === userId) {
                loadChat(userId);
            }
            loadChatsList();
        } else {
            alert('Ошибка очистки чата: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Clear chat error:', error);
        alert('Ошибка очистки чата');
    });
}

function formatTime(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (date.toDateString() === now.toDateString()) {
            if (diffMins < 1) return 'только что';
            if (diffMins < 60) return `${diffMins} мин назад`;
            return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
        }
        if (diffDays === 1) {
            return `вчера в ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
        }
        if (diffDays < 7) {
            return `${date.toLocaleDateString('ru-RU', { weekday: 'short' })} ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
        }
        return date.toLocaleDateString('ru-RU', { 
            day: '2-digit', 
            month: '2-digit', 
            year: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return '';
    }
}

function updateUnreadCount() {
    fetch('/get_unread_count')
        .then(response => response.json())
        .then(data => {
            console.log('Unread messages:', data.unread_count);
        })
        .catch(error => {
            console.error('Error getting unread count:', error);
        });
}

// Функции для автообновления чата
function startChatAutoUpdate(userId) {
    if (chatUpdateInterval) {
        clearInterval(chatUpdateInterval);
    }
    
    chatUpdateInterval = setInterval(() => {
        if (currentChatUserId === userId) {
            updateCurrentChat();
        }
    }, 500);
}

function stopChatAutoUpdate() {
    if (chatUpdateInterval) {
        clearInterval(chatUpdateInterval);
        chatUpdateInterval = null;
    }
}

function updateCurrentChat() {
    if (!currentChatUserId) return;
    
    fetch(`/get_messages/${currentChatUserId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            updateChatMessages(data.messages);
            updateChatsList();
        })
        .catch(error => {
            console.error('Error updating chat:', error);
        });
}

function updateChatMessages(messages) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const currentMessageIds = new Set();
    messagesContainer.querySelectorAll('.message').forEach(msg => {
        const messageId = msg.getAttribute('data-message-id');
        if (messageId) currentMessageIds.add(messageId);
    });
    
    const serverMessageIds = new Set(messages.map(msg => msg.id.toString()));
    
    currentMessageIds.forEach(messageId => {
        if (!serverMessageIds.has(messageId)) {
            const messageElement = messagesContainer.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                console.log('🗑️ Removing deleted message:', messageId);
                messageElement.remove();
            }
        }
    });
    
    let hasNewMessages = false;
    messages.forEach(msg => {
        if (!currentMessageIds.has(msg.id.toString())) {
            addMessageToContainer(messagesContainer, msg, currentChatUserId);
            hasNewMessages = true;
        }
    });
    
    if (hasNewMessages) {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

function startChatsAutoUpdate() {
    setInterval(() => {
        if (!currentChatUserId) {
            updateChatsList();
        }
    }, 3000);
}

// Вспомогательная функция для обновления списка чатов
function updateChatsList() {
    fetch('/get_chats')
        .then(response => response.json())
        .then(chats => {
            displayChatsList(chats);
        })
        .catch(error => {
            console.error('Error updating chats list:', error);
        });
}