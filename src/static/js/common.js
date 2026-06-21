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

// Upload image
async function uploadArticleImage(file, type_data = null, id = null) {
    const formData = new FormData();
    formData.append('image', file);
    if (type_data != null) {
        formData.append('type_data', type_data);
    }
    if (id != null) {
        formData.append('id', id);
    }

    try {
        const response = await fetch('/admin/api/upload-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // Update thumbnail input with URL
            $('#articleImageUrl').val(result.url);
            showToast('Thành công', 'Upload ảnh thành công', 'success');
            return result.url;
        } else {
            showToast('Lỗi', result.error || 'Upload ảnh thất bại', 'warning');
            return null;
        }
    } catch (error) {
        console.error('Lỗi upload ảnh:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi upload ảnh', 'warning');
        return null;
    }
}


// Generate slug from text
function slugify(text) {
    if (!text) return '';
    
    // Map Vietnamese characters
    const from = "àáäâãèéëêìíïîòóöôõùúüûñçăắằẳẵặâấầẩẫậđèéẹẻẽêếềểễệìíịỉĩòóọỏõôốồổỗộơớờởỡợùúụủũưứừửữựỳýỵỷỹ";
    const to = "aaaaaeeeeiiiioooooouuuuncaaaaaaaaaaaadeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyy";
    
    let slug = text.toLowerCase();
    
    for (let i = 0; i < from.length; i++) {
        slug = slug.replace(new RegExp(from[i], 'g'), to[i]);
    }
    
    // Convert đ/Đ to d
    slug = slug.replace(/đ/g, 'd');
    
    slug = slug.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
               .replace(/\s+/g, '-')       // collapse whitespace and replace by -
               .replace(/-+/g, '-')        // collapse dashes
               .replace(/^-+/, '')         // trim - from start of text
               .replace(/-+$/, '');        // trim - from end of text
    
    return slug;
}


$(document).ready(function () {
    checkAuth();
});