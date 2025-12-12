/**
 * =========================================
 * /assets/js/utils.js - 通用工具函数库 (最终修复版本)
 * =========================================
 */

// 1. API 配置
const API_BASE_URL = 'http://127.0.0.1:3000/api';

/**
 * 获取完整的 API URL
 * @param {string} endpoint - API 路径，例如 '/user/info'
 * @returns {string} 完整的 URL
 */
function getApiUrl(endpoint) {
    if (endpoint.startsWith('/')) {
        endpoint = endpoint.substring(1);
    }
    return `${API_BASE_URL}/${endpoint}`;
}

// 2. Token (认证) 管理
const TOKEN_KEY = 'token';

/**
 * 获取存储的认证 Token
 * @returns {string | null} Token 字符串或 null
 */
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * 设置认证 Token
 * @param {string} token - 要存储的 Token 字符串
 */
function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * 移除认证 Token (用于退出登录)
 */
function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * 获取包含认证 Token 的请求头对象
 * @returns {{Authorization: string}} headers 对象
 */
function getAuthHeaders() {
    const token = getToken();
    // 假设后端需要 "Bearer token_string" 格式
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}


// 3. 通用校验函数

/**
 * 校验手机号格式 (10或11位数字)
 * @param {string} phone - 手机号码
 * @returns {boolean}
 */
function isValidPhone(phone) {
    // 允许空字符串（表示未设置），或者符合10-11位数字
    if (phone === '') return true;
    return /^\d{10,11}$/.test(phone);
}

/**
 * 校验密码长度 (至少6位)
 * @param {string} password - 密码
 * @returns {boolean}
 */
function isValidPassword(password) {
    return password && password.length >= 6;
}


// 4. 辅助函数 - 价格格式化
/**
 * 格式化价格，保留两位小数
 * @param {number} price - 原始价格
 * @returns {string} 格式化后的价格字符串
 */
function formatPrice(price) {
    if (typeof price !== 'number') return '0.00';
    return price.toFixed(2);
}


// 导出工具函数，使其可以在其他脚本中调用
window.utils = {
    API_BASE_URL,
    getApiUrl,
    getToken,
    setToken,
    removeToken,
    getAuthHeaders,
    isValidPhone,
    isValidPassword,
    formatPrice
};


// =========================================
// 新增/修复：导航栏和搜索相关的前端交互逻辑
// =========================================

/**
 * 导航栏动态高亮逻辑：根据当前 URL 设置导航栏 active 状态
 * 【修复】：修正了 URL 匹配逻辑，确保带参数的页面也能正确高亮。
 */
function highlightCurrentNav() {
    // 获取当前完整的 URL (包含 pathname 和 search)
    const currentFullUrl = window.location.pathname + window.location.search;
    // 获取当前页面路径名 (e.g., /pages/product/list.html)
    const currentPathname = window.location.pathname;

    const navLinks = document.querySelectorAll('#main-nav a');

    navLinks.forEach(link => {
        link.classList.remove('active'); // 1. 移除所有 active 类

        const linkHref = link.getAttribute('href');

        // 1. 匹配 "特惠活动" (精确匹配 full URL 中的 promotion=1)
        if (linkHref.includes('promotion=1') && currentFullUrl.includes('promotion=1')) {
            link.classList.add('active');
        }
            // 2. 匹配 "全部商品" (匹配 list.html 页面，但排除特惠活动)
        // 如果当前路径是 list.html 并且 URL 中不包含 promotion=1，则高亮
        else if (linkHref.endsWith('list.html') &&
            currentPathname.endsWith('list.html') &&
            !currentFullUrl.includes('promotion=1')) {
            link.classList.add('active');
        }
        // 3. 匹配 "关于我们" (匹配 detail.html 页面，假设这是唯一的 detail.html 页面)
        else if (linkHref.endsWith('detail.html') &&
            currentPathname.endsWith('detail.html')) {
            link.classList.add('active');
        }
        // 4. 匹配 "首页" (匹配 index.html，包括根路径 /)
        else if (linkHref.includes('index.html') &&
            (currentPathname.endsWith('index.html') || currentPathname === '/')) {
            link.classList.add('active');
        }
    });
}

/**
 * 商品搜索逻辑：根据搜索框内容跳转到商品列表页
 */
function searchProduct() {
    const keyword = document.getElementById('search-input').value;
    if (keyword) {
        window.location.href = `/pages/product/list.html?keyword=${encodeURIComponent(keyword)}`;
    }
}

// 确保在 DOM 加载完成后调用 highlightCurrentNav 函数
document.addEventListener('DOMContentLoaded', highlightCurrentNav);

// 将新的全局函数挂载到 window 对象，确保 header.html 中的 onclick 可以调用
window.highlightCurrentNav = highlightCurrentNav;
window.searchProduct = searchProduct;