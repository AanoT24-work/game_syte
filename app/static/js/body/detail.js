document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        const likeBtn = event.target.closest('.like-btn');
        if (likeBtn && likeBtn.dataset.postId) {
            event.preventDefault();
            const postId = parseInt(likeBtn.dataset.postId);
            toggleLike(postId, likeBtn);
        }
    });
    
    async function toggleLike(postId, likeBtn) {
        const likeCount = document.getElementById(`like-count-${postId}`);
        
        if (!likeBtn || !likeCount) return;
        
        const wasLiked = likeBtn.classList.contains('liked');
        const previousCount = parseInt(likeCount.textContent) || 0;
        
        // Меняем визуальное состояние
        likeBtn.classList.toggle('liked');
        likeCount.textContent = wasLiked ? previousCount - 1 : previousCount + 1;
        
        try {
            const response = await fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    likeCount.textContent = data.likes_count;
                } else {
                    // Откатываем если ошибка
                    likeBtn.classList.toggle('liked');
                    likeCount.textContent = previousCount;
                }
            }
        } catch (error) {
            console.error('Error:', error);
            // Откатываем при ошибке сети
            likeBtn.classList.toggle('liked');
            likeCount.textContent = previousCount;
        }
    }
});