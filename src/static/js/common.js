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

function previewAvatar(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('avatarPreview').src = e.target.result;
            // Auto submit avatar
            const form = new FormData();
            form.append('avatar', input.files[0]);
            form.append('action', 'update_avatar');

            fetch('/admin/profile', {
                method: 'POST',
                body: form
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert(data.message || 'Có lỗi xảy ra khi cập nhật avatar');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Có lỗi xảy ra khi cập nhật avatar');
                });
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Password toggle functions
function setupPasswordToggle(toggleId, inputId) {
    const toggle = document.getElementById(toggleId);
    if (toggle) {
        toggle.addEventListener('click', function () {
            const passwordInput = document.getElementById(inputId);
            const icon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

// Setup password toggles
setupPasswordToggle('toggleCurrentPassword', 'current_password');
setupPasswordToggle('toggleNewPassword', 'new_password');
setupPasswordToggle('toggleConfirmNewPassword', 'confirm_new_password');

// Check password strength (same as register)
function checkPasswordStrength(password) {
    if (!password) return { strength: 'none', text: '', width: '0%', class: '' };

    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;

    if (strength <= 2) {
        return { strength: 'weak', text: 'Mật khẩu yếu', width: '33%', class: 'strength-weak' };
    } else if (strength <= 3) {
        return { strength: 'medium', text: 'Mật khẩu trung bình', width: '66%', class: 'strength-medium' };
    } else {
        return { strength: 'strong', text: 'Mật khẩu mạnh', width: '100%', class: 'strength-strong' };
    }
}

// Update password strength indicator
const newPasswordInput = document.getElementById('new_password');
if (newPasswordInput) {
    newPasswordInput.addEventListener('input', function () {
        const password = this.value;
        const strength = checkPasswordStrength(password);
        const fill = document.getElementById('strengthFill');
        const text = document.getElementById('strengthText');

        if (password) {
            fill.style.width = strength.width;
            fill.className = 'strength-fill ' + strength.class;
            text.textContent = strength.text;
        } else {
            fill.style.width = '0%';
            fill.className = 'strength-fill';
            text.textContent = '';
        }
    });
}

const changePasswordForm = document.getElementById('changePasswordForm');
if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', function (e) {
        const currentPassword = document.getElementById('current_password').value;
        const newPassword = document.getElementById('new_password').value;
        const confirmPassword = document.getElementById('confirm_new_password').value;

        let isValid = true;

        // Validate current password
        if (!currentPassword) {
            document.getElementById('current_password').classList.add('is-invalid');
            document.getElementById('current-password-error').textContent = 'Vui lòng nhập mật khẩu hiện tại';
            isValid = false;
        } else {
            document.getElementById('current_password').classList.remove('is-invalid');
            document.getElementById('current-password-error').textContent = '';
        }

        // Validate new password
        if (!newPassword) {
            document.getElementById('new_password').classList.add('is-invalid');
            document.getElementById('new-password-error').textContent = 'Vui lòng nhập mật khẩu mới';
            isValid = false;
        } else if (newPassword.length < 6) {
            document.getElementById('new_password').classList.add('is-invalid');
            document.getElementById('new-password-error').textContent = 'Mật khẩu phải có ít nhất 6 ký tự';
            isValid = false;
        } else {
            document.getElementById('new_password').classList.remove('is-invalid');
            document.getElementById('new-password-error').textContent = '';
        }

        // Validate confirm password
        if (!confirmPassword) {
            document.getElementById('confirm_new_password').classList.add('is-invalid');
            document.getElementById('confirm-password-error').textContent = 'Vui lòng xác nhận mật khẩu mới';
            isValid = false;
        } else if (newPassword !== confirmPassword) {
            document.getElementById('confirm_new_password').classList.add('is-invalid');
            document.getElementById('confirm-password-error').textContent = 'Mật khẩu xác nhận không khớp';
            isValid = false;
        } else {
            document.getElementById('confirm_new_password').classList.remove('is-invalid');
            document.getElementById('confirm-password-error').textContent = '';
        }

        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = this.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
}