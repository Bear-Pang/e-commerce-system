// 全局配置axios，确保请求路径正确
axios.defaults.baseURL = 'http://localhost:3000';

window.onload = function() {
    // 1. 加载头部组件
    axios.get('/components/layout/header.html')
    .then(res => {
        document.getElementById('header').innerHTML = res.data;
    })
    .catch(err => {
        console.log('加载头部失败：', err);
    });

    // 2. 加载底部组件
    axios.get('/components/layout/footer.html')
    .then(res => {
        document.getElementById('footer').innerHTML = res.data;
    })
    .catch(err => {
        console.log('加载底部失败：', err);
    });

    // 3. 获取轮播图数据（关键：路径完全匹配后端接口）
    axios.get('/api/banner/list')
    .then(res => {
        console.log('轮播图数据：', res.data); // 控制台打印数据，方便排查
        if (res.data.code === 200) {
            let html = '';
            res.data.data.forEach(item => {
                html += `<div class="banner-item">${item.title}</div>`;
            });
            document.getElementById('banner-list').innerHTML = html;
        }
    })
    .catch(err => {
        console.log('获取轮播图失败：', err);
    });

    // 4. 获取推荐商品数据
    axios.get('/api/product/recommend')
    .then(res => {
        console.log('商品数据：', res.data); // 控制台打印数据
        if (res.data.code === 200) {
            let html = '';
            res.data.data.forEach(item => {
                html += `
                <div class="product-card">
                    <h4>${item.name}</h4>
                    <div class="price">¥${item.price}</div>
                </div>
                `;
            });
            document.getElementById('product-list').innerHTML = html;
        }
    })
    .catch(err => {
        console.log('获取商品失败：', err);
    });
};