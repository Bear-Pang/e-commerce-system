// list.js - 商品列表页逻辑脚本

// 全局变量用于存储分页信息
let currentPage = 1;
let pageSize = 12; // 每页显示 12 个商品
let currentCategoryId = null;
let currentKeyword = null;

/**
 * 核心：解析 URL 中的查询参数
 */
function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    currentCategoryId = params.get('category_id');
    currentKeyword = params.get('keyword');
    currentPage = parseInt(params.get('page')) || 1;
}

/**
 * 渲染单个商品卡片
 * 沿用首页热门推荐的排版样式，但将其封装为函数
 * @param {object} product - 商品数据对象
 */
function renderProductCard(product) {
    // 假设图片路径与首页逻辑一致
    const productImageUrl = product.main_image || product.image || '/assets/image/product/default.png';
    const defaultImageUrl = '/assets/image/product/default.png';

    // 注意：这里的 product-card-shadow 类需要在 index.html 的 style 标签中或 main.css 中定义
    return `
        <a href="/pages/product/detail.html?id=${product.id}" class="block bg-white rounded-lg overflow-hidden product-card-shadow">
            <img
                src="${productImageUrl}"
                alt="${product.name}"
                class="w-full h-48 object-cover"
                onerror="this.onerror=null;this.src='${defaultImageUrl}'"
            >
            <div class="p-4">
                <h3 class="text-lg font-semibold text-secondary truncate mb-1">${product.name}</h3>
                <p class="text-gray-500 text-sm mb-2">${product.description || '暂无描述'}</p>
                <div class="flex items-end justify-between">
                    <span class="text-primary text-xl font-bold">¥${(product.price || 0).toFixed(2)}</span>
                    <button class="bg-primary text-white text-sm px-3 py-1 rounded-full hover:bg-primary/90 transition-colors">
                        查看详情
                    </button>
                </div>
            </div>
        </a>
    `;
}

/**
 * 获取商品列表数据
 */
function fetchProductList() {
    getQueryParams(); // 每次请求前更新参数

    const container = document.getElementById('product-list-container');
    const loadingEl = document.getElementById('list-loading');
    const errorEl = document.getElementById('list-error');

    if (container) container.innerHTML = '';
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (errorEl) errorEl.classList.add('hidden');

    let apiUrl = utils.getApiUrl(`product/list?page=${currentPage}&size=${pageSize}`);

    if (currentCategoryId) {
        apiUrl += `&category_id=${currentCategoryId}`;
    }
    if (currentKeyword) {
        apiUrl += `&keyword=${encodeURIComponent(currentKeyword)}`;
    }

    // 如果 URL 中包含 promotion=1 参数，则认为是特惠活动页
    if (window.location.search.includes('promotion=1')) {
        apiUrl += `&is_promotion=1`;
        // 可以在这里更新页面标题
        document.querySelector('h1').innerHTML = '<i class="fa fa-tags text-red-500 mr-2"></i> 特惠活动商品';
    }


    axios.get(apiUrl)
        .then(res => {
            if (loadingEl) loadingEl.classList.add('hidden');

            const data = res.data.data;
            const productList = data.list || [];

            if (productList.length > 0) {
                container.innerHTML = productList.map(renderProductCard).join('');
                // 渲染分页组件
                renderPagination(data.page, data.total_pages);
            } else {
                container.innerHTML = '<p class="col-span-full text-center text-gray-500 py-10">抱歉，未找到相关商品。</p>';
                document.getElementById('pagination-container').innerHTML = '';
            }
        })
        .catch(err => {
            if (loadingEl) loadingEl.classList.add('hidden');
            if (errorEl) errorEl.classList.remove('hidden');
            document.getElementById('list-error-msg').textContent = '商品加载失败，请检查网络或后端服务。';
            console.error('商品列表请求失败:', err);
        });
}


/**
 * 渲染分页组件 (此函数需要 utils.js 中的 formatPrice 等通用工具函数)
 * 这是一个简化的分页渲染示例，您可能需要加载 components/common/pagination.html 组件来美化它。
 */
function renderPagination(page, totalPages) {
    const container = document.getElementById('pagination-container');
    if (!container) return;

    let paginationHTML = '';

    // 生成分页链接的函数
    const generateLink = (targetPage) => {
        const url = new URL(window.location.href);
        url.searchParams.set('page', targetPage);
        return url.pathname + url.search;
    };

    // 上一页
    const prevLink = generateLink(page - 1);
    const prevClass = page === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100';
    paginationHTML += `<a href="${prevLink}" class="px-3 py-1 border rounded ${prevClass}">上一页</a>`;

    // 当前页码
    paginationHTML += `<span class="px-4 py-1 border rounded bg-primary text-white mx-2">${page}</span>`;

    // 下一页
    const nextLink = generateLink(page + 1);
    const nextClass = page === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100';
    paginationHTML += `<a href="${nextLink}" class="px-3 py-1 border rounded ${nextClass}">下一页</a>`;

    // 显示总页数
    paginationHTML += `<span class="ml-4 text-gray-600">共 ${totalPages} 页</span>`;

    container.innerHTML = paginationHTML;
}

/**
 * 初始化所有页面逻辑
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ list.html DOM 加载完成');

    // 1. 加载布局组件
    loadComponent('layout/header.html', '#header-container');
    loadComponent('layout/footer.html', '#footer-container');
    loadComponent('layout/sidebar.html', '#sidebar-container'); // 加载侧边栏组件

    // 2. 绑定重试事件
    document.getElementById('list-retry')?.addEventListener('click', fetchProductList);

    // 3. 开始加载数据
    fetchProductList();

    // 确保导航高亮执行
    if (typeof highlightCurrentNav === 'function') {
        highlightCurrentNav();
    }
});

// 将 fetchProductList 暴露给全局，以便侧边栏筛选等组件可以调用它
window.fetchProductList = fetchProductList;