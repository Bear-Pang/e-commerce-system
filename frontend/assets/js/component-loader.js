// DbProject/assets/js/component-loader.js
/**
 * 极简版组件加载：直接请求组件路径（无前缀）
 */
function loadComponent(componentPath, targetSelector, callback) {
  // 组件路径直接是 /components/xxx（后端能访问）
  const fullPath = `/components/${componentPath}`;
  fetch(fullPath)
    .then(res => {
      if (!res.ok) throw new Error(`404：组件路径${fullPath}不存在`);
      return res.text();
    })
    .then(html => {
      const target = document.querySelector(targetSelector);
      target && (target.innerHTML = html);
      callback && callback();
    })
    .catch(err => {
      console.error('组件加载失败：', err.message);
      const target = document.querySelector(targetSelector);
      target && (target.innerHTML = `<div style="color:red;">组件加载失败</div>`);
    });
}

/**
 * 全局axios：修复GET请求params参数传递错误（核心修复）
 */
if (!window.axios) {
  window.axios = {
    // 修复GET请求：正确拼接params到URL，移除fetch不支持的params属性
    get: function(url, options = {}) {
      const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      };
      // 拼接GET参数到URL（fetch无params配置项，需手动拼接）
      let fullUrl = url;
      if (options.params && Object.keys(options.params).length > 0) {
        const params = new URLSearchParams(options.params);
        fullUrl += `?${params.toString()}`;
      }
      // 发起GET请求（仅保留合法的method/headers）
      return fetch(fullUrl, {
        method: 'GET',
        headers: headers
      }).then(res => res.json());
    },
    // POST请求保留原有逻辑（无错误）
    post: function(url, data = {}, options = {}) {
      const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      };
      return fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data)
      }).then(res => res.json());
    }
  };
}

// 分页和兜底函数保留（无修改）
if (!window.renderPagination) {
  window.renderPagination = function() {
    const container = document.getElementById('page-numbers');
    if (!container || !window.pagination) return;
    const { page, totalPages } = window.pagination;
    container.innerHTML = '';
    container.innerHTML += `<button class="px-3 py-1 border rounded ${page === 1 ? 'bg-primary text-white' : ''}" onclick="changePage(1)">1</button>`;
    if (totalPages > 5 && page > 3) container.innerHTML += `<span class="px-3 py-1">...</span>`;
    if (page > 1 && page < totalPages) container.innerHTML += `<button class="px-3 py-1 border rounded bg-primary text-white" onclick="changePage(${page})">${page}</button>`;
    if (totalPages > 1 && page !== totalPages) container.innerHTML += `<button class="px-3 py-1 border rounded ${page === totalPages ? 'bg-primary text-white' : ''}" onclick="changePage(${totalPages})">${totalPages}</button>`;
  };
}
window.imgErrorFallback = function(imgElement, fallbackUrl = '/assets/image/banner/banner-default.png') {
  imgElement.src = fallbackUrl;
  imgElement.style.objectFit = 'cover';
};