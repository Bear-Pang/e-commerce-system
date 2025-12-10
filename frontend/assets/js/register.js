document.addEventListener('DOMContentLoaded', () => {
    // 修复1：使用正确的 ID 'register-form'
    const registerForm = document.getElementById('register-form');
    // 修复2：使用正确的 ID 'message-container' 和 'message-text' (与美化后的 HTML 对应)
    const messageContainer = document.getElementById('message-container');
    const messageText = document.getElementById('message-text');

    // 假设 component-loader.js 里的 loadComponent 函数已定义
    try {
        loadComponent('layout/header.html', '#header-container');
        loadComponent('layout/footer.html', '#footer-container');
    } catch (e) {
        console.log('加载头部/底部失败，不影响注册：', e);
    }

    /**
     * 显示提示信息
     * @param {string} msg 提示内容
     * @param {string} type 提示类型 (success/danger)
     */
    function showMessage(msg, type) {
        // 使用 register.html 中 Tailwind 样式对应的 ID
        messageText.textContent = msg;
        messageContainer.classList.remove('hidden');

        // 移除旧的颜色类，添加新的颜色类 (兼容 Tailwind 样式)
        messageContainer.classList.remove('bg-red-100', 'text-red-700', 'bg-green-100', 'text-green-700', 'border', 'border-red-400', 'rounded', 'px-4', 'py-3', 'border-green-400');

        if (type === 'danger') {
            messageContainer.classList.add('bg-red-100', 'text-red-700', 'border', 'border-red-400', 'rounded', 'px-4', 'py-3');
        } else if (type === 'success') {
            messageContainer.classList.add('bg-green-100', 'text-green-700', 'border', 'border-green-400', 'rounded', 'px-4', 'py-3');
        }

        // 错误信息自动隐藏
        if (type === 'danger') {
            setTimeout(() => {
                messageContainer.classList.add('hidden');
            }, 5000);
        }
    }

    // 注册表单提交
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            // 修复3：使用正确的 ID 'confirm-password'
            const confirmPassword = document.getElementById('confirm-password').value.trim();

            // 客户端校验：密码一致性
            if (password !== confirmPassword) {
                showMessage('两次输入的密码不一致！', 'danger');
                return;
            }

            // 客户端校验：长度
            if (username.length < 4 || password.length < 6) {
                showMessage('用户名至少4位，密码至少6位！', 'danger');
                return;
            }

            try {
                console.log('开始请求注册接口，参数：', {username, password});

                // 使用 axios 发送 POST 请求 (与 login.html 保持一致)
                const res = await axios.post('http://127.0.0.1:3000/api/user/register', {
                    username: username,
                    password: password
                });

                const result = res.data || res;
                console.log('接口返回结果：', result);

                // 检查后端是否返回 Token (实现自动登录)
                if (result.code === 200 && result.data && result.data.token) {
                    localStorage.setItem('token', result.data.token);
                    showMessage('注册成功，正在跳转到首页...', 'success');

                    // 2秒后跳转到首页
                    setTimeout(() => {
                        window.location.href = 'http://127.0.0.1:3000/';
                    }, 2000);

                } else {
                    // 如果后端未返回 Token，但注册成功（旧逻辑），则跳转到登录页
                    if (result.code === 200) {
                        showMessage(result.msg + '，即将跳转到登录页...', 'success');
                        setTimeout(() => {
                            window.location.href = '/pages/user/login.html';
                        }, 2000);
                    } else {
                        showMessage('注册失败：' + (result.msg || '未知错误'), 'danger');
                    }
                }
            } catch (err) {
                console.error('注册请求详细错误：', err);

                if (err.response) {
                    // 后端返回的错误（如 409 用户名已存在）
                    showMessage('注册失败：' + (err.response.data?.msg || '服务器返回错误'), 'danger');
                } else if (err.message && err.message.includes('Network Error')) {
                    showMessage('网络错误！请检查后端服务是否启动。', 'danger');
                } else {
                    showMessage('请求失败：' + err.message, 'danger');
                }
            }
        });
    } else {
        console.error("错误：未找到 ID 为 'register-form' 的表单元素，请检查 HTML ID 是否为 'register-form'。");
    }
});