// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/admin/api/current-user');
        const result = await response.json();

        if (!result.success) {
            window.location.href = '/admin/login';
            return;
        }
        else {
            if (result.success && result.data && result.data.role != 'customer') {
                var html = `<a href="/admin/profile">${result.data.name}</a>`;
                $('#userName').html(html);
            }
        }
    } catch (error) {
        console.error('Lỗi kiểm tra đăng nhập:', error);
        window.location.href = '/admin/login';
    }
}
