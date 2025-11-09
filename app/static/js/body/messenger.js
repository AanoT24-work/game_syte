let currentChatUserId = null;
let searchTimeout;
let chatUpdateInterval; // Добавляем интервал для автообновления

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
    
    // Закрываем результаты при клике вне поиска
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-box')) {
            const results = document.getElementById('searchResults');
            if (results) results.style.display = 'none';
        }
    });
    
    // Закрываем по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const results = document.getElementById('searchResults');
            if (results) results.style.display = 'none';
        }
    });
}

// Автообновление списка чатов
function startChatsAutoUpdate() {
    // Обновляем каждые 3 секунды
    setInterval(() => {
        if (!currentChatUserId) {
            // Если чат не открыт, просто обновляем список
            updateChatsList();
        }
    }, 3000);
}

// Функция для рендеринга аватарки в HTML - используем тот же путь что в ленте
function renderAvatar(user, element) {
    if (!element) return;
    
    const userId = user.id || user.user_id;
    if (!user || !userId) {
        element.innerHTML = '<span>👤</span>';
        return;
    }
    
    // Очищаем элемент
    element.innerHTML = '';
    
    if (user.avatar && user.avatar !== 'default_avatar.png' && user.avatar !== 'None') {
        // Используем тот же путь что в работающей ленте постов
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
        
        img.onload = function() {
            console.log('✅ Avatar loaded successfully from feed path');
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
    
    // Создаем контейнер для результатов если его нет
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
        
        // Пропускаем если элементы не найдены
        if (!item || !avatar || !username || !status) {
            return;
        }
        
        // Рендерим аватарку - используем id из поиска
        renderAvatar(user, avatar);
        username.textContent = user.username;
        status.textContent = user.has_chat ? '💬 Чат есть' : '➕ Новый чат';
        status.className = `result-chat-status ${user.has_chat ? 'has-chat' : 'new-chat'}`;
        
        // Используем id для старта чата
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

// ОБНОВЛЕНИЕ СПИСКА ЧАТОВ (для автообновления)
function updateChatsList() {
    fetch('/get_chats')
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(chats => {
            updateChatsListUI(chats);
        })
        .catch(error => {
            console.error('Error updating chats:', error);
        });
}

// ОБНОВЛЕНИЕ UI СПИСКА ЧАТОВ БЕЗ ПОЛНОЙ ПЕРЕЗАГРУЗКИ
function updateChatsListUI(chats) {
    const chatsList = document.getElementById('chatsList');
    if (!chatsList) return;
    
    console.log('🔄 Updating chats list UI, chats count:', chats ? chats.length : 0);
    
    // Если нет чатов
    if (!chats || chats.length === 0) {
        // Проверяем, не отображается ли уже сообщение "нет чатов"
        const noChatsElement = chatsList.querySelector('.no-chats');
        if (!noChatsElement) {
            chatsList.innerHTML = `
                <div class="no-chats">
                    <div>💬</div>
                    <div>Чатов пока нет</div>
                    <div>Найдите пользователя чтобы начать общение</div>
                </div>
            `;
        }
        return;
    }

    // Если есть сообщение "нет чатов" - удаляем его
    const noChatsElement = chatsList.querySelector('.no-chats');
    if (noChatsElement) {
        noChatsElement.remove();
    }

    // Создаем карту существующих чатов для быстрого доступа
    const existingChatsMap = new Map();
    const existingChatElements = chatsList.querySelectorAll('.chat-item');
    
    existingChatElements.forEach(chatElement => {
        const userId = chatElement.getAttribute('data-user-id');
        if (userId) {
            existingChatsMap.set(userId, chatElement);
        }
    });

    // Обновляем существующие чаты и добавляем новые
    chats.forEach(chat => {
        const userId = String(chat.id || chat.user_id);
        const existingChat = existingChatsMap.get(userId);
        
        if (existingChat) {
            // Обновляем существующий чат
            updateChatItem(existingChat, chat);
            // Удаляем из карты, чтобы потом знать какие остались
            existingChatsMap.delete(userId);
        } else {
            // Добавляем новый чат
            addChatItem(chatsList, chat);
        }
    });

    // Удаляем чаты которых больше нет (оставшиеся в карте)
    existingChatsMap.forEach((chatElement, userId) => {
        console.log('🗑️ Removing chat for user:', userId);
        chatElement.remove();
    });
}

// ОБНОВЛЕНИЕ ОДНОГО ЭЛЕМЕНТА ЧАТА
function updateChatItem(chatElement, chat) {
    const lastMessage = chatElement.querySelector('.chat-last-message');
    const chatTime = chatElement.querySelector('.chat-time');
    const chatUnread = chatElement.querySelector('.chat-unread');
    
    if (lastMessage) {
        lastMessage.textContent = chat.last_message || 'Нет сообщений';
    }
    
    if (chatTime) {
        chatTime.textContent = formatTime(chat.last_message_time);
    }
    
    if (chatUnread) {
        if (chat.unread_count > 0) {
            chatUnread.textContent = chat.unread_count;
            chatUnread.style.display = 'flex';
        } else {
            chatUnread.style.display = 'none';
        }
    }
}

// ДОБАВЛЕНИЕ НОВОГО ЭЛЕМЕНТА ЧАТА
function addChatItem(container, chat) {
    const template = document.getElementById('chatItemTemplate');
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
    
    // Устанавливаем data-attribute для идентификации
    const userId = chat.id || chat.user_id;
    chatItem.setAttribute('data-user-id', userId);
    
    // Рендерим аватарку
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
    
    // Обработчики событий
    if (userId) {
        chatItem.addEventListener('click', () => openChat(userId));
        
        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                clearChat(userId);
            });
        }
    }
    
    container.appendChild(clone);
}

// ОЧИСТКА УДАЛЕННЫХ ЧАТОВ
function cleanupRemovedChats(container, currentChats) {
    const currentUserIds = new Set(currentChats.map(chat => chat.id || chat.user_id));
    const allChatItems = container.querySelectorAll('.chat-item');
    
    allChatItems.forEach(item => {
        const userId = item.getAttribute('data-user-id');
        if (userId && !currentUserIds.has(userId)) {
            item.remove();
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
        
        // Пропускаем если основные элементы не найдены
        if (!chatItem || !chatAvatar || !chatName) {
            return;
        }
        
        // Устанавливаем data-attribute
        const userId = chat.id || chat.user_id;
        chatItem.setAttribute('data-user-id', userId);
        
        // Рендерим аватарку
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
        
        // Обработчики событий - используем user_id
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
    // Останавливаем предыдущее автообновление
    stopChatAutoUpdate();
    loadChat(userId);
    // Запускаем автообновление для этого чата
    startChatAutoUpdate(userId);
}

// ЗАГРУЗКА КОНКРЕТНОГО ЧАТА
function loadChat(userId) {
    currentChatUserId = userId;
    
    fetch(`/get_messages/${userId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            displayChat(data);
        })
        .catch(error => {
            console.error('Error loading chat:', error);
            alert('Ошибка загрузки чата');
        });
}

// АВТООБНОВЛЕНИЕ ОТКРЫТОГО ЧАТА
function startChatAutoUpdate(userId) {
    // Останавливаем предыдущий интервал
    if (chatUpdateInterval) {
        clearInterval(chatUpdateInterval);
    }
    
    // Запускаем обновление каждые 2 секунды
    chatUpdateInterval = setInterval(() => {
        if (currentChatUserId === userId) {
            updateCurrentChat();
        }
    }, 500);
}

// ОСТАНОВКА АВТООБНОВЛЕНИЯ
function stopChatAutoUpdate() {
    if (chatUpdateInterval) {
        clearInterval(chatUpdateInterval);
        chatUpdateInterval = null;
    }
}

// ОБНОВЛЕНИЕ ТЕКУЩЕГО ЧАТА
function updateCurrentChat() {
    if (!currentChatUserId) return;
    
    fetch(`/get_messages/${currentChatUserId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            updateChatMessages(data.messages);
            // Также обновляем список чатов
            updateChatsList();
        })
        .catch(error => {
            console.error('Error updating chat:', error);
        });
}

// ОБНОВЛЕНИЕ СООБЩЕНИЙ В ЧАТЕ
function updateChatMessages(messages) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    // Получаем ID текущих сообщений
    const currentMessageIds = new Set();
    messagesContainer.querySelectorAll('.message').forEach(msg => {
        const messageId = msg.getAttribute('data-message-id');
        if (messageId) currentMessageIds.add(messageId);
    });
    
    // Получаем ID сообщений с сервера
    const serverMessageIds = new Set(messages.map(msg => msg.id.toString()));
    
    // УДАЛЯЕМ сообщения которых нет на сервере
    currentMessageIds.forEach(messageId => {
        if (!serverMessageIds.has(messageId)) {
            const messageElement = messagesContainer.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                console.log('🗑️ Removing deleted message:', messageId);
                messageElement.remove();
            }
        }
    });
    
    // Добавляем только новые сообщения
    let hasNewMessages = false;
    messages.forEach(msg => {
        if (!currentMessageIds.has(msg.id.toString())) {
            addMessageToContainer(messagesContainer, msg, currentChatUserId);
            hasNewMessages = true;
        }
    });
    
    // Прокручиваем вниз если есть новые сообщения
    if (hasNewMessages) {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

function displayChat(chatData) {
    const messContainer = document.getElementById('messContainer');
    const template = document.getElementById('chatWindowTemplate');
    
    if (!messContainer || !template) return;
    
    messContainer.innerHTML = '';
    const clone = template.content.cloneNode(true);
    
    // Заполняем заголовок чата
    const avatar = clone.getElementById('chatHeaderAvatar');
    const name = clone.getElementById('chatHeaderName');
    const clearBtn = clone.getElementById('clearChatBtn');
    const messagesContainer = clone.getElementById('chatMessages');
    const chatInput = clone.getElementById('chatInput');
    const sendBtn = clone.getElementById('sendMessageBtn');
    
    if (!avatar || !name || !messagesContainer) return;
    
    // Рендерим аватарку в заголовке чата
    renderAvatar(chatData.user, avatar);
    name.textContent = chatData.user.username;
    
    // Добавляем сообщения
    if (chatData.messages && chatData.messages.length > 0) {
        chatData.messages.forEach(msg => {
            addMessageToContainer(messagesContainer, msg, chatData.user.id || chatData.user.user_id);
        });
    }
    
    // Обработчики событий
    const userId = chatData.user.id || chatData.user.user_id;
    if (clearBtn && userId) {
        clearBtn.addEventListener('click', () => clearChat(userId));
    }
    
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    messContainer.appendChild(clone);
    
    // Прокручиваем вниз
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
    
    // Фокус на поле ввода
    if (chatInput) {
        chatInput.focus();
    }
}

function addMessageToContainer(container, msg, chatUserId) {
    const template = document.getElementById('messageTemplate');
    if (!template) return;
    
    const clone = template.content.cloneNode(true);
    
    const messageEl = clone.querySelector('.message');
    const contentEl = clone.querySelector('.message-content');
    const textEl = clone.querySelector('.message-text');
    const timeEl = clone.querySelector('.message-time');
    const deleteBtn = clone.querySelector('.message-delete-btn');
    
    if (!messageEl || !textEl) return;
    
    // Устанавливаем ID сообщения для отслеживания
    messageEl.setAttribute('data-message-id', msg.id);
    
    // Определяем класс сообщения (входящее/исходящее)
    const isIncoming = msg.sender_id === chatUserId;
    messageEl.classList.add(isIncoming ? 'message-in' : 'message-out');
    
    // Содержимое сообщения
    textEl.textContent = msg.text;
    
    // Кнопка удаления только для исходящих сообщений
    if (deleteBtn) {
        if (isIncoming) {
            deleteBtn.style.display = 'none';
        } else {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteMessage(msg.id);
            });
        }
    }
    
    // Время сообщения
    if (timeEl) {
        timeEl.textContent = formatTime(msg.created_at);
    }
    
    container.appendChild(clone);
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

// ОЧИСТКА ЧАТА
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

// ОТПРАВКА СООБЩЕНИЯ
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
            // Вместо полной перезагрузки просто обновляем чат
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
}

// СТАРТ ЧАТА
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

// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
function formatTime(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
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