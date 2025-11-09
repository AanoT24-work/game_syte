console.log('🔄 infinite-scroll-fixed.js loaded');

class InfiniteScroll {
    constructor() {
        console.log('🎯 InfiniteScroll constructor called');
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMorePosts = true;
        this.postsContainer = document.getElementById('posts-container');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.noMorePosts = document.getElementById('no-more-posts');
        
        if (!this.postsContainer) {
            console.error('❌ posts-container not found');
            return;
        }
        
        this.init();
    }
    
    init() {
        console.log('🚀 InfiniteScroll initialized');
        this.initializeLikeHandlers();
        window.addEventListener('scroll', this.checkScroll.bind(this));
    }
    
    checkScroll() {
        if (this.isLoading || !this.hasMorePosts) return;
        
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        if (scrollTop + windowHeight >= documentHeight - 500) {
            this.loadMorePosts();
        }
    }
    
    async loadMorePosts() {
        if (this.isLoading || !this.hasMorePosts) return;
        
        this.isLoading = true;
        this.currentPage++;
        
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }
        
        try {
            const response = await fetch(`/posts?page=${this.currentPage}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            
            if (data.posts && data.posts.length > 0) {
                data.posts.forEach(post => {
                    const postElement = this.createPostElement(post);
                    this.postsContainer.appendChild(postElement);
                });
                this.hasMorePosts = data.has_next;
            } else {
                this.hasMorePosts = false;
            }
            
        } catch (error) {
            console.error('Ошибка загрузки постов:', error);
            this.hasMorePosts = false;
        } finally {
            this.isLoading = false;
            if (this.loadingIndicator) {
                this.loadingIndicator.style.display = 'none';
            }
            if (!this.hasMorePosts && this.noMorePosts) {
                this.noMorePosts.style.display = 'block';
            }
        }
    }
    
    createPostElement(post) {
        const postDiv = document.createElement('div');
        postDiv.className = 'publick-item';
        postDiv.setAttribute('data-post-id', post.id);
        
        const imageHtml = post.image ? `
            <div class="publick-image-container">
                <img src="/post/image/${post.id}" alt="Изображение поста" class="publick-image" loading="lazy">
            </div>
        ` : '';
        
        const avatarHtml = post.user.avatar && post.user.avatar !== 'default_avatar.png' ? 
            `<img src="/avatar/${post.user.id}" alt="Аватар">` : 
            `<span>👤</span>`;
        
        const isLiked = post.user_has_liked || false;
        const likeClass = isLiked ? 'liked' : '';
        const disabledAttr = !post.user_has_liked && !post.user ? 'disabled title="Войдите чтобы лайкать"' : '';
        
        postDiv.innerHTML = `
            <div class="publick-info">
                <div class="publick-avatar">${avatarHtml}</div>
                <a href="/user/${post.user.id}" class="publick-author">Username: ${this.escapeHtml(post.user.login)}</a>
            </div>
            ${imageHtml}
            <p class="publick-content">${this.escapeHtml(post.content)}</p>
            <div class="publick-meta">
                <small class="publick-date">${post.created_at}</small>
                <div class="like-comm-container">
                    <div class="like-wrapper">
                        <button class="like-btn ${likeClass}" data-post-id="${post.id}" ${disabledAttr}>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 18" class="icon favorite">
                                <path d="M14.44 0C12.63 0 11.01 0.88 10 2.23C9.48413 1.53881 8.81426 0.977391 8.04353 0.590295C7.27281 0.203198 6.42247 0.00108555 5.56 0C2.49 0 0 2.5 0 5.59C0 6.78 0.19 7.88 0.52 8.9C2.1 13.9 6.97 16.89 9.38 17.71C9.72 17.83 10.28 17.83 10.62 17.71C13.03 16.89 17.9 13.9 19.48 8.9C19.81 7.88 20 6.78 20 5.59C20 2.5 17.51 0 14.44 0Z"></path>
                            </svg>
                            <span class="like-count" id="like-count-${post.id}">${post.likes_count}</span>
                        </button>
                    </div>
                    <a href="/post/${post.id}" class="link">
                        <span class="link-icon">💬</span>
                    </a>
                </div>
            </div>
        `;
        
        return postDiv;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    initializeLikeHandlers() {
        console.log('🎯 Initializing like handlers');
        
        // Обработчик для всех лайков на странице
        document.addEventListener('click', (e) => {
            const likeBtn = e.target.closest('.like-btn');
            if (likeBtn && likeBtn.dataset.postId) {
                console.log('❤️ Like button clicked:', likeBtn.dataset.postId);
                e.preventDefault();
                e.stopPropagation();
                this.handleLikeClick(likeBtn);
            }
        });
        
        // Обработчик для динамически загруженных постов
        this.postsContainer.addEventListener('click', (e) => {
            const likeBtn = e.target.closest('.like-btn');
            if (likeBtn && likeBtn.dataset.postId) {
                console.log('❤️ Like button clicked (dynamic):', likeBtn.dataset.postId);
                e.preventDefault();
                e.stopPropagation();
                this.handleLikeClick(likeBtn);
            }
        });
    }
    
    async handleLikeClick(likeBtn) {
        const postId = likeBtn.dataset.postId;
        console.log('🔄 Handling like for post:', postId);
        
        const likeCount = document.getElementById(`like-count-${postId}`);
        
        if (!likeCount) {
            console.error('❌ Like count element not found for post:', postId);
            return;
        }
        
        // Проверяем авторизацию
        if (likeBtn.disabled) {
            console.log('⚠️ User not authenticated');
            alert('Войдите в систему чтобы ставить лайки');
            return;
        }
        
        const wasLiked = likeBtn.classList.contains('liked');
        const currentCount = parseInt(likeCount.textContent) || 0;
        
        console.log('📊 Current state:', { wasLiked, currentCount });
        
        // Визуальное обновление
        likeBtn.classList.toggle('liked');
        likeCount.textContent = wasLiked ? currentCount - 1 : currentCount + 1;
        
        try {
            console.log('📡 Sending like request...');
            const response = await fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            console.log('📨 Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Server response DATA:', data);
            
            if (data.success) {
                // Принудительно обновляем счетчик
                const newCount = data.likes_count;
                console.log('📈 New likes count from server:', newCount);
                
                // Если сервер вернул 0, но мы знаем что должен быть минимум 1
                if (newCount === 0 && data.liked) {
                    console.log('⚠️ Server returned 0 but liked is true, forcing count to 1');
                    likeCount.textContent = 1;
                } else {
                    likeCount.textContent = newCount;
                }
                
                // Принудительно обновим класс based на серверном состоянии
                if (data.liked) {
                    likeBtn.classList.add('liked');
                } else {
                    likeBtn.classList.remove('liked');
                }
                
                console.log('🎉 Like successful, final count:', likeCount.textContent, 'liked:', data.liked);
            } else {
                console.error('❌ Server returned error:', data.error);
                throw new Error(data.error || 'Server error');
            }
            
        } catch (error) {
            console.error('💥 Like error:', error);
            // Откатываем визуальные изменения
            likeBtn.classList.toggle('liked');
            likeCount.textContent = currentCount;
            alert('Ошибка при обновлении лайка: ' + error.message);
        }
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM fully loaded');
    if (document.getElementById('posts-container')) {
        console.log('🎯 Starting InfiniteScroll...');
        new InfiniteScroll();
    } else {
        console.log('⏸️ No posts-container found, skipping InfiniteScroll');
    }
});

// Также инициализируем если DOM уже загружен
if (document.readyState === 'loading') {
    console.log('📄 Document still loading...');
} else {
    console.log('📄 Document already ready');
    if (document.getElementById('posts-container')) {
        console.log('🎯 Starting InfiniteScroll immediately...');
        new InfiniteScroll();
    }
}