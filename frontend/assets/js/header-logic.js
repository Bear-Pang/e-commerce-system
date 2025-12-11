document.addEventListener('DOMContentLoaded', () => {
    // 检查组件是否已加载 (防止重复执行)
    if (document.getElementById('user-area')) {
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username'); // 假设登录时会存储 username

        const loginLink = document.getElementById('login-link');
        const registerLink = document.getElementById('register-link');
        const separator = document.getElementById('separator');
        const loggedInUserArea = document.getElementById('logged-in-user');
        const currentUsernameSpan = document.getElementById('current-username');
        const logoutBtn = document.getElementById('header-logout-btn');

        if (token && username) {
            // 已登录状态
            loginLink.classList.add('hidden');
            registerLink.classList.add('hidden');
            separator.classList.add('hidden');
            loggedInUserArea.classList.remove('hidden');
            currentUsernameSpan.textContent = username;
        } else {
            // 未登录状态
            loginLink.classList.remove('hidden');
            registerLink.classList.remove('hidden');
            separator.classList.remove('hidden');
            loggedInUserArea.classList.add('hidden');
        }

        // 退出登录功能
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('确定要退出登录吗？')) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('username');
                    // 刷新页面或跳转到首页/登录页
                    window.location.href = '/public/index.html';
                }
            });
        }

        // 简化的购物车数量加载 (实际应用中应调用 API)
        function loadCartCount() {
            // 这是一个简化的示例，实际应调用 /api/cart/count 接口
            const cartCountElement = document.getElementById('cart-count');
            // 假设从 localStorage 中获取一个模拟数量
            const count = parseInt(localStorage.getItem('cart_count') || '0');
            cartCountElement.textContent = count > 99 ? '99+' : count;
        }
        loadCartCount();
    }
});