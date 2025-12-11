/**
 * =========================================
 * /assets/js/utils.js - 通用工具函数库
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
    return token ? { 'Authorization': token } : {};
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


// 导出工具函数，使其可以在其他脚本中调用 (例如 profile.js)
// 假设这是通过全局变量实现的，因为您的项目中直接使用了函数名
// 如果项目使用模块化 (import/export)，则需要修改导出方式
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

// 或者直接将函数挂载到 window 对象 (在非模块化老项目中常见)
// window.getApiUrl = getApiUrl;
// window.getToken = getToken;
// window.setToken = setToken;
// window.removeToken = removeToken;
// window.getAuthHeaders = getAuthHeaders;
// window.isValidPhone = isValidPhone;
// window.isValidPassword = isValidPassword;
// window.formatPrice = formatPrice;