/**
 * =========================================
 * /assets/js/profile.js - 个人中心逻辑
 * 依赖: utils.js (用于 API URL, Token 管理, 校验)
 * =========================================
 */
document.addEventListener('DOMContentLoaded', () => {
    // 页面元素 ID
    const usernameElement = document.getElementById('profile-username');
    const phoneElement = document.getElementById('profile-phone');
    const editPhoneBtn = document.getElementById('edit-phone-btn');
    const phoneForm = document.getElementById('phone-form');
    const cancelPhoneBtn = document.getElementById('cancel-phone-btn');
    const newPhoneInput = document.getElementById('new-phone');
    const passwordForm = document.getElementById('password-form');
    const logoutBtn = document.getElementById('logout-btn');

    // 提示信息元素
    const messageContainer = document.getElementById('message-container');
    const messageText = document.getElementById('message-text');

    // 绝对路径常量
    const LOGIN_URL = '/pages/user/login.html';

    // 确保头部事件被绑定（如果 initHeaderEvents 在 profile.html 底部定义）
    if (typeof initHeaderEvents === 'function') {
        initHeaderEvents();
    }

    // 假设 utils.js 已通过 <script> 标签加载并挂载到 window.utils
    const utils = window.utils || {};

    /**
     * 显示提示信息
     * @param {string} msg 提示内容
     * @param {string} type 提示类型 (success/danger)
     */
    function showMessage(msg, type) {
        messageText.textContent = msg;
        messageContainer.classList.remove('hidden');

        // 重置样式
        messageContainer.className = 'mb-4 py-3 px-4 border rounded-md';

        if (type === 'danger') {
            messageContainer.classList.add('bg-red-100', 'text-red-700', 'border-red-400');
        } else if (type === 'success') {
            messageContainer.classList.add('bg-green-100', 'text-green-700', 'border-green-400');
        }

        // 自动隐藏
        setTimeout(() => {
            messageContainer.classList.add('hidden');
        }, 5000);
    }

    /**
     * 处理认证失败，清空 Token 并跳转
     */
    function handleAuthFailure() {
        if (utils.removeToken) utils.removeToken();
        setTimeout(() => {
            window.location.href = LOGIN_URL;
        }, 1000);
    }

    /**
     * 检查用户是否登录，并获取用户信息
     */
    async function loadUserProfile() {
        // 使用 utils.getToken() 获取 Token
        const token = utils.getToken ? utils.getToken() : localStorage.getItem('token');

        if (!token) {
            alert('请先登录！');
            window.location.href = LOGIN_URL;
            return;
        }

        try {
            // 使用 utils.getApiUrl() 和 utils.getAuthHeaders()
            const apiUrl = utils.getApiUrl ? utils.getApiUrl('user/info') : 'http://127.0.0.1:3000/api/user/info';
            const headers = utils.getAuthHeaders ? utils.getAuthHeaders() : { 'Authorization': token };

            const res = await axios.get(apiUrl, { headers });

            const user = res.data.data;
            if (res.data.code === 200 && user) {
                usernameElement.textContent = user.username;
                phoneElement.textContent = user.phone || '未设置';
                // 预填手机号到修改表单中
                newPhoneInput.value = user.phone === '未设置' ? '' : user.phone;
            } else {
                showMessage(res.data.msg || '获取用户信息失败', 'danger');
                // 如果 Token 无效，强制跳转登录页
                if (res.data.code === 401) {
                    handleAuthFailure();
                }
            }
        } catch (err) {
            console.error('获取用户信息请求失败：', err);
            showMessage('网络错误，无法获取用户信息。', 'danger');

            // 假设请求失败也可能是 Token 问题
            if (err.response && err.response.status === 401) {
                handleAuthFailure();
            }
        }
    }

    // --- 事件监听器 ---

    // 1. 切换手机号修改表单
    editPhoneBtn.addEventListener('click', () => {
        phoneForm.classList.toggle('hidden');
        // 使用 font-awesome 图标切换
        editPhoneBtn.innerHTML = phoneForm.classList.contains('hidden')
            ? '<i class="fa fa-pencil"></i> 修改'
            : '<i class="fa fa-angle-up"></i> 收起';
    });

    cancelPhoneBtn.addEventListener('click', () => {
        phoneForm.classList.add('hidden');
        editPhoneBtn.innerHTML = '<i class="fa fa-pencil"></i> 修改';
        loadUserProfile(); // 取消时重新加载以重置输入框
    });

    // 2. 手机号修改提交
    phoneForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const newPhone = newPhoneInput.value.trim();
        const authHeaders = utils.getAuthHeaders ? utils.getAuthHeaders() : { 'Authorization': utils.getToken() };
        const updateUrl = utils.getApiUrl ? utils.getApiUrl('user/update') : 'http://127.0.0.1:3000/api/user/update';

        // 使用 utils.isValidPhone() 校验
        if (utils.isValidPhone && !utils.isValidPhone(newPhone)) {
            showMessage('手机号格式不正确（10或11位数字）', 'danger');
            return;
        } else if (!utils.isValidPhone && newPhone && !/^\d{10,11}$/.test(newPhone)) {
            // 兼容 utils.js 未提供该函数的情况
            showMessage('手机号格式不正确（10或11位数字）', 'danger');
            return;
        }

        // 确保是修改了内容才提交
        if (newPhone === phoneElement.textContent || (newPhone === '' && phoneElement.textContent === '未设置')) {
            showMessage('手机号未发生变化', 'danger');
            return;
        }

        try {
            const res = await axios.post(updateUrl,
                { phone: newPhone },
                { headers: authHeaders }
            );

            if (res.data.code === 200) {
                showMessage(res.data.msg || '手机号更新成功！', 'success');
                phoneForm.classList.add('hidden');
                editPhoneBtn.innerHTML = '<i class="fa fa-pencil"></i> 修改';
                loadUserProfile(); // 刷新用户信息
            } else {
                showMessage('手机号更新失败: ' + (res.data.msg || '未知错误'), 'danger');
            }
        } catch (err) {
            console.error('手机号更新请求失败：', err);
            showMessage('网络请求失败，请稍后再试。', 'danger');
        }
    });

    // 3. 密码修改提交
    passwordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const newPassword = document.getElementById('new-password').value.trim();
        const confirmNewPassword = document.getElementById('confirm-new-password').value.trim();

        const submitBtn = passwordForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        const updateUrl = utils.getApiUrl ? utils.getApiUrl('user/update') : 'http://127.0.0.1:3000/api/user/update';
        const authHeaders = utils.getAuthHeaders ? utils.getAuthHeaders() : { 'Authorization': utils.getToken() };


        // 使用 utils.isValidPassword() 校验
        if (utils.isValidPassword && !utils.isValidPassword(newPassword)) {
            showMessage('新密码长度必须至少为6位', 'danger');
            submitBtn.disabled = false;
            return;
        } else if (!utils.isValidPassword && newPassword.length < 6) {
            // 兼容 utils.js 未提供该函数的情况
            showMessage('新密码长度必须至少为6位', 'danger');
            submitBtn.disabled = false;
            return;
        }

        if (newPassword !== confirmNewPassword) {
            showMessage('两次输入的新密码不一致！', 'danger');
            submitBtn.disabled = false;
            return;
        }

        try {
            const res = await axios.post(updateUrl,
                { password: newPassword },
                { headers: authHeaders }
            );

            if (res.data.code === 200) {
                // 如果密码修改成功，更新本地 Token (如果后端返回了新的)
                if (res.data.data && res.data.data.token && utils.setToken) {
                    utils.setToken(res.data.data.token);
                }

                showMessage(res.data.msg + '，请重新登录确保安全！', 'success');
                passwordForm.reset(); // 清空表单
                submitBtn.disabled = false;

                // 提示后强制跳转到登录页，让用户使用新密码登录
                setTimeout(() => {
                    handleAuthFailure(); // 清除旧 Token，跳转到登录
                }, 3000);

            } else {
                showMessage('密码更新失败: ' + (res.data.msg || '未知错误'), 'danger');
                submitBtn.disabled = false;
            }
        } catch (err) {
            console.error('密码更新请求失败：', err);
            showMessage('网络请求失败，请稍后再试。', 'danger');
            submitBtn.disabled = false;
        }
    });

    // 4. 退出登录
    logoutBtn.addEventListener('click', () => {
        if (confirm('确定要退出登录吗？')) {
            showMessage('已成功退出登录，正在跳转...', 'success');
            handleAuthFailure(); // 清除 Token，跳转到登录
        }
    });


    // 页面加载时执行
    loadUserProfile();
});