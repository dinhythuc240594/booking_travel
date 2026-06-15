// Check authentication
async function checkAuth() {
    if (window.location.pathname.startsWith('/admin/login')) {
        return;
    }
    try {
        const response = await fetch('/admin/api/current-user');
        const result = await response.json();

        if (!result.success || !result.data || (result.data.role !== 'admin' && result.data.role !== 'staff')) {
            window.location.href = '/admin/login';
            return;
        }

        const html = `<a href="/admin/profile">${result.data.name}</a>`;
        $('#userName').html(html);
    }
    catch (error) {
        console.error('Lỗi kiểm tra đăng nhập:', error);
        window.location.href = '/admin/login';
    }
}

$(document).ready(function () {
    checkAuth();
});