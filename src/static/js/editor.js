const loadedSections = new Set();

function markSectionLoaded(section) {
    if (section) {
        loadedSections.add(section);
    }
}

$(document).ready(function () {

    // // Check authentication
    // checkAuth();

    // Initialize Summernote editor
    $('#articleContent, #editArticleContent').summernote({
        height: 400,
        placeholder: 'Nhập nội dung bài viết...',
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']]
        ],
        callbacks: {
            onImageUpload: function (files) {
                // Upload image when inserted into editor
                for (let i = 0; i < files.length; i++) {
                    uploadImageToEditor(files[i]);
                }
            }
        }
    });

    // Load notifications khi mở dropdown
    $('#notificationDropdown').on('click', function () {
        loadNotifications(false); // Không hiển thị toast khi click vào dropdown
    });

    // Khởi tạo thống kê editor & polling thông báo duyệt / từ chối
    initEditorStats();

    // Menu navigation
    $('.sidebar-menu a[data-section]').click(function (e) {
        e.preventDefault();
        const section = $(this).data('section');

        // Update active menu
        $('.sidebar-menu li').removeClass('active');
        $(this).parent().addClass('active');

        // Show section
        $('.content-section').removeClass('active');
        $('#' + section).addClass('active');

        // Update page title
        updatePageTitle(section);

        // // Lazy load dữ liệu cho các tab khi được mở lần đầu
        // if (!loadedSections.has(section) && sectionLoaders[section]) {
        //     sectionLoaders[section]();
        // }
        loadSectionData(section);
    });

    // Header create button
    $('.header-actions button[data-section="create"]').click(function () {
        $('.sidebar-menu li').removeClass('active');
        $('.sidebar-menu a[data-section="create"]').parent().addClass('active');
        $('.content-section').removeClass('active');
        $('#create').addClass('active');
        $('#pageTitle').text('Tạo bài viết mới');
    });

    // Logout
    $('#logoutBtn').click(function (e) {
        e.preventDefault();
        if (confirm('Bạn có chắc muốn đăng xuất?')) {
            // Xóa localStorage nếu có
            localStorage.removeItem('userInfo');
            // Redirect đến endpoint logout để xóa session trên server và quay về trang đăng nhập
            window.location.href = '/admin/logout';
        }
    });

    // Image preview and upload
    $('#articleImage').change(function () {
        const file = this.files[0];
        if (file) {
            // Show preview
            const reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').html(`
                    <img src="${e.target.result}" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;">
                    <div class="upload-progress" style="display: block;">
                        <div class="progress">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%">Đang upload...</div>
                        </div>
                    </div>
                `);
            };
            reader.readAsDataURL(file);

            // Upload image immediately
            uploadArticleImage(file, 'tour', $('#editArticleId').val()).then(function (url) {
                if (url) {
                    $('#imagePreview .upload-progress').html('<div class="alert alert-success mt-2"><i class="fas fa-check"></i> Upload thành công</div>');
                } else {
                    $('#imagePreview .upload-progress').html('<div class="alert alert-danger mt-2"><i class="fas fa-times"></i> Upload thất bại</div>');
                }
            });
        }
    });

    // Save draft
    $('#saveDraftBtn').click(function () {
        saveDraft();
    });

    // Submit article
    $('#articleForm').submit(function (e) {
        e.preventDefault();
        submitArticle();
    });

    // Filter articles trong tab "Bài viết của tôi"
    $('#filterStatus').change(function () {
        const status = $(this).val();
        loadMyArticles(1, status, $('#searchMyArticles').val().trim());
    });

    // Tìm kiếm trong "Bài viết của tôi"
    $('#searchMyArticles').on('keypress', function (e) {
        if (e.which === 13) { // Enter
            e.preventDefault();
            loadMyArticles(1, $('#filterStatus').val(), $(this).val().trim());
        }
    });

    // Tìm kiếm ở tab Bản nháp
    $('#searchDrafts').on('keypress', function (e) {
        if (e.which === 13) {
            e.preventDefault();
            loadDrafts(1);
        }
    });

    // Tìm kiếm ở tab Chờ duyệt
    $('#searchPending').on('keypress', function (e) {
        if (e.which === 13) {
            e.preventDefault();
            loadPendingArticlesEditor(1);
        }
    });

    // Tìm kiếm ở tab Đã xuất bản
    $('#searchPublished').on('keypress', function (e) {
        if (e.which === 13) {
            e.preventDefault();
            loadPublishedArticles(1);
        }
    });

    // Edit article
    $(document).on('click', '.btn-edit', function () {
        const articleId = $(this).data('id');
        editArticle(articleId);
    });

    // Delete article
    $(document).on('click', '.btn-delete', function () {
        const articleId = $(this).data('id');
        if (confirm('Bạn có chắc muốn xóa bài viết này?')) {
            deleteArticle(articleId);
        }
    });

    // View article (for pending articles)
    $(document).on('click', '.btn-view', function () {
        const articleId = $(this).data('id');
        viewArticle(articleId);
    });

    // Toggle visibility
    $(document).on('change', '.visibility-toggle', function () {
        const articleId = $(this).data('id');
        const visible = $(this).prop('checked');
        toggleVisibility(articleId, visible);
    });

    // Save edit
    $('#saveEditBtn').click(function () {
        saveEdit('draft');
    });
    // Submit draft for review from edit modal
    $('#submitEditBtn').click(function () {
        saveEdit('pending');
    });

    // Edit article image upload handler
    $('#editArticleImage').change(function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                $('#editArticleImagePreview').attr('src', e.target.result);
            };
            reader.readAsDataURL(file);

            // Upload image immediately
            uploadArticleImage(file, 'tour', $('#editArticleId').val()).then(function (url) {
                if (url) {
                    $('#editArticleImageUrl').val(url);
                    $('#editArticleImagePreview').attr('src', url);
                }
            });
        }
    });

    // Multiple images upload for create form
    $('#articleGallery').change(async function () {
        const files = this.files;
        if (!files || files.length === 0) return;
        
        let urls = [];
        try {
            urls = JSON.parse($('#articleGalleryUrls').val() || '[]');
        } catch(e) {}
        
        showSpinner();
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const url = await uploadArticleImage(file, 'tour', $('#editArticleId').val());
            if (url) {
                urls.push(url);
            }
        }
        
        hideSpinner();
        $('#articleGalleryUrls').val(JSON.stringify(urls));
        renderGalleryPreview('#galleryPreview', '#articleGalleryUrls', urls);
        
        $(this).val('');
    });

    // Multiple images upload for edit form
    $('#editArticleGallery').change(async function () {
        const files = this.files;
        if (!files || files.length === 0) return;
        
        let urls = [];
        try {
            urls = JSON.parse($('#editArticleGalleryUrls').val() || '[]');
        } catch(e) {}
        
        showSpinner();
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const url = await uploadArticleImage(file, 'tour', $('#editArticleId').val());
            if (url) {
                urls.push(url);
            }
        }
        
        hideSpinner();
        $('#editArticleGalleryUrls').val(JSON.stringify(urls));
        renderGalleryPreview('#editGalleryPreview', '#editArticleGalleryUrls', urls);
        
        $(this).val('');
    });

    // Xem lý do từ chối
    $(document).on('click', '.btn-view-rejection', function () {

        fetch(`/admin/api/rejected-article/${$(this).data('id')}`).then(response => response.json()).then(data => {
            console.log(data);
            const title = data.title;
            const reason = data.rejection_reason;
            const rejectedBy = data.rejected_by;
            const rejectedAt = data.rejected_at;

            $('#rejectionArticleTitle').text(title);
            $('#rejectionRejectedBy').text(rejectedBy);
            $('#rejectionRejectedAt').text(rejectedAt);
            $('#rejectionReasonText').text(reason || 'Không có lý do từ chối');

            const modal = new bootstrap.Modal(document.getElementById('rejectionReasonModal'));
            modal.show();
        });
    });

    // // Initialize tag autocomplete for all tag inputs
    // initTagAutocomplete('#articleTags', '#tagSuggestions');
    // initTagAutocomplete('#editArticleTags', '#editTagSuggestions');
    // initTagAutocomplete('#intArticleTags', '#intTagSuggestions');
});

// ===== Editor statistics & notifications =====

let editorStats = {
    total: 0,
    draft: 0,
    pending: 0,
    published: 0,
    rejected: 0
};

// Lưu trữ danh sách ID bài viết đã thông báo
let notifiedArticleIds = new Set();

// Khởi tạo thống kê từ DOM và đồng bộ với API
function initEditorStats() {
    editorStats.total = parseInt($('#statTotal').text()) || 0;
    editorStats.draft = parseInt($('#statDrafts').text()) || 0;
    editorStats.pending = parseInt($('#statPending').text()) || 0;
    editorStats.published = parseInt($('#statPublished').text()) || 0;

    // Load danh sách ID đã thông báo từ localStorage
    const savedIds = localStorage.getItem('editor_notified_ids');
    if (savedIds) {
        try {
            notifiedArticleIds = new Set(JSON.parse(savedIds));
        } catch (e) {
            console.error('Lỗi load notified IDs:', e);
            notifiedArticleIds = new Set();
        }
    }

    // Đồng bộ lần đầu từ API (không cần thông báo)
    refreshEditorStats(false);
    loadNotifications(false);

    // Polling mỗi 30s để phát hiện bài được duyệt / bị từ chối
    setInterval(function () {
        refreshEditorStats(true);
        loadNotifications(true);
    }, 30000);
}

// Load data for specific section
async function loadSectionData(section) {
    switch (section) {
        case 'my-articles':
            loadMyArticles(1, $('#filterStatus').val(), $('#searchMyArticles').val().trim());
            break;
        case 'drafts':
            loadDrafts();
            break;
        case 'pending':
            loadPendingArticlesEditor();
            break;
        case 'rejected':
            loadRejectedArticles();
            break;
        case 'published':
            loadPublishedArticles();
            break;
        case 'dashboard':
            refreshEditorStats();
            break;
        case 'tour-tree':
            loadTourTree();
            break;
    }
}

async function requestMyArticles({ page = 1, perPage = 10, status = null, search = null } = {}) {
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('per_page', perPage);
    if (status && status !== 'all') {
        params.append('status', status);
    }
    if (search) {
        params.append('search', search);
    }

    const response = await fetch(`/admin/api/tour/my-articles?${params.toString()}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    });

    const result = await response.json();
    return { ok: response.ok, result };
}

// Lấy tổng bài theo trạng thái cho editor hiện tại (dựa trên pagination.total)
async function fetchCountByStatus(status) {
    try {
        const { ok, result } = await requestMyArticles({ page: 1, perPage: 1, status });
        if (!ok || !result.success || !result.pagination) {
            return null;
        }

        return result.pagination.total || 0;
    } catch (error) {
        console.error('Lỗi tải thống kê bài viết editor:', error);
        return null;
    }
}

// Cập nhật lại thống kê & hiển thị toast khi có bài được duyệt / từ chối
async function refreshEditorStats() {
    try {

        const response = await fetch('/admin/api/statistics/editor', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        const result = await response.json();
        if (!result.success || !result.data) {
            return;
        }

        // Cập nhật DOM dashboard
        $('#statTotal').text(result.data.total);
        $('#statDrafts').text(result.data.draft);
        $('#statPending').text(result.data.pending);
        $('#statPublished').text(result.data.published);

        // Cập nhật badge menu trái
        $('#draftCount').text(result.data.draft);
        $('#pendingCount').text(result.data.pending);


        $('#approvedNewsTitle').text(result.data.article_approved);
        $('#updateNewsTitle').text(result.data.article_update);
        $('#newestNewsTitle').text(result.data.article_newest);
    } catch (error) {
        console.error('Lỗi cập nhật thống kê editor:', error);
    }
}

// Load notifications từ API và hiển thị
async function loadNotifications(showToastNotifications) {
    try {
        const response = await fetch('/admin/api/editor-notifications?limit=20', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) {
            return;
        }

        const result = await response.json();
        if (!result.success || !result.data) {
            return;
        }

        const notifications = result.data || [];
        const newNotifications = [];

        // Phát hiện các bài viết mới được duyệt/từ chối
        notifications.forEach(notif => {
            const articleId = notif.tour_id.toString();
            if (!notifiedArticleIds.has(articleId)) {
                newNotifications.push(notif);
                notifiedArticleIds.add(articleId);
            }
        });

        // Lưu danh sách ID đã thông báo vào localStorage
        if (newNotifications.length > 0) {
            localStorage.setItem('editor_notified_ids', JSON.stringify(Array.from(notifiedArticleIds)));
        }

        // Hiển thị toast cho các bài viết mới
        if (showToastNotifications && newNotifications.length > 0) {
            newNotifications.forEach(notif => {
                if (notif.status === 'published') {
                    showToast('Thông báo', `Bài viết "${notif.title}" đã được duyệt và xuất bản`, 'success');
                } else if (notif.status === 'rejected') {
                    showToast('Thông báo', `Bài viết "${notif.title}" đã bị từ chối`, 'warning');
                }
            });
        }

        // Hiển thị notifications trong dropdown
        displayNotifications(notifications);
    } catch (error) {
        console.error('Lỗi tải notifications:', error);
    }
}

// Hiển thị notifications trong dropdown
function displayNotifications(notifications) {
    const $notificationList = $('#notificationList');
    const $notificationEmpty = $('#notificationEmpty');
    const $notificationCount = $('#notificationCount');

    if (!notifications || notifications.length === 0) {
        $notificationList.html('');
        $notificationEmpty.show().text('Chưa có thông báo mới.');
        $notificationCount.text('0').hide();
        return;
    }

    $notificationEmpty.hide();

    // Đếm số notification chưa đọc (các bài mới)
    const unreadCount = notifications.filter(n => !notifiedArticleIds.has(n.tour_id.toString())).length;

    if (unreadCount > 0) {
        $notificationCount.text(unreadCount).show();
    } else {
        $notificationCount.hide();
    }

    let html = '';
    notifications.slice(0, 10).forEach(notif => {
        const isUnread = !notifiedArticleIds.has(notif.tour_id.toString());
        const dateStr = notif.published_at || notif.updated_at || '';
        const date = dateStr ? new Date(dateStr + 'Z').toLocaleString('vi-VN', {
            timeZone: 'Asia/Ho_Chi_Minh',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }) : '';

        const statusClass = notif.status === 'published' ? 'success' : 'danger';
        const statusIcon = notif.status === 'published' ? 'fa-check-circle' : 'fa-times-circle';
        const statusText = notif.status === 'published' ? 'Đã duyệt' : 'Bị từ chối';

        html += `
            <li>
                <div class="dropdown-item ${isUnread ? 'notification-unread' : ''}" style="cursor: pointer;" data-article-id="${notif.id}">
                    <div class="d-flex align-items-start">
                        <div class="flex-shrink-0">
                            <i class="fas ${statusIcon} text-${statusClass}"></i>
                        </div>
                        <div class="flex-grow-1 ms-2">
                            <div class="fw-bold">${escapeHtml(notif.title || 'Không có tiêu đề')}</div>
                            <small class="text-muted">
                                <span class="badge bg-${statusClass}">${statusText}</span>
                                ${date ? ` - ${date}` : ''}
                            </small>
                        </div>
                    </div>
                </div>
            </li>
        `;
    });

    $notificationList.html(html);

    // Xử lý click vào notification để mở edit modal và đánh dấu đã đọc
    $notificationList.off('click', '.dropdown-item').on('click', '.dropdown-item', function () {
        const articleId = $(this).data('article-id');
        if (articleId) {
            // Đánh dấu đã đọc
            notifiedArticleIds.add(articleId.toString());
            localStorage.setItem('editor_notified_ids', JSON.stringify(Array.from(notifiedArticleIds)));

            // Cập nhật lại hiển thị
            displayNotifications(notifications);

            // Mở modal edit
            editArticle(articleId);
        }
    });
}

// Helper function để escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// Update page title
function updatePageTitle(section) {
    const titles = {
        'dashboard': 'Dashboard',
        'my-articles': 'Bài viết của tôi',
        'create': 'Tạo bài viết mới',
        'drafts': 'Bản nháp',
        'pending': 'Chờ duyệt',
        'published': 'Đã xuất bản',
        'tour-tree': 'Sơ đồ Phân cấp Tour',
    };
    $('#pageTitle').text(titles[section] || 'Dashboard');
}

// Load my articles from API (database, joined with categories) với phân trang & lọc
async function loadMyArticles(page = 1, status = null, search = null) {
    try {
        markSectionLoaded('my-articles');
        showSpinner();

        const { ok, result } = await requestMyArticles({
            page,
            perPage: 10,
            status,
            search
        });
        hideSpinner();

        if (!ok || !result.success) {
            showToast('Lỗi', result.error || 'Không thể tải danh sách bài viết', 'warning');
            return;
        }

        // Chuẩn hóa dữ liệu trả về để phù hợp với displayArticles
        const articles = (result.data || []).map(item => ({
            tour_id: item.tour_id,
            title: item.title,
            // Ưu tiên tên danh mục lấy từ bảng categories (category_name / category_title...),
            // fallback về slug hoặc chuỗi rỗng nếu không có
            category_name: item.category_name || item.category_title || item.category || '',
            status: item.status, // ví dụ: 'draft' | 'pending' | 'published'
            visible: item.visible !== undefined ? item.visible : true,
            // Chuyển ngày về string hiển thị
            date: item.created_at || item.published_at || ''
        }));

        var tabIdLoad = '';
        if (status == 'draft') {
            tabIdLoad = 'draftsTable';
        } else if (status == 'pending') {
            tabIdLoad = 'pendingTable';
        } else if (status == 'published') {
            tabIdLoad = 'publishedTable';
        } else {
            tabIdLoad = 'myArticlesTable';
        }

        const pagination = result.pagination || {};
        displayArticles(articles, tabIdLoad);
        updatePagination(
            pagination,
            'myArticlesPagination',
            (newPage) => loadMyArticles(newPage, $('#filterStatus').val(), $('#searchMyArticles').val().trim())
        );
        updateInfoText(pagination, 'myArticlesInfo');
    } catch (error) {
        console.error('Lỗi tải bài viết:', error);
        hideSpinner();
        showToast('Lỗi', 'Có lỗi xảy ra khi tải danh sách bài viết', 'warning');
    }
}

// Load danh sách bản nháp
function loadDrafts(page = 1) {
    const search = $('#searchDrafts').val() ? $('#searchDrafts').val().trim() : null;
    fetchMyArticlesForSection('draft', page, search, 'draftsTable', 'draftsPagination', 'draftsInfo', 'drafts');
}

// Load danh sách chờ duyệt
function loadPendingArticlesEditor(page = 1) {
    const search = $('#searchPending').val() ? $('#searchPending').val().trim() : null;
    fetchMyArticlesForSection('pending', page, search, 'pendingTable', 'pendingPagination', 'pendingInfo', 'pending');
}

// Load danh sách bị từ chối
function loadRejectedArticles(page = 1) {
    const search = $('#searchRejected').val() ? $('#searchRejected').val().trim() : null;
    fetchMyArticlesForSection('rejected', page, search, 'rejectedTable', 'rejectedPagination', 'rejectedInfo', 'rejected');
}

// Load danh sách đã xuất bản
function loadPublishedArticles(page = 1) {
    const search = $('#searchPublished').val() ? $('#searchPublished').val().trim() : null;
    fetchMyArticlesForSection('published', page, search, 'publishedTable', 'publishedPagination', 'publishedInfo', 'published');
}

// Hàm dùng chung để load bài viết cho từng section
async function fetchMyArticlesForSection(status, page, search, tableId, paginationId, infoId, sectionKey = null) {
    try {
        if (sectionKey) {
            markSectionLoaded(sectionKey);
        }
        showSpinner();

        const { ok, result } = await requestMyArticles({
            page,
            perPage: 10,
            status,
            search
        });
        hideSpinner();

        if (!ok || !result.success) {
            showToast('Lỗi', result.error || 'Không thể tải danh sách bài viết', 'warning');
            return;
        }

        const articles = (result.data || []).map(item => ({
            tour_id: item.tour_id,
            title: item.title,
            category_name: item.category_name || (item.category && item.category.name) || '',
            status: item.status,
            visible: item.visible !== undefined ? item.visible : true,
            date: item.created_at || item.published_at || ''
        }));

        const pagination = result.pagination || {};
        displayArticles(articles, tableId);
        updatePagination(
            pagination,
            paginationId,
            (newPage) => fetchMyArticlesForSection(status, newPage, search, tableId, paginationId, infoId)
        );
        updateInfoText(pagination, infoId);
    } catch (error) {
        console.error('Lỗi tải bài viết:', error);
        hideSpinner();
        showToast('Lỗi', 'Có lỗi xảy ra khi tải danh sách bài viết', 'warning');
    }
}

// Get approved news title
function getApprovedNewsTitle(articles) {
    const approvedNewsTitle = articles.find(article => article.status === 'published');
    $('#approvedNewsTitle').text(approvedNewsTitle.title);
}

// Get update news title
function getUpdateNewsTitle(articles) {
    const updateNewsTitle = articles.find(article => article.updated_at !== article.created_at);
    $('#updateNewsTitle').text(updateNewsTitle.title);
}

// Get create news title
function getCreateNewsTitle(articles) {
    const createNewsTitle = articles.find(article => article.created_at !== article.updated_at);
    $('#createNewsTitle').text(createNewsTitle.title);
}

// Display articles vào bảng theo ID
function displayArticles(articles, tableBodyId) {
    // create empty table before load
    $('#' + tableBodyId).html('');
    let html = '';
    articles.forEach((article, index) => {
        const statusBadge = getStatusBadge(article.status);
        const checked = article.visible ? 'checked' : '';

        const date = new Date(article.date + 'Z');

        const dateVN = date.toLocaleString('sv-SE', {
            timeZone: 'Asia/Ho_Chi_Minh', // Chuyển sang múi giờ VN
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false // Sử dụng định dạng 24h
        });

        html += '';
        html += '<tr>';
        // html += '<td>' + (index + 1) + '</td>';
        html += '<td><strong>' + article.title + '</strong></td>';
        html += '<td><span class="badge bg-primary">' + article.category_name + '</span></td>';
        if (tableBodyId != 'draftsTable' && tableBodyId != 'publishedTable') {
            html += '<td>' + statusBadge + '</td>';
        } else {
            html += '<td style="display: none;">' + statusBadge + '</td>';
        }
        html += '<td style="display: none;">';
        html += '<label class="visibility-switch">';
        html += '<input type="checkbox" class="visibility-toggle" data-id="' + article.tour_id + '" ' + checked + '>';
        html += '<span class="visibility-slider"></span>';
        html += '</label>';
        html += '</td>';
        html += '<td>' + (dateVN) + '</td>';
        html += '<td>';
        // Chỉ hiển thị nút edit và delete cho bài viết draft
        // Bài viết pending chỉ có quyền xem
        if (article.status === 'draft' || article.status === 'rejected') {
            html += '<button class="btn btn-sm btn-info btn-action btn-edit" data-id="' + article.tour_id + '" title="Chỉnh sửa">';
            html += '<i class="fas fa-edit"></i>';
            html += '</button>';
            html += '<button class="btn btn-sm btn-danger btn-action btn-delete" data-id="' + article.tour_id + '" title="Xóa">';
            html += '<i class="fas fa-trash"></i>';
            html += '</button>';
        } else if (article.status === 'pending') {
            // Bài viết pending chỉ có quyền xem, không có nút action
            html += '<button class="btn btn-sm btn-info btn-action btn-view" data-id="' + article.tour_id + '" title="Xem bài viết">';
            html += '<i class="fas fa-eye"></i>';
            html += '</button>';
        } else {
            // Các trạng thái khác (published, rejected) vẫn có nút delete
            html += '<button class="btn btn-sm btn-danger btn-action btn-delete" data-id="' + article.tour_id + '" title="Xóa">';
            html += '<i class="fas fa-trash"></i>';
            html += '</button>';
        }

        if (article.status === 'rejected') {
            html += '<button class="btn btn-sm btn-danger btn-action btn-view-rejection"';
            html += 'data-id="' + article.tour_id + '" data-title="' + article.title + '" data-reason="' + article.rejection_reason + '" data-rejected-by="' + article.rejected_by + '" data-rejected-at="' + article.rejected_at + '" title="Xem lý do từ chối">';
            html += '<i class="fas fa-info-circle"></i>';
            html += '</button>';
        }

        html += '</td>';
        html += '</tr>';
    });

    $('#' + tableBodyId).html(html);
}

// Get status badge
function getStatusBadge(status) {
    const badges = {
        'draft': '<span class="status-badge status-draft">Bản nháp</span>',
        'pending': '<span class="status-badge status-pending">Chờ duyệt</span>',
        'published': '<span class="status-badge status-published">Đã xuất bản</span>',
        'rejected': '<span class="status-badge status-rejected">Bị từ chối</span>'
    };
    return badges[status] || status;
}

// Cập nhật thanh phân trang
function updatePagination(pagination, containerId, onPageClick) {
    const container = $('#' + containerId);
    container.empty();

    const page = pagination.page || 1;
    const totalPages = pagination.pages || 1;

    if (totalPages <= 1) {
        return;
    }

    const createPageItem = (p, label = null, disabled = false, active = false) => {
        const li = $('<li>').addClass('page-item');
        if (disabled) li.addClass('disabled');
        if (active) li.addClass('active');

        const a = $('<a>')
            .addClass('page-link')
            .attr('href', '#')
            .attr('data-page', p)
            .text(label || p);

        a.on('click', function (e) {
            e.preventDefault();
            if (!disabled && !active) {
                onPageClick(p);
            }
        });

        li.append(a);
        container.append(li);
    };

    createPageItem(page - 1, '«', page <= 1, false);

    for (let p = 1; p <= totalPages; p++) {
        createPageItem(p, null, false, p === page);
    }

    createPageItem(page + 1, '»', page >= totalPages, false);
}

// Hiển thị thông tin phân trang
function updateInfoText(pagination, infoElementId) {
    const infoEl = $('#' + infoElementId);
    const page = pagination.page || 1;
    const perPage = pagination.per_page || 10;
    const total = pagination.total || 0;

    if (!total) {
        infoEl.text('Không có bản ghi nào.');
        return;
    }

    const start = (page - 1) * perPage + 1;
    const end = Math.min(page * perPage, total);
    infoEl.text(`Hiển thị ${start}-${end} trên tổng ${total} bài viết`);
}

// Upload image to editor (for Summernote)
async function uploadImageToEditor(file) {
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/admin/api/upload-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // Insert image into editor
            $('#articleContent').summernote('insertImage', result.url);
        } else {
            showToast('Lỗi', result.error || 'Upload ảnh thất bại', 'warning');
        }
    } catch (error) {
        console.error('Lỗi upload ảnh:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi upload ảnh', 'warning');
    }
}

// Save draft
async function saveDraft() {
    const title = $('#articleTitle').val().trim();
    const content = $('#articleContent').summernote('code');
    const category = $('#articleCategory').val();
    const location_id = $('#articleLocation').val();
    const description = $('#articleDescription').val().trim();
    const thumbnail = $('#articleImageUrl').val() || '';
    const price_per_adult = $('#price_per_adult').val() || 0;
    const price_per_child = $('#price_per_child').val() || 0;
    const duration_days = $('#articleDurationDays').val() || 1;
    const isHot = $('#articleIsHot').is(':checked');
    const isFeatured = $('#articleIsFeatured').is(':checked');
    // const tags = normalizeTagString($('#articleTags').val());

    if (!title) {
        showToast('Cảnh báo', 'Vui lòng nhập tiêu đề bài viết!', 'warning');
        return;
    }

    if (!content || content.trim() === '' || content === '<p><br></p>') {
        showToast('Cảnh báo', 'Vui lòng nhập nội dung bài viết!', 'warning');
        return;
    }

    if (!category) {
        showToast('Cảnh báo', 'Vui lòng chọn danh mục!', 'warning');
        return;
    }

    if (!location_id) {
        showToast('Cảnh báo', 'Vui lòng chọn địa điểm!', 'warning');
        return;
    }

    if (!price_per_adult) {
        showToast('Cảnh báo', 'Vui lòng nhập giá người lớn!', 'warning');
        return;
    }

    if (!price_per_child) {
        showToast('Cảnh báo', 'Vui lòng nhập giá trẻ em!', 'warning');
        return;
    }

    // Validate tags - chỉ chấp nhận tags có sẵn
    // if (tags) {
    //     const tagValidation = validateTags(tags);
    //     if (!tagValidation.valid) {
    //         showToast('Cảnh báo', `Các tags sau không tồn tại trong hệ thống: ${tagValidation.invalidTags.join(', ')}. Vui lòng chỉ sử dụng tags có sẵn.`, 'warning');
    //         return;
    //     }
    // }

    showSpinner();

    try {
        const response = await fetch('/admin/api/tour/article/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content,
                category_name: category,
                location_id: location_id,
                price_per_adult: price_per_adult,
                price_per_child: price_per_child,
                duration_days: duration_days,
                summary: description,
                thumbnail: thumbnail,
                is_hot: isHot,
                is_featured: isFeatured,
                // tags: tags,
                status: 'draft',
                images: JSON.parse($('#articleGalleryUrls').val() || '[]')
            })
        });

        const result = await response.json();

        hideSpinner();

        if (result.success) {
            showToast('Thành công', 'Bài viết đã được lưu vào bản nháp', 'success');

            // Clear form
            $('#articleForm')[0].reset();
            $('#articleContent').summernote('code', '');
            $('#imagePreview').html('');
            $('#articleImageUrl').val('');
            $('#galleryPreview').html('');
            $('#articleGalleryUrls').val('[]');
            $('#articleIsHot').prop('checked', false);
            $('#articleIsFeatured').prop('checked', false);
            $('#articleDurationDays').val('1');

            // Đồng bộ lại thống kê từ API
            refreshEditorStats(false);

            // Reload articles
            loadMyArticles();
        } else {
            showToast('Lỗi', result.error || 'Không thể lưu bài viết', 'warning');
        }
    } catch (error) {
        hideSpinner();
        console.error('Lỗi lưu bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi lưu bài viết', 'warning');
    }
}

function normalizeTagString(tagsString) {
    return tagsString.trim().replace(/[,;]+/g, ',');
}

// Validate tags - chỉ chấp nhận tags có sẵn trong tagSuggestionsCache
function validateTags(tagsString) {
    if (!tagsString || !tagsString.trim()) {
        return { valid: true, invalidTags: [] };
    }

    // Đảm bảo cache đã được load
    if (tagSuggestionsCache.length === 0) {
        console.warn('Tag cache chưa được load, đang tải...');
        // Không block user, nhưng sẽ validate ở backend
        return { valid: true, invalidTags: [], warning: 'Cache chưa sẵn sàng, sẽ validate ở server' };
    }

    // Parse tags từ string
    const tagNames = tagsString
        .split(/[,\s;]+/)
        .map(tag => tag.trim().replace(/^#/, ''))
        .filter(tag => tag.length > 0);

    const invalidTags = [];

    // Kiểm tra từng tag có trong cache không (case-insensitive)
    tagNames.forEach(tagName => {
        const tagLower = tagName.toLowerCase();
        const found = tagSuggestionsCache.some(cachedTag => cachedTag.toLowerCase() === tagLower);
        if (!found) {
            invalidTags.push(tagName);
        }
    });

    return {
        valid: invalidTags.length === 0,
        invalidTags: invalidTags
    };
}

// Submit article
async function submitArticle() {
    const title = $('#articleTitle').val().trim();
    const content = $('#articleContent').summernote('code');
    const category = $('#articleCategory').val();
    const location_id = $('#articleLocation').val();
    const price_per_adult = $('#price_per_adult').val() || 0;
    const price_per_child = $('#price_per_child').val() || 0;
    const duration_days = $('#articleDurationDays').val() || 1;
    const description = $('#articleDescription').val().trim();
    const thumbnail = $('#articleImageUrl').val() || '';
    const isHot = $('#articleIsHot').is(':checked');
    const isFeatured = $('#articleIsFeatured').is(':checked');
    // const tags = normalizeTagString($('#articleTags').val());

    // Validation
    if (!title) {
        showToast('Cảnh báo', 'Vui lòng nhập tiêu đề bài viết!', 'warning');
        return;
    }

    if (!content || content.trim() === '' || content === '<p><br></p>') {
        showToast('Cảnh báo', 'Vui lòng nhập nội dung bài viết!', 'warning');
        return;
    }

    if (!category) {
        showToast('Cảnh báo', 'Vui lòng chọn danh mục!', 'warning');
        return;
    }

    if (!location_id) {
        showToast('Cảnh báo', 'Vui lòng chọn địa điểm!', 'warning');
        return;
    }

    if (!price_per_adult) {
        showToast('Cảnh báo', 'Vui lòng nhập giá người lớn!', 'warning');
        return;
    }

    if (!price_per_child) {
        showToast('Cảnh báo', 'Vui lòng nhập giá trẻ em!', 'warning');
        return;
    }

    if (!duration_days || duration_days < 1) {
        showToast('Cảnh báo', 'Vui lòng nhập số ngày đi hợp lệ (tối thiểu 1 ngày)!', 'warning');
        return;
    }

    // // Validate tags - chỉ chấp nhận tags có sẵn
    // const tagValidation = validateTags(tags);
    // if (!tagValidation.valid) {
    //     showToast('Cảnh báo', `Các tags sau không tồn tại trong hệ thống: ${tagValidation.invalidTags.join(', ')}. Vui lòng chỉ sử dụng tags có sẵn.`, 'warning');
    //     return;
    // }

    showSpinner();

    try {
        const response = await fetch('/admin/api/tour/article/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content,
                category_name: category,
                location_id: location_id,
                price_per_adult: price_per_adult,
                price_per_child: price_per_child,
                duration_days: duration_days,
                summary: description,
                thumbnail: thumbnail,
                is_hot: isHot,
                is_featured: isFeatured,
                // tags: tags,
                status: 'pending',
                images: JSON.parse($('#articleGalleryUrls').val() || '[]')
            })
        });

        const result = await response.json();

        hideSpinner();

        if (result.success) {
            showToast('Thành công', 'Bài viết đã được gửi để duyệt', 'success');

            // Clear form
            $('#articleForm')[0].reset();
            $('#articleContent').summernote('code', '');
            $('#imagePreview').html('');
            $('#articleImageUrl').val('');
            $('#galleryPreview').html('');
            $('#articleGalleryUrls').val('[]');
            $('#articleIsHot').prop('checked', false);
            $('#articleIsFeatured').prop('checked', false);
            $('#articleDurationDays').val('1');

            // Đồng bộ lại thống kê từ API
            refreshEditorStats(false);

            // Reload articles
            loadMyArticles();
        } else {
            showToast('Lỗi', result.error || 'Không thể gửi bài viết', 'warning');
        }
    } catch (error) {
        hideSpinner();
        console.error('Lỗi gửi bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi gửi bài viết', 'warning');
    }
}

// View article (read-only for pending articles)
async function viewArticle(articleId) {
    try {
        const response = await fetch(`/admin/api/tour/article/${articleId}`);
        const result = await response.json();
        if (result.success) {
            const article = result.data;

            // Open preview in new window
            const previewWindow = window.open('', 'Xem bài viết', 'width=1000,height=700,scrollbars=yes');
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>${escapeHtml(article.title || 'Xem bài viết')}</title>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            padding: 40px; 
                            max-width: 900px; 
                            margin: 0 auto; 
                            background: #f5f5f5;
                            line-height: 1.6;
                        }
                        .article-container {
                            background: white;
                            padding: 40px;
                            border-radius: 8px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        h1 { 
                            color: #333; 
                            margin-bottom: 15px; 
                            font-size: 28px;
                            line-height: 1.3;
                        }
                        .meta { 
                            color: #666; 
                            font-size: 14px; 
                            margin-bottom: 20px; 
                            padding-bottom: 15px;
                            border-bottom: 1px solid #eee;
                        }
                        .category { 
                            background: #0066cc; 
                            color: white; 
                            padding: 5px 12px; 
                            border-radius: 4px; 
                            font-size: 12px; 
                            display: inline-block; 
                            margin-bottom: 15px; 
                            font-weight: 500;
                        }
                        .status-badge {
                            display: inline-block;
                            padding: 5px 12px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 500;
                            margin-left: 10px;
                        }
                        .status-pending {
                            background: #ffc107;
                            color: #000;
                        }
                        .status-hot {
                            background: #ff0000;
                            color: #000;
                        }
                        .status-featured {
                            background: #ffa500;
                            color: #000;
                        }
                        .content { 
                            line-height: 1.8; 
                            color: #444; 
                            margin-top: 25px;
                            font-size: 16px;
                        }
                        .summary { 
                            background: #f8f9fa; 
                            padding: 20px; 
                            border-left: 4px solid #0066cc; 
                            margin-bottom: 25px; 
                            border-radius: 4px;
                        }
                        .summary strong {
                            color: #333;
                            display: block;
                            margin-bottom: 8px;
                        }
                        img { 
                            max-width: 100%; 
                            height: auto; 
                            margin: 25px 0; 
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }
                        .view-info {
                            background: #e7f3ff;
                            padding: 15px;
                            border-radius: 4px;
                            margin-bottom: 20px;
                            border-left: 4px solid #0066cc;
                        }
                        .view-info strong {
                            color: #0066cc;
                        }
                    </style>
                </head>
                <body>
                    <div class="article-container">
                        <div class="view-info">
                            <strong><i class="fas fa-info-circle"></i> Chế độ xem:</strong> Bạn đang xem bài viết ở chế độ chỉ đọc (read-only)
                        </div>
                        <span class="category">${escapeHtml(article.category_name || article.category || 'N/A')}</span>
                        ${article.is_hot ? `<span class="status-badge status-hot"><i class="fas fa-fire text-danger"></i> Tin nóng</span>` : ''}
                        ${article.is_featured ? `<span class="status-badge status-featured"><i class="fas fa-star text-warning"></i> Tin nổi bật</span>` : ''}
                        ${article.status === 'pending' ? `<span class="status-badge status-pending">Chờ duyệt</span>` : ''}
                        ${article.status === 'approved' ? `<span class="status-badge status-approved">Đã duyệt</span>` : ''}
                        ${article.status === 'rejected' ? `<span class="status-badge status-rejected">Đã từ chối</span>` : ''}
                        <h1>${escapeHtml(article.title || 'Không có tiêu đề')}</h1>
                        <div class="meta">
                            <i class="fas fa-calendar"></i> Ngày tạo: ${article.created_at ? new Date(article.created_at + 'Z').toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : 'N/A'} 
                            ${article.updated_at && article.updated_at !== article.created_at ?
                    ' | <i class="fas fa-edit"></i> Cập nhật: ' + new Date(article.updated_at + 'Z').toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : ''}
                        </div>
                        ${article.thumbnail ? `<img src="${escapeHtml(article.thumbnail)}" alt="${escapeHtml(article.title)}" onerror="this.style.display='none'">` : ''}
                        ${article.summary ? `<div class="summary"><strong>Tóm tắt:</strong> ${escapeHtml(article.summary)}</div>` : ''}
                        <div class="content">${article.content || 'Không có nội dung'}</div>
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        } else {
            showToast('Lỗi', result.error || 'Không thể tải bài viết', 'warning');
        }
    } catch (error) {
        console.error('Lỗi tải bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi tải bài viết', 'warning');
    }
}

// Edit article
async function editArticle(articleId) {
    try {
        const response = await fetch(`/admin/api/tour/article/${articleId}`);
        const result = await response.json();
        if (result.success) {
            const article = result.data;

            // Kiểm tra trạng thái bài viết
            if (article.status !== 'draft' && article.status !== 'rejected') {
                showToast('Không thể chỉnh sửa', 'Bài viết đang trong trạng thái chờ duyệt hoặc đã xuất bản, bạn không thể chỉnh sửa', 'warning');
                return;
            }

            // Load categories if not already loaded
            if ($('#editArticleCategory option').length <= 1) {
                try {
                    const catResponse = await fetch('/admin/api/categories');
                    const catResult = await catResponse.json();
                    if (catResult.success && catResult.data) {
                        let categoryOptions = '<option value="">Chọn danh mục</option>';
                        catResult.data.forEach(cat => {
                            categoryOptions += `<option value="${cat.id}">${cat.name}</option>`;
                        });
                        $('#editArticleCategory').html(categoryOptions);
                    }
                } catch (error) {
                    console.error('Lỗi tải danh mục:', error);
                }
            }

            $('#editArticleId').val(article.tour_id);
            $('#editArticleTitle').val(article.title);
            $('#editArticleContent').summernote('code', article.content);
            $('#editArticleCategory').val(article.category_name);
            $('#editArticleLocation').val(article.location_id);
            $('#editArticlePricePerAdult').val(article.price_per_adult);
            $('#editArticlePricePerChild').val(article.price_per_child);
            $('#editArticleDescription').val(article.summary);
            $('#editArticleImageUrl').val(article.thumbnail || '');
            $('#editArticleImagePreview').attr('src', article.thumbnail || '/static/images/default-image.png');
            $('#editArticleIsHot').prop('checked', article.is_hot || false);
            $('#editArticleIsFeatured').prop('checked', article.is_featured || false);
            $('#editArticleDurationDays').val(article.duration_days);
            $('#editArticlePricePerAdult').val(article.price_per_adult);
            $('#editArticlePricePerChild').val(article.price_per_child);
            $('#editArticleSlug').val(article.slug);
            // $('#editArticleTags').val(article.tags || '');

            const galleryUrls = article.images || [];
            $('#editArticleGalleryUrls').val(JSON.stringify(galleryUrls));
            renderGalleryPreview('#editGalleryPreview', '#editArticleGalleryUrls', galleryUrls);

            const modal = new bootstrap.Modal(document.getElementById('editModal'));
            modal.show();
        } else {
            showToast('Lỗi', result.error || 'Không thể tải bài viết', 'warning');
        }
    } catch (error) {
        console.error('Lỗi tải bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi tải bài viết', 'warning');
    }
}

// Save edit (có thể kèm theo thay đổi trạng thái, ví dụ: gửi duyệt)
async function saveEdit(newStatus = null) {
    const articleId = $('#editArticleId').val();
    const title = $('#editArticleTitle').val();
    const content = $('#editArticleContent').summernote('code');
    const category = $('#editArticleCategory').val();
    const description = $('#editArticleDescription').val();
    const image = $('#editArticleImageUrl').val();
    const isHot = $('#editArticleIsHot').is(':checked');
    const isFeatured = $('#editArticleIsFeatured').is(':checked');
    const location_id = $('#editArticleLocation').val();
    const price_per_adult = $('#editArticlePricePerAdult').val() || 0;
    const price_per_child = $('#editArticlePricePerChild').val() || 0;
    const slug = $('#editArticleSlug').val();
    const duration_days = $('#editArticleDurationDays').val() || 0;
    const status = newStatus;
    // const tags = normalizeTagString($('#editArticleTags').val());
    if (!title) {
        showToast('Cảnh báo', 'Vui lòng nhập tiêu đề bài viết!', 'warning');
        return;
    }

    if (!content) {
        showToast('Cảnh báo', 'Vui lòng nhập nội dung bài viết!', 'warning');
        return;
    }
    if (!category) {
        showToast('Cảnh báo', 'Vui lòng chọn danh mục!', 'warning');
        return;
    }
    if (!description) {
        showToast('Cảnh báo', 'Vui lòng nhập mô tả ngắn gọn về bài viết!', 'warning');
        return;
    }
    if (!image) {
        showToast('Cảnh báo', 'Vui lòng chọn ảnh đại diện!', 'warning');
        return;
    }
    if (!location_id) {
        showToast('Cảnh báo', 'Vui lòng chọn địa điểm!', 'warning');
        return;
    }
    // if (!tags) {
    //     showToast('Cảnh báo', 'Vui lòng nhập tags!', 'warning');
    //     return;
    // }

    // // Validate tags - chỉ chấp nhận tags có sẵn
    // const tagValidation = validateTags(tags);
    // if (!tagValidation.valid) {
    //     showToast('Cảnh báo', `Các tags sau không tồn tại trong hệ thống: ${tagValidation.invalidTags.join(', ')}. Vui lòng chỉ sử dụng tags có sẵn.`, 'warning');
    //     return;
    // }

    try {
        const payload = {
            id: articleId,
            title: title,
            content: content,
            category_name: category,
            summary: description,
            thumbnail: image,
            is_hot: isHot,
            is_featured: isFeatured,
            location_id: location_id,
            price_per_adult: price_per_adult,
            price_per_child: price_per_child,
            slug: slug,
            duration_days: duration_days,
            images: JSON.parse($('#editArticleGalleryUrls').val() || '[]')
            // tags: tags
        };
        if (newStatus) {
            payload.status = newStatus;
        } else {
            payload.status = status;
        }

        const response = await fetch(`/admin/api/tour/article/${articleId}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (result.success) {
            showToast('Thành công', 'Bài viết đã được cập nhật', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadMyArticles(1, status, null);
        } else {
            showToast('Lỗi', result.error || 'Không thể cập nhật bài viết', 'warning');
        }
    } catch (error) {
        hideSpinner();
        console.error('Lỗi cập nhật bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi cập nhật bài viết', 'warning');
    }
}

// Delete article (soft delete)
async function deleteArticle(articleId) {
    showSpinner();

    try {
        const response = await fetch(`/admin/api/tour/article/${articleId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        hideSpinner();

        if (response.ok) {
            showToast('Thành công', 'Bài viết đã được xóa', 'success');

            // Remove from table
            $('button[data-id="' + articleId + '"]').closest('tr').fadeOut(function () {
                $(this).remove();
            });

            // Reload current section to refresh the list
            const activeSection = $('.content-section.active').attr('id');
            if (activeSection === 'my-articles') {
                loadMyArticles(1, $('#filterStatus').val(), $('#searchMyArticles').val().trim());
            } else if (activeSection === 'drafts') {
                loadDrafts(1);
            } else if (activeSection === 'pending') {
                loadPendingArticlesEditor(1);
            } else if (activeSection === 'published') {
                loadPublishedArticles(1);
            }

            // Đồng bộ lại thống kê từ API sau khi xóa
            refreshEditorStats(false);
        } else {
            const result = await response.json().catch(() => ({}));
            showToast('Lỗi', result.error || 'Không thể xóa bài viết', 'warning');
        }
    } catch (error) {
        hideSpinner();
        console.error('Lỗi xóa bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi xóa bài viết', 'warning');
    }
}

// Toggle visibility
function toggleVisibility(articleId, visible) {
    const status = visible ? 'hiện' : 'ẩn';

    showSpinner();

    // Simulate API call
    setTimeout(function () {
        hideSpinner();
        showToast('Thành công', `Bài viết đã được ${status}`, 'success');
    }, 500);
}

// Show spinner
function showSpinner() {
    $('body').append('<div class="spinner-overlay"><div class="spinner-border-custom"></div></div>');
}

// Hide spinner
function hideSpinner() {
    $('.spinner-overlay').fadeOut(function () {
        $(this).remove();
    });
}

// Show toast notification
function showToast(title, message, type) {
    const bgClass = type === 'success' ? 'bg-success' : type === 'warning' ? 'bg-warning' : 'bg-info';
    const toast = `
        <div class="toast custom-toast" role="alert">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    if (!$('.toast-container').length) {
        $('body').append('<div class="toast-container"></div>');
    }

    $('.toast-container').append(toast);
    const toastEl = $('.toast-container .toast:last');
    const bsToast = new bootstrap.Toast(toastEl[0]);
    bsToast.show();

    setTimeout(function () {
        toastEl.remove();
    }, 5000);
}

// RSS Feed handlers
$(document).on('click', '.rss-preset', function (e) {
    e.preventDefault();
    $('#rssFeedUrl').val($(this).data('url'));
});

// $('#fetchRssBtn').click(function () {
//     const rssUrl = $('#rssFeedUrl').val().trim();
//     const limit = $('#rssLimit').val() || 20;

//     if (!rssUrl) {
//         alert('Vui lòng nhập URL RSS feed');
//         return;
//     }

//     $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Đang tải...');

//     $.ajax({
//         url: '/admin/api/fetch-api-news',
//         method: 'POST',
//         contentType: 'application/json',
//         data: JSON.stringify({
//             source_type: 'rss',
//             rss_url: rssUrl,
//             limit: parseInt(limit)
//         }),
//         success: function (response) {
//             if (response.success) {
//                 displayRssArticles(response.data);
//                 showToast('Thành công', `Đã tải ${response.count} bài viết từ RSS`, 'success');
//             } else {
//                 alert('Lỗi: ' + response.error);
//             }
//         },
//         error: function (xhr) {
//             const error = xhr.responseJSON ? xhr.responseJSON.error : 'Không thể kết nối đến server';
//             alert('Lỗi: ' + error);
//         },
//         complete: function () {
//             $('#fetchRssBtn').prop('disabled', false).html('<i class="fas fa-download"></i> Tải bài');
//         }
//     });
// });

// function displayRssArticles(articles) {
//     if (!articles || articles.length === 0) {
//         $('#rssArticlesList').html('<p class="text-muted text-center">Không có bài viết nào</p>');
//         return;
//     }

//     let html = '<div class="row">';
//     articles.forEach((article, index) => {
//         html += `
//             <div class="col-md-6 mb-3">
//                 <div class="card">
//                     <div class="card-body">
//                         <h6 class="card-title">${article.title}</h6>
//                         <p class="card-text small text-muted">${article.summary.substring(0, 150)}...</p>
//                         <div class="d-flex justify-content-between align-items-center">
//                             <small class="text-muted"><i class="fas fa-calendar"></i> ${new Date(article.published_at).toLocaleString('vi-VN')}</small>
//                             <button class="btn btn-sm btn-primary save-rss-article" data-index="${index}">
//                                 <i class="fas fa-save"></i> Lưu
//                             </button>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         `;
//     });
//     html += '</div>';

//     $('#rssArticlesList').html(html);
//     window.rssArticlesData = articles;
// }

// API News handlers
// $('#fetchApiBtn').click(function () {
//     const apiUrl = $('#apiUrl').val().trim();
//     const apiKey = $('#apiKey').val().trim();
//     const country = $('#apiCountry').val();
//     const category = $('#apiCategory').val();
//     const limit = $('#apiLimit').val() || 20;

//     if (!apiKey) {
//         alert('Vui lòng nhập API key');
//         return;
//     }

//     $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Đang tải...');

//     $.ajax({
//         url: '/admin/api/fetch-api-news',
//         method: 'POST',
//         contentType: 'application/json',
//         data: JSON.stringify({
//             source_type: 'api',
//             api_url: apiUrl,
//             api_key: apiKey,
//             country: country,
//             category: category,
//             limit: parseInt(limit)
//         }),
//         success: function (response) {
//             if (response.success) {
//                 displayApiArticles(response.data);
//                 showToast('Thành công', `Đã tải ${response.count} bài viết từ API`, 'success');
//             } else {
//                 alert('Lỗi: ' + response.error);
//             }
//         },
//         error: function (xhr) {
//             const error = xhr.responseJSON ? xhr.responseJSON.error : 'Không thể kết nối đến server';
//             alert('Lỗi: ' + error);
//         },
//         complete: function () {
//             $('#fetchApiBtn').prop('disabled', false).html('<i class="fas fa-download"></i> Tải bài từ API');
//         }
//     });
// });

// function displayApiArticles(articles) {
//     if (!articles || articles.length === 0) {
//         $('#apiArticlesList').html('<p class="text-muted text-center">Không có bài viết nào</p>');
//         return;
//     }

//     let html = '<div class="row">';
//     articles.forEach((article, index) => {
//         html += `
//             <div class="col-md-6 mb-3">
//                 <div class="card">
//                     ${article.thumbnail ? `<img src="${article.thumbnail}" class="card-img-top" alt="thumbnail" style="height: 200px; object-fit: cover;">` : ''}
//                     <div class="card-body">
//                         <h6 class="card-title">${article.title}</h6>
//                         <p class="card-text small text-muted">${article.summary.substring(0, 150)}...</p>
//                         <div class="d-flex justify-content-between align-items-center">
//                             <small class="text-muted"><i class="fas fa-calendar"></i> ${new Date(article.published_at).toLocaleString('vi-VN')}</small>
//                             <button class="btn btn-sm btn-primary save-api-article" data-index="${index}">
//                                 <i class="fas fa-save"></i> Lưu
//                             </button>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         `;
//     });
//     html += '</div>';

//     $('#apiArticlesList').html(html);
//     window.apiArticlesData = articles;
// }

// Save RSS article
// $(document).on('click', '.save-rss-article', function () {
//     const index = $(this).data('index');
//     const article = window.rssArticlesData[index];

//     if (!article) {
//         alert('Không tìm thấy bài viết');
//         return;
//     }

//     // TODO: Show modal to select category and status, then save
//     console.log('Save RSS article:', article);
//     alert('Chức năng lưu bài sẽ được hoàn thiện sau. Bài viết: ' + article.title);
// });

// // Save API article
// $(document).on('click', '.save-api-article', function () {
//     const index = $(this).data('index');
//     const article = window.apiArticlesData[index];

//     if (!article) {
//         alert('Không tìm thấy bài viết');
//         return;
//     }

//     // TODO: Show modal to select category and status, then save
//     console.log('Save API article:', article);
//     alert('Chức năng lưu bài sẽ được hoàn thiện sau. Bài viết: ' + article.title);
// });

// ===== Tag Autocomplete Functionality =====

let tagSuggestionsCache = [];

// Initialize tag autocomplete for an input
function initTagAutocomplete(inputSelector, suggestionsSelector) {
    const $input = $(inputSelector);
    const $suggestions = $(suggestionsSelector);

    // Load all tags on first use
    if (tagSuggestionsCache.length === 0) {
        loadAllTags();
    }

    $input.on('input', function () {
        const value = $(this).val();
        const cursorPos = this.selectionStart;
        const textBeforeCursor = value.substring(0, cursorPos);

        // Check if user is typing after a #
        const lastHashIndex = textBeforeCursor.lastIndexOf('#');
        if (lastHashIndex !== -1) {
            const textAfterHash = textBeforeCursor.substring(lastHashIndex + 1);
            // Check if there's no space or comma after the #
            if (!textAfterHash.match(/[\s,]/)) {
                const searchTerm = textAfterHash.toLowerCase();
                showTagSuggestions($input, $suggestions, searchTerm, lastHashIndex);
                return;
            }
        }

        // Hide suggestions if not typing after #
        hideTagSuggestions($suggestions);
    });

    $input.on('keydown', function (e) {
        const $activeSuggestion = $suggestions.find('.suggestion-item.active');

        if ($suggestions.is(':visible') && $activeSuggestion.length > 0) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const $next = $activeSuggestion.next('.suggestion-item');
                if ($next.length) {
                    $activeSuggestion.removeClass('active');
                    $next.addClass('active');
                } else {
                    $suggestions.find('.suggestion-item').first().addClass('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                const $prev = $activeSuggestion.prev('.suggestion-item');
                if ($prev.length) {
                    $activeSuggestion.removeClass('active');
                    $prev.addClass('active');
                } else {
                    $suggestions.find('.suggestion-item').last().addClass('active');
                }
            } else if (e.key === 'Enter' || e.key === 'Tab') {
                e.preventDefault();
                const tagName = $activeSuggestion.data('tag');
                if (tagName) {
                    insertTag($input, tagName);
                    hideTagSuggestions($suggestions);
                }
            } else if (e.key === 'Escape') {
                hideTagSuggestions($suggestions);
            }
        }
    });

    // Hide suggestions when clicking outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest(inputSelector).length && !$(e.target).closest(suggestionsSelector).length) {
            hideTagSuggestions($suggestions);
        }
    });
}

// Load all tags from API
async function loadAllTags() {
    try {
        const response = await fetch('/admin/api/tags');
        const result = await response.json();
        if (result.success) {
            tagSuggestionsCache = result.data.map(tag => tag.name);
        }
    } catch (error) {
        console.error('Lỗi tải tags:', error);
    }
}

// Show tag suggestions
function showTagSuggestions($input, $suggestions, searchTerm, hashIndex) {
    if (!searchTerm) {
        // Show all tags if no search term
        const filteredTags = tagSuggestionsCache.slice(0, 10);
        renderSuggestions($input, $suggestions, filteredTags, hashIndex);
        return;
    }

    // Filter tags by search term
    const filteredTags = tagSuggestionsCache
        .filter(tag => tag.toLowerCase().includes(searchTerm))
        .slice(0, 10);

    renderSuggestions($input, $suggestions, filteredTags, hashIndex);
}

// Render suggestions
function renderSuggestions($input, $suggestions, tags, hashIndex) {
    if (tags.length === 0) {
        hideTagSuggestions($suggestions);
        return;
    }

    let html = '<div class="suggestion-list">';
    tags.forEach((tag, index) => {
        html += `<div class="suggestion-item ${index === 0 ? 'active' : ''}" data-tag="${tag}">#${tag}</div>`;
    });
    html += '</div>';

    $suggestions.html(html).show();

    // Handle click on suggestion
    $suggestions.off('click', '.suggestion-item').on('click', '.suggestion-item', function () {
        const tagName = $(this).data('tag');
        insertTag($input, tagName);
        hideTagSuggestions($suggestions);
    });
}

// Insert tag into input
function insertTag($input, tagName) {
    const value = $input.val();
    const cursorPos = $input[0].selectionStart;
    const textBeforeCursor = value.substring(0, cursorPos);

    const lastHashIndex = textBeforeCursor.lastIndexOf('#');
    if (lastHashIndex !== -1) {
        const beforeHash = value.substring(0, lastHashIndex);
        const afterCursor = value.substring(cursorPos);
        const newValue = beforeHash + '#' + tagName + ' ' + afterCursor;
        $input.val(newValue);

        // Set cursor position after inserted tag
        const newCursorPos = beforeHash.length + tagName.length + 2;
        $input[0].setSelectionRange(newCursorPos, newCursorPos);
        $input.focus();
    }
}

// Hide tag suggestions
function hideTagSuggestions($suggestions) {
    $suggestions.hide();
}

// Tour Tree View Manager
async function loadTourTree() {
    try {
        const response = await fetch('/admin/api/tour/tree');
        const result = await response.json();

        if (result.success && result.tree) {
            const treeContainer = $('#tourTreeContainer');
            treeContainer.empty();

            const html = renderTreeNode(result.tree);
            treeContainer.html(html);

            // Add click handlers for folder elements to toggle collapse
            treeContainer.find('.tree-folder-header').click(function () {
                const folder = $(this).parent();
                folder.toggleClass('collapsed');
                const icon = $(this).find('.folder-icon');
                if (folder.hasClass('collapsed')) {
                    icon.removeClass('fa-folder-open').addClass('fa-folder');
                } else {
                    icon.removeClass('fa-folder').addClass('fa-folder-open');
                }
            });
        } else {
            $('#tourTreeContainer').html('<div class="alert alert-danger">Không thể tải sơ đồ tour.</div>');
        }
    } catch (error) {
        console.error('Error in loadTourTree:', error);
        $('#tourTreeContainer').html('<div class="alert alert-danger">Lỗi kết nối máy chủ.</div>');
    }
}

function renderTreeNode(node) {
    if (node.type === 'leaf') {
        let statusBadge = '';
        if (node.status === 'published') {
            statusBadge = '<span class="badge bg-success small me-1">Đã xuất bản</span>';
        } else if (node.status === 'pending') {
            statusBadge = '<span class="badge bg-warning text-dark small me-1">Chờ duyệt</span>';
        } else {
            statusBadge = '<span class="badge bg-secondary small me-1">Nháp</span>';
        }

        return `
            <div class="tree-item py-1 px-3 d-flex align-items-center justify-content-between border-bottom border-light">
                <div class="d-flex align-items-center">
                    <i class="fas fa-umbrella-beach text-info me-2"></i>
                    <span class="fw-semibold text-dark">${escapeHtml(node.title)}</span>
                    <span class="text-muted ms-2" style="font-size: 11px;">(${node.duration_days} ngày)</span>
                </div>
                <div class="d-flex align-items-center">
                    ${statusBadge}
                    <span class="text-primary fw-bold me-3" style="font-size: 13px;">${new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(node.price_per_adult)}</span>
                </div>
            </div>
        `;
    } else if (node.type === 'composite') {
        let iconClass = 'fa-folder-open';
        let folderTypeClass = 'bg-primary-light text-primary';
        if (node.group_type === 'Địa điểm') {
            folderTypeClass = 'bg-success-light text-success';
        } else if (node.group_type === 'Danh mục') {
            folderTypeClass = 'bg-info-light text-info';
        }

        let childrenHtml = '';
        if (node.children && node.children.length > 0) {
            childrenHtml = node.children.map(child => renderTreeNode(child)).join('');
        } else {
            childrenHtml = '<div class="text-muted py-2 px-4 small">Thư mục trống</div>';
        }

        return `
            <div class="tree-folder my-2 shadow-sm rounded border border-light">
                <div class="tree-folder-header p-3 d-flex align-items-center justify-content-between bg-light cursor-pointer select-none">
                    <div class="d-flex align-items-center">
                        <i class="fas ${iconClass} folder-icon me-2 text-warning"></i>
                        <span class="fw-bold text-dark">${escapeHtml(node.group_name)}</span>
                        <span class="badge ${folderTypeClass} rounded-pill ms-2 small" style="font-size: 10px;">${node.group_type}</span>
                    </div>
                    <span class="badge bg-secondary rounded-pill small">${node.tour_count} bài viết</span>
                </div>
                <div class="tree-folder-content p-2 bg-white">
                    ${childrenHtml}
                </div>
            </div>
        `;
    }
    return '';
}

// Render gallery preview inside a container
function renderGalleryPreview(containerId, hiddenInputId, urls) {
    const container = $(containerId);
    container.empty();
    urls.forEach((url, index) => {
        container.append(`
            <div class="position-relative" style="width: 80px; height: 80px; border-radius: 4px; overflow: hidden; border: 1px solid #ddd;">
                <img src="${url}" style="width: 100%; height: 100%; object-fit: cover;">
                <button type="button" class="btn btn-danger btn-sm p-0 position-absolute d-flex align-items-center justify-content-center" 
                        style="top: 2px; right: 2px; width: 18px; height: 18px; font-size: 10px; border-radius: 50%;" 
                        onclick="removeGalleryImage('${containerId}', '${hiddenInputId}', ${index})">
                    &times;
                </button>
            </div>
        `);
    });
}

// Remove gallery image from the array and re-render
window.removeGalleryImage = function(containerId, hiddenInputId, index) {
    const input = $(hiddenInputId);
    let urls = [];
    try {
        urls = JSON.parse(input.val() || '[]');
    } catch(e) {}
    urls.splice(index, 1);
    input.val(JSON.stringify(urls));
    renderGalleryPreview(containerId, hiddenInputId, urls);
};
