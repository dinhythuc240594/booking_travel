$(document).ready(function () {
    const path = window.location.pathname;

    // Nếu đang ở trang editor dashboard thì không chạy logic dashboard admin,
    // để tránh gọi các API chỉ dành cho admin (vd: /admin/api/tour/pending-articles)
    if (path.startsWith('/admin/editor-dashboard')) {
        return;
    }

    // // Check authentication
    // checkAuth();

    // Initialize chart
    initializeChart();

    // Load initial data cho dashboard admin
    // (editor dashboard sẽ dùng editor.js riêng)
    // loadPendingArticles();
    // loadAPIArticles(); // Không tự động load API articles
    loadStatistics();
    // loadHotArticles();

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

        // Load data for the section
        loadSectionData(section);
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

    // Fetch API articles
    $('#fetchAPIBtn').click(function () {
        fetchAPIArticles();
    });

    // Clear API filters
    $('#clearApiFilters').click(function () {
        clearAPIFilters();
    });

    // Apply filters on change
    $('#apiSource, #apiSearchInput, #apiSortBy, #apiPageSize').on('input change', function () {
        if (apiArticlesData.length > 0) {
            $('#apiCurrentPage').val(1);
            applyAPIFilters();
        }
    });

    // Pagination click
    $(document).on('click', '#apiPagination .page-link', function (e) {
        e.preventDefault();
        const page = parseInt($(this).data('page'));
        if (page && page > 0) {
            $('#apiCurrentPage').val(page);
            applyAPIFilters();
        }
    });

    // Approve article
    $(document).on('click', '.btn-approve', function () {
        const articleId = $(this).data('id');
        const articleType = $(this).data('type'); // 'international' hoặc undefined
        approveArticle(articleId, articleType);
    });

    // Save API article
    $(document).on('click', '.btn-save-api', function () {
        const articleData = JSON.parse($(this).data('article'));
        openSaveAPIArticleModal(articleData);
    });

    // Preview API article
    $(document).on('click', '.btn-preview-api', function () {
        const articleData = JSON.parse($(this).data('article'));
        previewAPIArticle(articleData);
    });

    // Reject article - mở modal
    $(document).on('click', '.btn-reject', function () {
        const articleId = $(this).data('id');
        const articleType = $(this).data('type');

        $('#rejectArticleId').val(articleId);
        $('#rejectArticleType').val(articleType || '');
        $('#rejectReason').val('');

        const modal = new bootstrap.Modal(document.getElementById('rejectArticleModal'));
        modal.show();
    });

    // Xử lý confirm reject từ modal
    $('#confirmRejectBtn').on('click', function () {
        const articleId = $('#rejectArticleId').val();
        const articleType = $('#rejectArticleType').val();
        const reason = $('#rejectReason').val().trim();

        if (!reason) {
            alert('Vui lòng nhập lý do từ chối');
            return;
        }

        // Đóng modal
        bootstrap.Modal.getInstance(document.getElementById('rejectArticleModal')).hide();

        // Gọi hàm reject
        rejectArticle(articleId, reason, articleType);
    });

    // Preview article
    $(document).on('click', '.btn-preview', function () {
        const articleId = $(this).data('id');
        const articleType = $(this).data('type'); // 'international' hoặc undefined
        previewArticle(articleId, articleType);
    });

    // // Edit international article
    // $(document).on('click', '.btn-edit[data-type="international"]', function () {
    //     const articleId = $(this).data('id');
    //     editInternationalArticle(articleId);
    // });

    // // Delete international article
    // $(document).on('click', '.btn-delete[data-type="international"]', function () {
    //     const articleId = $(this).data('id');
    //     if (confirm('Bạn có chắc muốn xóa bài viết này?')) {
    //         deleteInternationalArticle(articleId);
    //     }
    // });

    // // Submit international draft for approval
    // $(document).on('click', '.btn-submit[data-type="international"]', function () {
    //     const articleId = $(this).data('id');
    //     if (confirm('Bạn có chắc muốn gửi bài viết này để duyệt?')) {
    //         submitInternationalDraft(articleId);
    //     }
    // });

    // Modal approve/reject
    $('#approveBtn').click(function () {
        const articleId = $(this).data('id');
        const articleType = $(this).data('type'); // 'international' hoặc undefined
        approveArticle(articleId, articleType);
        $('#previewArticleModal').modal('hide');
    });

    $('#rejectBtn').click(function () {
        const articleId = $(this).data('id');
        const articleType = $(this).data('type'); // 'international' hoặc undefined
        const reason = prompt('Lý do từ chối:');
        if (reason) {
            rejectArticle(articleId, reason, articleType);
            $('#previewArticleModal').modal('hide');
        }
    });

    // Tag manager events
    $('#tagSearchInput').on('input', function () {
        const search = $(this).val().trim();
        loadTags(search);
    });

    $('#tagForm').on('submit', function (e) {
        e.preventDefault();
        saveTag();
    });

    $('#tagResetBtn').on('click', function () {
        resetTagForm();
    });

    // $(document).on('click', '.btn-edit-tag', function () {
    //     const tagId = $(this).data('id');
    //     const tagName = $(this).data('name');
    //     const tagSlug = $(this).data('slug');
    //     fillTagForm(tagId, tagName, tagSlug);
    // });

    // $(document).on('click', '.btn-delete-tag', function () {
    //     const tagId = $(this).data('id');
    //     const tagName = $(this).data('name');
    //     if (confirm(`Bạn có chắc muốn xóa hashtag "${tagName}"?`)) {
    //         deleteTag(tagId);
    //     }
    // });

    // loadHandlerAPI();

});

// Update page title based on section
function updatePageTitle(section) {
    const titles = {
        'dashboard': 'Dashboard',
        'pending': 'Bài viết chờ duyệt',
        'approved': 'Bài viết đã duyệt',
        'rejected': 'Bài viết bị từ chối',
        'location': 'Quản lý địa điểm',
        'users': 'Quản lý người dùng',
        'bookings': 'Quản lý Bookings',
        'statistics': 'Thống kê',
        'tour-tree': 'Thư mục bài viết'
    };
    $('#pageTitle').text(titles[section] || 'Dashboard');
}

// Load data for specific section
async function loadSectionData(section) {
    switch (section) {
        case 'pending':
            loadPendingArticles();
            break;
        case 'approved':
            loadApprovedArticles();
            break;
        case 'rejected':
            loadRejectedArticles();
            break;
        case 'location':
            loadLocations();
            break;
        case 'bookings':
            loadBookings();
            break;
        case 'tour-tree':
            loadTourTree();
            break;
        case 'dashboard':
            loadStatistics();
            // loadHotArticles();
            break;
        case 'tags-manager':
            loadTags();
            break;
        case 'settings':
            // Settings will be loaded by its own script in setting-section.html
            if (typeof loadSettings === 'function') {
                loadSettings();
            }
            break;
    }
}

// Load approved articles
async function loadApprovedArticles() {
    try {
        const response = await fetch('/admin/api/tour/approved-articles');
        const result = await response.json();

        if (result.success && result.data) {
            let html = '';
            result.data.forEach((article, index) => {
                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td><strong>${article.title}</strong></td>
                        <td>${article.author}</td>
                        <td><span class="badge bg-primary">${article.category_name_vi || article.category_name}</span></td>
                        <td>${article.date}</td>
                        <td><span class="badge bg-success">${article.views} lượt xem</span></td>
                        <td>
                            <button class="btn btn-sm btn-primary btn-preview" data-id="${article.tour_id}" title="Xem">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            if (result.data.length === 0) {
                html = '<tr><td colspan="7" class="text-center text-muted">Không có bài viết nào</td></tr>';
            }

            $('#approved').find('tbody').html(html);
        }
    } catch (error) {
        console.error('Lỗi tải bài viết đã duyệt:', error);
    }
}

// Load rejected articles
async function loadRejectedArticles() {
    try {
        const response = await fetch('/admin/api/tour/rejected-articles');
        const result = await response.json();

        if (result.success && result.data) {
            let html = '';
            result.data.forEach((article, index) => {

                const rejectedBy = article.rejected_by || 'N/A';
                const rejectedAt = article.rejected_at || article.date;
                const hasReason = article.rejection_reason && article.rejection_reason.trim() !== '';

                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>
                            <strong>${escapeHtml(article.title)}</strong>
                        </td>
                        <td>${escapeHtml(article.author)}</td>
                        <td><span class="badge bg-primary">${escapeHtml(article.category_name_vi || article.category_name)}</span></td>
                        <td>${article.date}</td>
                        <td>
                            <small>${escapeHtml(rejectedBy)}</small><br>
                            <small class="text-muted">${rejectedAt}</small>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary btn-preview" data-id="${article.tour_id}" data-type="${article.type || ''}" title="Xem">
                                <i class="fas fa-eye"></i>
                            </button>
                            ${hasReason ? `
                                <button class="btn btn-sm btn-danger btn-view-rejection" 
                                        data-title="${escapeHtml(article.title)}"
                                        data-reason="${escapeHtml(article.rejection_reason)}"
                                        data-rejected-by="${escapeHtml(rejectedBy)}"
                                        data-rejected-at="${rejectedAt}"
                                        title="Xem lý do từ chối">
                                    <i class="fas fa-info-circle"></i> Lý do
                                </button>
                            ` : ''}
                        </td>
                    </tr>
                `;
            });

            if (result.data.length === 0) {
                html = '<tr><td colspan="7" class="text-center text-muted">Không có bài viết nào</td></tr>';
            }

            $('#rejected').find('tbody').html(html);
        }
    } catch (error) {
        console.error('Lỗi tải bài viết bị từ chối:', error);
    }
}

async function loadLocations() {
    try {
        const response = await fetch(`/admin/api/locations`, {
            method: 'GET',
            headers: {
                // 'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();
        if (result.success) {
            const locations = result.locations;
            let html = '';
            locations.forEach(location => {
                html += `
                <tr>
                    <td>${location.location_id}</td>
                    <td>
                        <strong>${escapeHtml(location.name)}</strong><br>
                        <small class="text-muted">Slug: ${escapeHtml(location.slug || '')}</small>
                    </td>
                    <td>${escapeHtml(location.city)}</td>
                    <td><img src="${escapeHtml(location.image_url)}" width="100px" height="100px"></td>
                    <td>
                        <button class="edit-location btn btn-sm btn-primary" data-id="${location.location_id}" title="Sửa">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="delete-location btn btn-sm btn-danger" data-id="${location.location_id}" title="Xóa">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            });

            if (locations.length === 0) {
                html = '<tr><td colspan="5" class="text-center text-muted">Không có địa điểm nào</td></tr>';
            }

            $('#location').find('tbody').html(html);
        }
    } catch (error) {
        console.error('Lỗi tải địa điểm:', error);
    }
}

// Xem lý do từ chối
$(document).on('click', '.btn-view-rejection', function () {
    const title = $(this).data('title');
    const reason = $(this).data('reason');
    const rejectedBy = $(this).data('rejected-by');
    const rejectedAt = $(this).data('rejected-at');

    $('#rejectionArticleTitle').text(title);
    $('#rejectionRejectedBy').text(rejectedBy);
    $('#rejectionRejectedAt').text(rejectedAt);
    $('#rejectionReasonText').text(reason || 'Không có lý do từ chối');

    const modal = new bootstrap.Modal(document.getElementById('rejectionReasonModal'));
    modal.show();
});

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/admin/api/statistics');
        const result = await response.json();

        if (result.success && result.data) {
            const stats = result.data;
            $('#statPending').text(stats.pending);
            $('#statApproved').text(stats.approved);
            $('#statRejected').text(stats.rejected);
            $('#apiApproved').text(stats.api_approved);
            $('#apiRejected').text(stats.api_rejected);
            $('#apiPending').text(stats.api_pending);
            $('#pendingCount').text(stats.pending);
            $('#rejectedCount').text(stats.rejected);

            // Update notification bell if elements exist
            const $notifCount = $('#notificationCount');
            const $notifList = $('#notificationList');
            const $notifEmpty = $('#notificationEmpty');
            if ($notifCount.length && $notifList.length && $notifEmpty.length) {
                const totalAlerts = (stats.pending || 0) + (stats.rejected || 0);
                $notifCount.text(totalAlerts);

                let html = '';
                if (stats.pending > 0) {
                    html += `
                        <div class="dropdown-item d-flex justify-content-between align-items-center">
                            <div>
                                <div><strong>${stats.pending}</strong> bài viết <span class="text-warning">chờ duyệt</span></div>
                                <small class="text-muted">Kiểm tra trong mục "Bài chờ duyệt".</small>
                            </div>
                            <span class="badge bg-warning text-dark ms-2"><i class="fas fa-clock"></i></span>
                        </div>
                    `;
                }
                if (stats.rejected > 0) {
                    html += `
                        <div class="dropdown-item d-flex justify-content-between align-items-center">
                            <div>
                                <div><strong>${stats.rejected}</strong> bài viết <span class="text-danger">bị từ chối</span></div>
                                <small class="text-muted">Xem chi tiết ở mục "Bài từ chối".</small>
                            </div>
                            <span class="badge bg-danger ms-2"><i class="fas fa-times"></i></span>
                        </div>
                    `;
                }
                if (stats.api > 0) {
                    html += `
                        <div class="dropdown-item d-flex justify-content-between align-items-center">
                            <div>
                                <div><strong>${stats.api}</strong> bài viết mới từ <span class="text-info">API</span></div>
                                <small class="text-muted">Kiểm tra tab "Bài viết từ API".</small>
                            </div>
                            <span class="badge bg-info ms-2"><i class="fas fa-cloud"></i></span>
                        </div>
                    `;
                }

                if (html) {
                    $notifEmpty.hide();
                    $notifList.html(html);
                } else {
                    $notifList.empty();
                    $notifEmpty.show().text('Chưa có thông báo mới.');
                }
            }
        }

        // Fetch bookings statistics
        const bookingsResponse = await fetch('/admin/api/bookings/statistics');
        const bookingsResult = await bookingsResponse.json();

        if (bookingsResult.success && bookingsResult.data) {
            const bookingStats = bookingsResult.data;
            $('#statBookingTotal').text(bookingStats.total_bookings);
            $('#statBookingRevenue').text(new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(bookingStats.total_revenue));
            $('#statBookingPending').text(bookingStats.pending_count);
            $('#statBookingCompleted').text(bookingStats.completed_count);

            // Render Recent Bookings
            let recentHtml = '';
            bookingStats.recent_bookings.forEach(booking => {
                let badgeClass = 'bg-secondary';
                let statusLabel = booking.status;
                if (booking.status === 'pending') {
                    badgeClass = 'bg-warning text-dark';
                    statusLabel = 'Chờ duyệt';
                } else if (booking.status === 'confirmed') {
                    badgeClass = 'bg-primary';
                    statusLabel = 'Đã duyệt';
                } else if (booking.status === 'completed') {
                    badgeClass = 'bg-success';
                    statusLabel = 'Hoàn thành';
                } else if (booking.status === 'cancelled') {
                    badgeClass = 'bg-danger';
                    statusLabel = 'Đã hủy';
                }

                recentHtml += `
                    <tr>
                        <td>#${booking.id}</td>
                        <td><strong>${escapeHtml(booking.userName)}</strong></td>
                        <td><strong>${escapeHtml(booking.tourTitle)}</strong></td>
                        <td><strong class="text-primary">${new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(booking.totalPrice)}</strong></td>
                        <td><span class="badge ${badgeClass}">${statusLabel}</span></td>
                        <td>${booking.createdAt}</td>
                    </tr>
                `;
            });
            if (bookingStats.recent_bookings.length === 0) {
                recentHtml = '<tr><td colspan="6" class="text-center text-muted">Chưa có giao dịch đặt tour nào</td></tr>';
            }
            $('#recentBookingsTableBody').html(recentHtml);

            // Render/Update Booking Chart
            initializeBookingChart();
        }

    } catch (error) {
        console.error('Lỗi tải thống kê:', error);
    }
}

// =========================
// Tag Manager
// =========================

let tagsCache = [];

async function loadTags(search = '') {
    try {
        let url = '/admin/api/tags';
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url);
        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
            tagsCache = result.data;
            renderTagsTable(tagsCache);
        } else {
            renderTagsTable([]);
        }
    } catch (error) {
        console.error('Lỗi tải hashtag:', error);
        renderTagsTable([]);
    }
}

function renderTagsTable(tags) {
    const $tbody = $('#tagsTableBody');
    const $badge = $('#tagsTotalBadge');

    if (!$tbody.length) {
        return;
    }

    if (!tags || tags.length === 0) {
        $tbody.html(`
            <tr>
                <td colspan="4" class="text-center text-muted">Chưa có hashtag nào.</td>
            </tr>
        `);
        if ($badge.length) {
            $badge.text('0 hashtag');
        }
        return;
    }

    let html = '';
    tags.forEach((tag, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td><code>#${tag.name}</code></td>
                <td>${tag.slug}</td>
                <td>
                    <button class="btn btn-sm btn-warning btn-edit-tag" 
                            data-id="${tag.id}" 
                            data-name="${tag.name}" 
                            data-slug="${tag.slug}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger btn-delete-tag ms-1" 
                            data-id="${tag.id}" 
                            data-name="${tag.name}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    $tbody.html(html);
    if ($badge.length) {
        $badge.text(`${tags.length} hashtag`);
    }
}

// Load pending articles
async function loadPendingArticles() {
    try {
        const response = await fetch('/admin/api/tour/pending-articles');
        const result = await response.json();

        if (result.success && result.data) {
            let html = '';
            result.data.forEach((article, index) => {
                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td><strong>${article.title}</strong></td>
                        <td>${article.author}</td>
                        <td><span class="badge bg-primary">${article.category_name_vi || article.category_name}</span></td>
                        <td>${article.date}</td>
                        <td>
                            <button class="btn btn-sm btn-info btn-action btn-preview" data-bs-target="#previewArticleModal" data-id="${article.tour_id}" title="Xem trước">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-success btn-action btn-approve" data-id="${article.tour_id}" title="Duyệt">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="btn btn-sm btn-danger btn-action btn-reject" data-id="${article.tour_id}" title="Từ chối">
                                <i class="fas fa-times"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            if (result.data.length === 0) {
                html = '<tr><td colspan="6" class="text-center text-muted">Không có bài viết nào chờ duyệt</td></tr>';
            }

            $('#pendingtourTable').html(html);
        }
    } catch (error) {
        console.error('Lỗi tải bài viết chờ duyệt:', error);
        $('#pendingtourTable').html('<tr><td colspan="6" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>');
    }
}

// Fetch API articles
async function fetchAPIArticles() {
    const btn = $('#fetchAPIBtn');
    btn.prop('disabled', true);
    btn.html('<i class="fas fa-spinner fa-spin"></i> Đang tải...');

    try {
        // Lấy thông tin từ form
        const limit = parseInt($('#apiLimit').val()) || 20;
        const startDate = $('#apiStartDate').val();
        const endDate = $('#apiEndDate').val();
        const country = $('#apiCountry').val();
        const category = $('#apiCategory').val();

        // Có thể thêm form để nhập API key và URL
        const apiKey = prompt('Nhập API Key (để trống nếu dùng mock data):') || '';
        const apiUrl = 'https://newsapi.org/v2/top-headlines';

        const response = await fetch('/admin/api/fetch-api-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey,
                api_url: apiUrl,
                limit: limit,
                start_date: startDate,
                end_date: endDate,
                country: country,
                category: category
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast('Thành công', result.message || 'Đã lấy bài viết mới từ API', 'success');
            // Hiển thị kết quả và áp dụng filter
            displayAPIArticles(result.data);
            $('#apiFilterResults').show();
            applyAPIFilters();
        } else {
            showToast('Lỗi', result.error || 'Không thể lấy bài viết từ API', 'warning');
        }
    } catch (error) {
        console.error('Lỗi fetch API:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi lấy bài viết từ API', 'warning');
    } finally {
        btn.prop('disabled', false);
        btn.html('<i class="fas fa-sync-alt"></i> Lấy dữ liệu từ API');
    }
}

// Store API articles data
let apiArticlesData = [];

// Display API articles
function displayAPIArticles(articles) {
    apiArticlesData = articles;
    applyAPIFilters();
}

// Apply filters to API articles
function applyAPIFilters() {
    let filtered = [...apiArticlesData];

    // Filter by source
    const sourceFilter = $('#apiSource').val().toLowerCase();
    if (sourceFilter) {
        filtered = filtered.filter(article =>
            article.source.toLowerCase().includes(sourceFilter)
        );
    }

    // Filter by keyword
    const keywordFilter = $('#apiSearchInput').val().toLowerCase();
    if (keywordFilter) {
        filtered = filtered.filter(article =>
            article.title.toLowerCase().includes(keywordFilter) ||
            (article.summary && article.summary.toLowerCase().includes(keywordFilter)) ||
            (article.content && article.content.toLowerCase().includes(keywordFilter))
        );
    }

    // Sort
    const sortBy = $('#apiSortBy').val();
    switch (sortBy) {
        case 'published_desc':
            filtered.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
            break;
        case 'published_asc':
            filtered.sort((a, b) => new Date(a.published_at) - new Date(b.published_at));
            break;
        case 'title_asc':
            filtered.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'title_desc':
            filtered.sort((a, b) => b.title.localeCompare(a.title));
            break;
        case 'source_asc':
            filtered.sort((a, b) => a.source.localeCompare(b.source));
            break;
    }

    // Pagination
    const pageSize = parseInt($('#apiPageSize').val()) || 20;
    const currentPage = parseInt($('#apiCurrentPage').val()) || 1;
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginated = filtered.slice(startIndex, endIndex);

    // Display
    renderAPIArticlesTable(paginated);

    // Update info
    $('#apiResultsInfo').text(`Hiển thị ${startIndex + 1}-${Math.min(endIndex, filtered.length)} trong tổng số ${filtered.length} bài viết`);

    // Pagination
    renderAPIPagination(filtered.length, pageSize, currentPage);
}

// Render API articles table
function renderAPIArticlesTable(articles) {
    let html = '';

    if (articles.length === 0) {
        html = '<tr><td colspan="7" class="text-center text-muted">Không có bài viết nào phù hợp</td></tr>';
    } else {
        articles.forEach((article, index) => {
            const date = article.published_at ? new Date(article.published_at).toLocaleString('vi-VN') : 'N/A';
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${article.title}</strong></td>
                    <td><span class="badge bg-info">${article.source}</span></td>
                    <td><span class="badge bg-primary">${article.category_name || 'N/A'}</span></td>
                    <td>${article.author || 'N/A'}</td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-sm btn-info btn-action btn-preview-api" data-article='${JSON.stringify(article).replace(/'/g, "&#39;")}' title="Xem trước">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-success btn-action btn-save-api" data-article='${JSON.stringify(article).replace(/'/g, "&#39;")}' title="Lưu bài viết">
                            <i class="fas fa-save"></i> Lưu
                        </button>
                    </td>
                </tr>
            `;
        });
    }

    $('#apiArticlesTable').html(html);
}

// Render pagination
function renderAPIPagination(total, pageSize, currentPage) {
    const totalPages = Math.ceil(total / pageSize);
    let html = '';

    if (totalPages <= 1) {
        $('#apiPagination').html('');
        return;
    }

    // Previous button
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page="${currentPage - 1}">Trước</a>
    </li>`;

    // Page numbers
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);

    if (endPage - startPage < maxPages - 1) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    if (startPage > 1) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (startPage > 2) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
            <a class="page-link" href="#" data-page="${i}">${i}</a>
        </li>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
    }

    // Next button
    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page="${currentPage + 1}">Sau</a>
    </li>`;

    $('#apiPagination').html(html);

    // Store current page
    $('<input>').attr({
        type: 'hidden',
        id: 'apiCurrentPage',
        value: currentPage
    }).appendTo('body');
}

// Clear API filters
function clearAPIFilters() {
    $('#apiSource').val('');
    $('#apiSearchInput').val('');
    $('#apiSortBy').val('published_desc');
    $('#apiPageSize').val(20);
    $('#apiCurrentPage').val(1);
    applyAPIFilters();
}

// Approve article
async function approveArticle(articleId, articleType) {
    if (confirm('Bạn có chắc muốn duyệt bài viết này?')) {
        showSpinner();

        try {
            // Xác định route dựa trên loại bài viết
            const route = articleType === 'international'
                ? `/admin/international/${articleId}/approve`
                : `/admin/api/tour/article/${articleId}/approve`;

            const response = await fetch(route, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            hideSpinner();

            if (response.ok) {
                showToast('Thành công', 'Bài viết đã được duyệt và xuất bản', 'success');

                // Remove from table
                $(`button[data-id="${articleId}"]`).closest('tr').fadeOut(function () {
                    $(this).remove();
                });

                // Reload stats
                loadStatistics();
            } else {
                showToast('Lỗi', result.error || 'Không thể duyệt bài viết', 'warning');
            }
        } catch (error) {
            hideSpinner();
            console.error('Lỗi duyệt bài viết:', error);
            showToast('Lỗi', 'Có lỗi xảy ra khi duyệt bài viết', 'warning');
        }
    }
}

// Open save API article modal
async function openSaveAPIArticleModal(articleData) {
    // Load categories
    try {
        const response = await fetch('/admin/api/categories');
        const result = await response.json();

        let categoryOptions = '<option value="">-- Chọn danh mục --</option>';
        if (result.success && result.data) {
            result.data.forEach(cat => {
                categoryOptions += `<option value="${cat.id}">${cat.name}</option>`;
            });
        }

        $('#saveAPICategory').html(categoryOptions);
    } catch (error) {
        console.error('Lỗi tải danh mục:', error);
    }

    // Set article data
    $('#saveAPIArticleData').val(JSON.stringify(articleData));
    $('#saveAPITitle').val(articleData.title);
    $('#saveAPISummary').val(articleData.summary || '');
    $('#saveAPIStatus').val('draft'); // Default to draft

    const modal = new bootstrap.Modal(document.getElementById('saveAPIArticleModal'));
    modal.show();
}



// Preview API article
function previewAPIArticle(articleData) {
    const content = `
        <div class="article-preview">
            ${articleData.thumbnail ? `<img src="${articleData.thumbnail}" alt="${articleData.title}" style="width: 100%; border-radius: 8px; margin-bottom: 20px;">` : ''}
            <h3>${articleData.title}</h3>
            <div class="mb-3">
                <span class="badge bg-info">${articleData.source}</span>
                <small class="text-muted ms-2">Bởi ${articleData.author || 'Unknown'} - ${new Date(articleData.published_at).toLocaleString('vi-VN')}</small>
            </div>
            <div class="mb-3">
                <strong>Tóm tắt:</strong>
                <p>${articleData.summary || 'N/A'}</p>
            </div>
            <div>
                <strong>Nội dung:</strong>
                <div>${articleData.content || articleData.summary || 'N/A'}</div>
            </div>
            ${articleData.source_url ? `<div class="mt-3"><a href="${articleData.source_url}" target="_blank" class="btn btn-sm btn-outline-primary">Xem bài gốc</a></div>` : ''}
        </div>
    `;

    $('#previewContent').html(content);

    const modal = new bootstrap.Modal(document.getElementById('previewAPIArticleModal'));
    modal.show();
}

// Reject article
async function rejectArticle(articleId, reason, articleType) {
    showSpinner();

    try {
        // Xác định route dựa trên loại bài viết
        const route = articleType === 'international'
            ? `/admin/international/${articleId}/reject`
            : `/admin/api/tour/article/${articleId}/reject`;

        const response = await fetch(route, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: reason
            })
        });

        const result = await response.json();
        hideSpinner();

        if (response.ok && result.success) {
            showToast('Thành công', 'Bài viết đã bị từ chối và email đã được gửi đến tác giả', 'success');

            // Remove from table
            $(`button[data-id="${articleId}"]`).closest('tr').fadeOut(function () {
                $(this).remove();
            });

            // Reload stats
            loadStatistics();
        } else {
            showToast('Lỗi', result.error || 'Không thể từ chối bài viết', 'warning');
        }
    } catch (error) {
        hideSpinner();
        console.error('Lỗi từ chối bài viết:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi từ chối bài viết', 'warning');
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, function (m) { return map[m]; });
}

// Preview article
async function previewArticle(articleId, articleType) {
    try {
        // Fetch article data from API - sử dụng endpoint phù hợp với loại bài viết
        const apiEndpoint = articleType === 'international'
            ? `/admin/api/international-article/${articleId}`
            : `/admin/api/tour/article/${articleId}`;
        const response = await fetch(apiEndpoint);
        const result = await response.json();
        if (result.success) {
            const article = result.data;

            // Prepare images
            let images = [];
            if (Array.isArray(article.images)) {
                images = article.images.filter(img => typeof img === 'string' && img.trim() !== '');
            }
            if (images.length === 0) {
                const fallbackImg = article.thumbnail;
                if (fallbackImg) {
                    images = [fallbackImg];
                } else {
                    images = ['https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&auto=format&fit=crop&q=80'];
                }
            }

            const isDefaultImage = (url) => {
                return !url || url.includes("photo-1500530855697-b586d89ba3ee");
            };

            const hasCustomImages = images.length > 0 && !images.every(isDefaultImage);

            let displayImages = [...images];
            if (!hasCustomImages) {
                const fallbackImages = [
                    "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&auto=format&fit=crop&q=80",
                    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&auto=format&fit=crop&q=80",
                    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
                    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=80"
                ];

                let fbIdx = 0;
                while (displayImages.length < 5) {
                    displayImages.push(fallbackImages[fbIdx % fallbackImages.length]);
                    fbIdx++;
                }
            }

            displayImages = displayImages.filter(img => img !== "");
            const displayImagesJson = JSON.stringify(displayImages);

            // Generate gallery HTML dynamically based on displayImages count
            const len = displayImages.length;
            let galleryHtml = '';
            
            if (len === 1) {
                galleryHtml = `
                    <div class="gallery-grid" style="grid-template-columns: 1fr;">
                        <div class="gallery-item gallery-large" onclick="openLightbox(0)">
                            <img src="${escapeHtml(displayImages[0])}" alt="Image 1">
                        </div>
                    </div>
                `;
            } else if (len === 2) {
                galleryHtml = `
                    <div class="gallery-grid" style="grid-template-columns: 1fr 1fr;">
                        <div class="gallery-item" onclick="openLightbox(0)">
                            <img src="${escapeHtml(displayImages[0])}" alt="Image 1">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(1)">
                            <img src="${escapeHtml(displayImages[1])}" alt="Image 2">
                        </div>
                        <button class="gallery-btn-all" onclick="openLightbox(0)">
                            <i class="fas fa-images text-cyan"></i> Xem tất cả hình ảnh
                        </button>
                    </div>
                `;
            } else if (len === 3) {
                galleryHtml = `
                    <div class="gallery-grid">
                        <div class="gallery-item gallery-large" onclick="openLightbox(0)">
                            <img src="${escapeHtml(displayImages[0])}" alt="Image 1">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(1)" style="grid-column: span 2;">
                            <img src="${escapeHtml(displayImages[1])}" alt="Image 2">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(2)" style="grid-column: span 2;">
                            <img src="${escapeHtml(displayImages[2])}" alt="Image 3">
                        </div>
                        <button class="gallery-btn-all" onclick="openLightbox(0)">
                            <i class="fas fa-images text-cyan"></i> Xem tất cả hình ảnh
                        </button>
                    </div>
                `;
            } else if (len === 4) {
                galleryHtml = `
                    <div class="gallery-grid">
                        <div class="gallery-item gallery-large" onclick="openLightbox(0)">
                            <img src="${escapeHtml(displayImages[0])}" alt="Image 1">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(1)">
                            <img src="${escapeHtml(displayImages[1])}" alt="Image 2">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(2)">
                            <img src="${escapeHtml(displayImages[2])}" alt="Image 3">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(3)" style="grid-column: span 2;">
                            <img src="${escapeHtml(displayImages[3])}" alt="Image 4">
                        </div>
                        <button class="gallery-btn-all" onclick="openLightbox(0)">
                            <i class="fas fa-images text-cyan"></i> Xem tất cả hình ảnh
                        </button>
                    </div>
                `;
            } else if (len >= 5) {
                galleryHtml = `
                    <div class="gallery-grid">
                        <div class="gallery-item gallery-large" onclick="openLightbox(0)">
                            <img src="${escapeHtml(displayImages[0])}" alt="Image 1">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(1)">
                            <img src="${escapeHtml(displayImages[1])}" alt="Image 2">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(2)">
                            <img src="${escapeHtml(displayImages[2])}" alt="Image 3">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(3)">
                            <img src="${escapeHtml(displayImages[3])}" alt="Image 4">
                        </div>
                        <div class="gallery-item" onclick="openLightbox(4)">
                            <img src="${escapeHtml(displayImages[4])}" alt="Image 5">
                        </div>
                        <button class="gallery-btn-all" onclick="openLightbox(0)">
                            <i class="fas fa-images text-cyan"></i> Xem tất cả hình ảnh
                        </button>
                    </div>
                `;
            }

            // Prepare start dates
            const startDates = Array.isArray(article.start_dates) && article.start_dates.length > 0
                ? article.start_dates
                : ["2026-06-25", "2026-07-02", "2026-07-09", "2026-07-16"];

            const startDatesJson = JSON.stringify(startDates);

            // Prepare categories, location, status
            const categoryName = article.category_name_vi || article.category_name || 'N/A';
            const locationName = article.location_name || 'Việt Nam';
            const durationDays = parseInt(article.duration_days || 1);
            const durationStr = `${durationDays} ngày ${Math.max(0, durationDays - 1)} đêm`;

            let statusBadge = '';
            if (article.status === 'draft') {
                statusBadge = '<span class="status-badge status-draft"><i class="fas fa-file-alt"></i> Bản nháp</span>';
            } else if (article.status === 'pending') {
                statusBadge = '<span class="status-badge status-pending"><i class="fas fa-clock"></i> Chờ duyệt</span>';
            } else if (article.status === 'approved' || article.status === 'published') {
                statusBadge = '<span class="status-badge status-approved"><i class="fas fa-check-circle"></i> Đã duyệt</span>';
            } else if (article.status === 'rejected') {
                statusBadge = '<span class="status-badge status-rejected"><i class="fas fa-times-circle"></i> Đã từ chối</span>';
            }

            const hotBadge = article.is_hot ? '<span class="status-badge status-hot"><i class="fas fa-fire"></i> Tin nóng</span>' : '';
            const featuredBadge = article.is_featured ? '<span class="status-badge status-featured"><i class="fas fa-star"></i> Nổi bật</span>' : '';

            // Calculate prices & widgets check
            const pricePerAdult = parseFloat(article.discount_price || article.price_per_adult || 0);
            const originalPrice = parseFloat(article.price_per_adult || 0);
            const hasDiscount = article.discount_price && parseFloat(article.discount_price) < originalPrice;
            const pricePerChild = parseFloat(article.price_per_child || Math.round(pricePerAdult * 0.7));

            // Check if it's a tour with pricing
            const hasBookingWidget = (pricePerAdult > 0 || originalPrice > 0);

            // Open preview in new window
            const previewWindow = window.open('', 'Xem bài viết', 'width=1100,height=800,scrollbars=yes');
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html lang="vi">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>${escapeHtml(article.title || 'Xem bài viết')}</title>
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body {
                            font-family: 'Outfit', sans-serif;
                            background: #f8fafc;
                            color: #0f172a;
                            line-height: 1.6;
                            padding: 32px 0;
                        }
                        .container {
                            max-width: 1200px;
                            margin: 0 auto;
                            padding: 0 24px;
                        }
                        .breadcrumb {
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            font-size: 13px;
                            color: #64748b;
                            margin-bottom: 16px;
                        }
                        .breadcrumb span {
                            transition: color 0.2s;
                        }
                        .breadcrumb span.active {
                            color: #0f172a;
                            font-weight: 500;
                        }
                        .breadcrumb i {
                            font-size: 10px;
                            color: #cbd5e1;
                        }
                        .header-section {
                            margin-bottom: 24px;
                        }
                        .badges-row {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 8px;
                            margin-bottom: 12px;
                        }
                        .status-badge {
                            display: inline-flex;
                            align-items: center;
                            gap: 6px;
                            padding: 6px 14px;
                            border-radius: 9999px;
                            font-size: 12px;
                            font-weight: 700;
                            letter-spacing: 0.02em;
                        }
                        .status-draft { background: #f1f5f9; color: #64748b; }
                        .status-pending { background: #fef3c7; color: #d97706; }
                        .status-approved { background: #d1fae5; color: #059669; }
                        .status-rejected { background: #fee2e2; color: #dc2626; }
                        .status-hot { background: #ffe4e6; color: #e11d48; }
                        .status-featured { background: #e0f2fe; color: #0284c7; }
                        .status-preview { background: #ecfeff; color: #0891b2; border: 1px dashed #22d3ee; }
                        .tour-title {
                            font-size: 32px;
                            font-weight: 800;
                            color: #0f172a;
                            line-height: 1.25;
                            letter-spacing: -0.02em;
                            margin-bottom: 16px;
                        }
                        .meta-row {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 24px;
                            font-size: 14px;
                            color: #475569;
                        }
                        .meta-item {
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        }
                        .text-cyan { color: #06b6d4; }
                        
                        /* Airbnb Gallery Grid */
                        .gallery-grid {
                            display: grid;
                            grid-template-columns: repeat(4, 1fr);
                            grid-template-rows: repeat(2, 1fr);
                            gap: 12px;
                            height: 420px;
                            border-radius: 24px;
                            overflow: hidden;
                            margin-bottom: 32px;
                            position: relative;
                        }
                        .gallery-item {
                            position: relative;
                            cursor: pointer;
                            overflow: hidden;
                            background: #e2e8f0;
                        }
                        .gallery-item img {
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                            transition: transform 0.5s ease;
                        }
                        .gallery-item:hover img {
                            transform: scale(1.03);
                        }
                        .gallery-item::after {
                            content: '';
                            position: absolute;
                            inset: 0;
                            background: rgba(0, 0, 0, 0.05);
                            opacity: 0;
                            transition: opacity 0.3s;
                        }
                        .gallery-item:hover::after {
                            opacity: 1;
                        }
                        .gallery-large {
                            grid-column: span 2;
                            grid-row: span 2;
                        }
                        .gallery-btn-all {
                            position: absolute;
                            bottom: 20px;
                            right: 20px;
                            background: rgba(255, 255, 255, 0.9);
                            border: 1px solid #e2e8f0;
                            color: #0f172a;
                            padding: 10px 18px;
                            border-radius: 12px;
                            font-size: 13px;
                            font-weight: 700;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
                            transition: all 0.2s;
                        }
                        .gallery-btn-all:hover {
                            background: #ffffff;
                            transform: scale(1.02);
                        }

                        /* Split Columns */
                        .main-layout {
                            margin-bottom: 48px;
                        }
                        .main-layout.two-cols {
                            display: grid;
                            grid-template-columns: 2fr 1fr;
                            gap: 32px;
                        }
                        .main-layout.one-col {
                            display: block;
                        }
                        .left-col {
                            display: flex;
                            flex-direction: column;
                            gap: 32px;
                        }
                        .card-box {
                            background: white;
                            border: 1px solid #e2e8f0;
                            border-radius: 24px;
                            padding: 32px;
                            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.01);
                        }
                        .section-title {
                            font-size: 18px;
                            font-weight: 800;
                            color: #0f172a;
                            margin-bottom: 20px;
                            padding-bottom: 12px;
                            border-bottom: 1px solid #f1f5f9;
                        }
                        .content-area {
                            font-size: 15px;
                            line-height: 1.8;
                            color: #334155;
                        }
                        .content-area img {
                            max-width: 100%;
                            height: auto;
                            border-radius: 12px;
                            margin: 20px 0;
                        }
                        .right-col {
                            position: sticky;
                            top: 24px;
                        }
                        .booking-widget {
                            background: white;
                            border: 1px solid #e2e8f0;
                            border-radius: 24px;
                            padding: 24px;
                            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
                        }
                        .widget-label {
                            font-size: 11px;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.05em;
                            color: #94a3b8;
                            margin-bottom: 8px;
                        }
                        .price-container {
                            display: flex;
                            align-items: baseline;
                            gap: 8px;
                            padding-bottom: 20px;
                            border-bottom: 1px solid #f1f5f9;
                            margin-bottom: 20px;
                        }
                        .price-current {
                            font-size: 28px;
                            font-weight: 800;
                            color: #06b6d4;
                        }
                        .price-original {
                            font-size: 14px;
                            color: #94a3b8;
                            text-decoration: line-through;
                        }
                        .price-unit {
                            font-size: 12px;
                            color: #94a3b8;
                        }
                        .form-group {
                            margin-bottom: 20px;
                        }
                        .select-input {
                            width: 100%;
                            background: #f8fafc;
                            border: 1px solid #e2e8f0;
                            border-radius: 12px;
                            padding: 12px 16px;
                            font-size: 14px;
                            font-weight: 600;
                            color: #0f172a;
                            outline: none;
                            cursor: pointer;
                            transition: border-color 0.2s;
                        }
                        .select-input:focus {
                            border-color: #06b6d4;
                        }
                        .passenger-row {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 12px 0;
                        }
                        .passenger-info {
                            display: flex;
                            flex-direction: column;
                        }
                        .passenger-title {
                            font-size: 14px;
                            font-weight: 700;
                            color: #0f172a;
                        }
                        .passenger-price {
                            font-size: 12px;
                            color: #64748b;
                        }
                        .counter-control {
                            display: flex;
                            align-items: center;
                            gap: 16px;
                        }
                        .counter-btn {
                            width: 32px;
                            height: 32px;
                            border-radius: 50%;
                            border: 1px solid #e2e8f0;
                            background: white;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 14px;
                            font-weight: 600;
                            color: #64748b;
                            transition: all 0.2s;
                        }
                        .counter-btn:hover:not(:disabled) {
                            border-color: #06b6d4;
                            color: #06b6d4;
                        }
                        .counter-btn:disabled {
                            opacity: 0.3;
                            cursor: not-allowed;
                        }
                        .counter-val {
                            font-size: 15px;
                            font-weight: 700;
                            color: #0f172a;
                            min-width: 16px;
                            text-align: center;
                        }
                        .total-box {
                            margin-top: 24px;
                            padding-top: 20px;
                            border-top: 1px solid #f1f5f9;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 24px;
                        }
                        .total-title {
                            font-size: 15px;
                            font-weight: 700;
                            color: #0f172a;
                        }
                        .total-price {
                            font-size: 22px;
                            font-weight: 850;
                            color: #06b6d4;
                        }
                        .btn-submit {
                            width: 100%;
                            background: linear-gradient(135deg, #06b6d4 0%, #2563eb 100%);
                            border: none;
                            color: white;
                            padding: 14px;
                            border-radius: 16px;
                            font-size: 14px;
                            font-weight: 700;
                            cursor: pointer;
                            box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
                            transition: all 0.2s;
                        }
                        .btn-submit:hover {
                            transform: translateY(-1px);
                            box-shadow: 0 6px 16px rgba(6, 182, 212, 0.25);
                        }
                        .btn-submit:active {
                            transform: translateY(0);
                        }
                        .disclaimer {
                            margin-top: 16px;
                            font-size: 11px;
                            color: #94a3b8;
                            text-align: center;
                            line-height: 1.5;
                        }

                        /* Lightbox */
                        .lightbox-modal {
                            position: fixed;
                            top: 0; left: 0; right: 0; bottom: 0;
                            background: rgba(9, 9, 11, 0.95);
                            backdrop-filter: blur(12px);
                            z-index: 9999;
                            display: none;
                            align-items: center;
                            justify-content: center;
                            user-select: none;
                        }
                        .lightbox-content {
                            max-width: 90%;
                            max-height: 80%;
                            position: relative;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                        }
                        .lightbox-img {
                            max-width: 100%;
                            max-height: 70vh;
                            object-fit: contain;
                            border-radius: 12px;
                            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                        }
                        .lightbox-btn {
                            position: absolute;
                            top: 50%;
                            transform: translateY(-50%);
                            background: rgba(255, 255, 255, 0.1);
                            color: white;
                            border: none;
                            width: 48px;
                            height: 48px;
                            border-radius: 50%;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 20px;
                            transition: background 0.2s, transform 0.2s;
                        }
                        .lightbox-btn:hover {
                            background: rgba(255, 255, 255, 0.2);
                            transform: translateY(-50%) scale(1.05);
                        }
                        .lightbox-prev { left: -72px; }
                        .lightbox-next { right: -72px; }
                        .lightbox-close {
                            position: absolute;
                            top: 24px; right: 24px;
                            background: rgba(255, 255, 255, 0.1);
                            color: white;
                            border: none;
                            width: 40px; height: 40px;
                            border-radius: 50%;
                            cursor: pointer;
                            font-size: 18px;
                            display: flex; align-items: center; justify-content: center;
                            transition: background 0.2s;
                        }
                        .lightbox-close:hover { background: rgba(255, 255, 255, 0.2); }
                        .lightbox-counter {
                            position: absolute;
                            top: 24px; left: 24px;
                            color: #a1a1aa;
                            font-size: 14px;
                            font-weight: 500;
                        }
                        .lightbox-thumbnails {
                            margin-top: 24px;
                            display: flex;
                            gap: 8px;
                            overflow-x: auto;
                            max-width: 100%;
                            padding: 4px;
                        }
                        .lightbox-thumb {
                            width: 60px; height: 40px;
                            object-fit: cover;
                            border-radius: 6px;
                            cursor: pointer;
                            border: 2px solid transparent;
                            opacity: 0.6;
                            transition: all 0.2s;
                        }
                        .lightbox-thumb.active {
                            border-color: #06b6d4;
                            opacity: 1;
                            transform: scale(1.05);
                        }

                        /* Alert Modal */
                        .preview-alert-overlay {
                            position: fixed;
                            inset: 0;
                            background: rgba(9, 9, 11, 0.6);
                            backdrop-filter: blur(4px);
                            display: none;
                            align-items: center;
                            justify-content: center;
                            z-index: 10000;
                        }
                        .preview-alert-box {
                            background: white;
                            border-radius: 24px;
                            padding: 32px;
                            max-width: 440px;
                            width: 90%;
                            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                            text-align: center;
                            animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                        }
                        @keyframes scaleIn {
                            from { transform: scale(0.9); opacity: 0; }
                            to { transform: scale(1); opacity: 1; }
                        }
                        .preview-alert-icon {
                            font-size: 48px;
                            color: #10b981;
                            margin-bottom: 16px;
                        }
                        .preview-alert-box h3 {
                            font-size: 18px;
                            font-weight: 800;
                            color: #0f172a;
                            margin-bottom: 8px;
                        }
                        .preview-alert-box p {
                            font-size: 14px;
                            color: #64748b;
                            margin-bottom: 12px;
                        }
                        .preview-alert-details {
                            background: #f8fafc;
                            border: 1px solid #e2e8f0;
                            border-radius: 12px;
                            padding: 16px;
                            font-size: 13px !important;
                            text-align: left;
                            color: #334155 !important;
                            margin-bottom: 16px !important;
                            line-height: 1.6;
                        }
                        .preview-alert-details span {
                            font-weight: 700;
                            color: #0f172a;
                        }
                        .preview-alert-info {
                            font-size: 11px;
                            color: #1e3a8a;
                            background: #eff6ff;
                            padding: 12px;
                            border-radius: 12px;
                            border-left: 3px solid #3b82f6;
                            text-align: left;
                            margin-bottom: 24px;
                            line-height: 1.4;
                        }
                        .preview-alert-close-btn {
                            width: 100%;
                            background: #0f172a;
                            color: white;
                            border: none;
                            padding: 12px;
                            border-radius: 12px;
                            font-size: 14px;
                            font-weight: 700;
                            cursor: pointer;
                            transition: background 0.2s;
                        }
                        .preview-alert-close-btn:hover {
                            background: #1e293b;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <!-- Breadcrumbs -->
                        <div class="breadcrumb">
                            <span>Trang chủ</span>
                            <i class="fas fa-chevron-right"></i>
                            <span>Tours</span>
                            <i class="fas fa-chevron-right"></i>
                            <span>${escapeHtml(categoryName)}</span>
                            <i class="fas fa-chevron-right"></i>
                            <span class="active">${escapeHtml(article.title || 'Không có tiêu đề')}</span>
                        </div>

                        <!-- Header -->
                        <div class="header-section">
                            <div class="badges-row">
                                ${statusBadge}
                                ${hotBadge}
                                ${featuredBadge}
                                <span class="status-badge status-preview"><i class="fas fa-eye"></i> Chế độ xem trước</span>
                            </div>
                            <h1 class="tour-title">${escapeHtml(article.title || 'Không có tiêu đề')}</h1>
                            <div class="meta-row">
                                <div class="meta-item"><i class="fas fa-map-marker-alt text-cyan"></i> <span>${escapeHtml(locationName)}</span></div>
                                <div class="meta-item"><i class="fas fa-clock"></i> <span>${escapeHtml(durationStr)}</span></div>
                                <div class="meta-item"><i class="fas fa-user"></i> <span>Người viết: ${escapeHtml(article.author_full_name || article.author || 'N/A')}</span></div>
                            </div>
                        </div>

                        <!-- Airbnb Gallery -->
                        ${galleryHtml}

                        <!-- Split columns -->
                        <div class="main-layout ${hasBookingWidget ? 'two-cols' : 'one-col'}">
                            <!-- Left Col -->
                            <div class="left-col">
                                <div class="card-box">
                                    <h2 class="section-title">Mô tả chi tiết</h2>
                                    <div class="content-area">
                                        ${article.content || '<p>Không có nội dung chi tiết cho tour này.</p>'}
                                    </div>
                                </div>
                            </div>

                            <!-- Right Col (Widget) -->
                            ${hasBookingWidget ? `
                            <div class="right-col">
                                <div class="booking-widget">
                                    <div class="widget-label">Giá chỉ từ</div>
                                    <div class="price-container">
                                        <span class="price-current" id="widget-display-price"></span>
                                        ${hasDiscount ? `<span class="price-original">${formatVND(originalPrice)}</span>` : ''}
                                        <span class="price-unit">/ khách</span>
                                    </div>

                                    <div class="form-group">
                                        <div class="widget-label">Chọn ngày khởi hành</div>
                                        <select class="select-input" id="select-departure">
                                            <!-- Hydrated dynamically -->
                                        </select>
                                    </div>

                                    <div class="form-group">
                                        <div class="widget-label">Số lượng hành khách</div>
                                        
                                        <div class="passenger-row">
                                            <div class="passenger-info">
                                                <span class="passenger-title">Người lớn</span>
                                                <span class="passenger-price" id="price-adult-label"></span>
                                            </div>
                                            <div class="counter-control">
                                                <button class="counter-btn" id="btn-minus-adult" onclick="updateAdults(-1)">-</button>
                                                <span class="counter-val" id="val-adults">1</span>
                                                <button class="counter-btn" id="btn-plus-adult" onclick="updateAdults(1)">+</button>
                                            </div>
                                        </div>

                                        <div class="passenger-row">
                                            <div class="passenger-info">
                                                <span class="passenger-title">Trẻ em</span>
                                                <span class="passenger-price" id="price-child-label"></span>
                                            </div>
                                            <div class="counter-control">
                                                <button class="counter-btn" id="btn-minus-child" onclick="updateChildren(-1)" disabled>-</button>
                                                <span class="counter-val" id="val-children">0</span>
                                                <button class="counter-btn" id="btn-plus-child" onclick="updateChildren(1)">+</button>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="total-box">
                                        <span class="total-title">Tổng cộng</span>
                                        <span class="total-price" id="val-total-price"></span>
                                    </div>

                                    <button class="btn-submit" onclick="submitBookingMock()">Đặt Tour Ngay</button>
                                    <div class="disclaimer">
                                        Nhân viên hỗ trợ sẽ liên hệ với quý khách qua số điện thoại để xác nhận hành trình sau khi đăng ký.
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>

                    <!-- Lightbox Modal -->
                    <div id="lightbox-modal" class="lightbox-modal">
                        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
                        <div class="lightbox-counter" id="lightbox-counter">1 / 5</div>
                        <div class="lightbox-content">
                            <button class="lightbox-btn lightbox-prev" onclick="changeImage(-1)"><i class="fas fa-chevron-left"></i></button>
                            <img id="lightbox-img" class="lightbox-img" src="" alt="Lightbox Image">
                            <button class="lightbox-btn lightbox-next" onclick="changeImage(1)"><i class="fas fa-chevron-right"></i></button>
                            <div class="lightbox-thumbnails" id="lightbox-thumbnails"></div>
                        </div>
                    </div>

                    <!-- Alert Modal -->
                    <div id="preview-alert-modal" class="preview-alert-overlay" onclick="closeAlertModal()">
                        <div class="preview-alert-box" onclick="event.stopPropagation()">
                            <div class="preview-alert-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <h3>Đặt Tour Giả Lập Thành Công!</h3>
                            <p>Đây là <strong>giao diện xem trước (preview)</strong> nội dung bài viết.</p>
                            <div class="preview-alert-details">
                                <div>Tour: <span id="alert-tour-title"></span></div>
                                <div>Ngày đi: <span id="alert-tour-date"></span></div>
                                <div>Hành khách: <span id="alert-tour-people"></span></div>
                                <div>Tổng tiền: <span id="alert-tour-price"></span></div>
                            </div>
                            <div class="preview-alert-info">
                                <i class="fas fa-info-circle"></i> Trên môi trường thực tế, hệ thống sẽ mở popup xác nhận thông tin, gửi yêu cầu đặt tour về hệ thống (trạng thái Chờ duyệt) và gửi email thông báo tự động.
                            </div>
                            <button class="preview-alert-close-btn" onclick="closeAlertModal()">Đóng xem trước</button>
                        </div>
                    </div>

                    <script>
                        // Injected state variables
                        const displayImages = ${displayImagesJson};
                        const startDates = ${startDatesJson};
                        const pricePerAdult = ${pricePerAdult};
                        const pricePerChild = ${pricePerChild};
                        const tourTitle = "${escapeHtml(article.title || 'Không có tiêu đề')}";

                        let adults = 1;
                        let children = 0;
                        let currentImageIndex = 0;

                        function formatVND(value) {
                            return new Intl.NumberFormat('vi-VN', {
                                style: 'currency',
                                currency: 'VND',
                                maximumFractionDigits: 0
                            }).format(value);
                        }

                        // Init static strings if widget is active
                        if (document.getElementById('widget-display-price')) {
                            document.getElementById('widget-display-price').textContent = formatVND(pricePerAdult);
                            document.getElementById('price-adult-label').textContent = formatVND(pricePerAdult) + ' / khách';
                            document.getElementById('price-child-label').textContent = 'Trẻ em: ' + formatVND(pricePerChild) + ' / khách';
                        }

                        // Populate start dates
                        const dateSelect = document.getElementById('select-departure');
                        if (dateSelect) {
                            startDates.forEach(dateStr => {
                                const option = document.createElement('option');
                                option.value = dateStr;
                                try {
                                    const dObj = new Date(dateStr);
                                    if (!isNaN(dObj)) {
                                        option.textContent = dObj.toLocaleDateString('vi-VN', {
                                            weekday: 'long',
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric'
                                        });
                                    } else {
                                        option.textContent = dateStr;
                                    }
                                } catch (err) {
                                    option.textContent = dateStr;
                                }
                                dateSelect.appendChild(option);
                            });
                        }

                        function updateAdults(change) {
                            adults = Math.max(1, adults + change);
                            document.getElementById('val-adults').textContent = adults;
                            document.getElementById('btn-minus-adult').disabled = (adults <= 1);
                            calculateTotal();
                        }

                        function updateChildren(change) {
                            children = Math.max(0, children + change);
                            document.getElementById('val-children').textContent = children;
                            document.getElementById('btn-minus-child').disabled = (children <= 0);
                            calculateTotal();
                        }

                        function calculateTotal() {
                            if (!document.getElementById('val-total-price')) return;
                            const total = (adults * pricePerAdult) + (children * pricePerChild);
                            document.getElementById('val-total-price').textContent = formatVND(total);
                        }

                        // Lightbox Actions
                        function openLightbox(index) {
                            currentImageIndex = index;
                            document.getElementById('lightbox-modal').style.display = 'flex';
                            updateLightboxContent();

                            const thumbContainer = document.getElementById('lightbox-thumbnails');
                            thumbContainer.innerHTML = '';
                            displayImages.forEach((imgSrc, idx) => {
                                const img = document.createElement('img');
                                img.src = imgSrc;
                                img.className = 'lightbox-thumb' + (idx === currentImageIndex ? ' active' : '');
                                img.onclick = () => {
                                    currentImageIndex = idx;
                                    updateLightboxContent();
                                };
                                thumbContainer.appendChild(img);
                            });
                        }

                        function closeLightbox() {
                            document.getElementById('lightbox-modal').style.display = 'none';
                        }

                        // Next/Prev gallery image
                        function changeImage(direction) {
                            currentImageIndex = (currentImageIndex + direction + displayImages.length) % displayImages.length;
                            updateLightboxContent();
                        }

                        function updateLightboxContent() {
                            document.getElementById('lightbox-img').src = displayImages[currentImageIndex];
                            document.getElementById('lightbox-counter').textContent = (currentImageIndex + 1) + ' / ' + displayImages.length;

                            const thumbs = document.querySelectorAll('.lightbox-thumb');
                            thumbs.forEach((thumb, idx) => {
                                if (idx === currentImageIndex) {
                                    thumb.classList.add('active');
                                    thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
                                } else {
                                    thumb.classList.remove('active');
                                }
                            });
                        }

                        document.addEventListener('keydown', (e) => {
                            const modal = document.getElementById('lightbox-modal');
                            if (modal.style.display === 'flex') {
                                if (e.key === 'ArrowRight') changeImage(1);
                                else if (e.key === 'ArrowLeft') changeImage(-1);
                                else if (e.key === 'Escape') closeLightbox();
                            }
                        });

                        function submitBookingMock() {
                            const dateEl = document.getElementById('select-departure');
                            const selectedDate = dateEl ? dateEl.value : 'Chưa chọn';
                            const totalVal = (adults * pricePerAdult) + (children * pricePerChild);

                            document.getElementById('alert-tour-title').textContent = tourTitle;
                            document.getElementById('alert-tour-date').textContent = selectedDate;
                            document.getElementById('alert-tour-people').textContent = adults + ' Người lớn, ' + children + ' Trẻ em';
                            document.getElementById('alert-tour-price').textContent = formatVND(totalVal);

                            document.getElementById('preview-alert-modal').style.display = 'flex';
                        }

                        function closeAlertModal() {
                            document.getElementById('preview-alert-modal').style.display = 'none';
                        }

                        calculateTotal();
                    </script>
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

// Initialize chart
async function initializeChart() {
    const ctx = document.getElementById('articleChart');
    if (ctx) {
        try {
            const response = await fetch('/admin/api/chart-data');
            const result = await response.json();

            if (result.success && result.data) {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: result.data.labels,
                        datasets: result.data.datasets.map((dataset, index) => ({
                            label: dataset.label,
                            data: dataset.data,
                            borderColor: index === 0 ? '#c00' : '#27ae60',
                            backgroundColor: index === 0 ? 'rgba(192, 0, 0, 0.1)' : 'rgba(39, 174, 96, 0.1)',
                            tension: 0.4
                        }))
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Lỗi tải dữ liệu biểu đồ:', error);
            // Fallback to default chart
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
                    datasets: [{
                        label: 'Bài viết mới',
                        data: [0, 0, 0, 0, 0, 0, 0],
                        borderColor: '#c00',
                        backgroundColor: 'rgba(192, 0, 0, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
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

// ============================================
// RSS FEEDS AND API NEWS HANDLERS
// ============================================

// RSS Preset Links
$(document).on('click', '.rss-preset', function (e) {
    e.preventDefault();
    const url = $(this).data('url');
    $('#rssFeedUrl').val(url);
});

// Fetch RSS Button
$('#fetchRssBtn').click(function () {
    const rssUrl = $('#rssFeedUrl').val().trim();
    const limit = $('#rssLimit').val() || 20;

    if (!rssUrl) {
        alert('Vui lòng nhập URL RSS feed');
        return;
    }

    const btn = $(this);
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Đang tải...');

    $.ajax({
        url: '/admin/api/fetch-api-news',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            source_type: 'rss',
            rss_url: rssUrl,
            limit: parseInt(limit)
        }),
        success: function (response) {
            if (response.success) {
                displayRssArticles(response.data);
                showToast('Thành công', `Đã tải ${response.count} bài viết từ RSS feed`, 'success');
                window.rssArticlesData = response.data;
            } else {
                showToast('Lỗi', response.message || 'Không thể tải bài viết', 'warning');
            }
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON?.message || 'Lỗi kết nối server';
            showToast('Lỗi', errorMsg, 'warning');
        },
        complete: function () {
            btn.prop('disabled', false).html('<i class="fas fa-download"></i> Tải bài');
        }
    });
});

// Display RSS Articles
function displayRssArticles(articles) {
    const container = $('#rssArticlesList');

    if (!articles || articles.length === 0) {
        container.html('<p class="text-muted text-center">Không có bài viết nào</p>');
        return;
    }

    let html = '<div class="row">';
    articles.forEach((article, index) => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">${article.title}</h6>
                        <p class="card-text text-muted small">${article.summary || 'Không có mô tả'}</p>
                        ${article.thumbnail ? `<img src="${article.thumbnail}" class="img-fluid rounded mb-2" style="max-height: 150px; object-fit: cover; width: 100%;">` : ''}
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">${article.published_at || 'N/A'}</small>
                            <button class="btn btn-sm btn-primary save-rss-article" data-index="${index}" data-article-id="${article.tour_id}">
                                <i class="fas fa-save"></i> Lưu
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.html(html);
}

// Save RSS Article Handler
$(document).on('click', '.save-rss-article', function () {
    const index = $(this).data('index');
    const article = window.rssArticlesData[index];

    openSaveExternalArticleModal(article);
});

// Open modal for saving external articles (RSS/API)
async function openSaveExternalArticleModal(articleData) {
    // Load categories - check region để load đúng loại danh mục
    const region = window.currentApiRegion || 'domestic';
    const isInternational = region === 'international';

    try {
        // Load categories từ API tương ứng với region
        const categoryEndpoint = isInternational
            ? '/admin/api/international-categories'
            : '/admin/api/categories';

        const response = await fetch(categoryEndpoint);
        const result = await response.json();

        let categoryOptions = '<option value="">-- Chọn danh mục --</option>';
        if (result.success) {
            // Xử lý cả trường hợp result.data và result.categories
            const categories = result.data || result.categories || [];

            if (categories.length === 0) {
                console.error('Không có danh mục nào');
                showToast('Cảnh báo', 'Không có danh mục nào trong hệ thống', 'warning');
            }

            categories.forEach(cat => {
                categoryOptions += `<option value="${cat.id}">${cat.name}</option>`;
            });
        } else {
            console.error('API trả về lỗi:', result);
            showToast('Lỗi', result.error || 'Không thể tải danh mục', 'warning');
            return;
        }

        $('#saveAPICategory').html(categoryOptions);

        // Lưu region info vào data attribute để biết save vào bảng nào
        $('#saveAPIArticleData').data('region', region);

    } catch (error) {
        console.error('Lỗi tải danh mục:', error);
        showToast('Lỗi', 'Không thể tải danh mục: ' + error.message, 'warning');
        return;
    }

    // Set article data
    $('#saveAPIArticleData').val(JSON.stringify(articleData));
    $('#saveAPITitle').val(articleData.title);
    $('#saveAPISummary').val(articleData.summary || articleData.description || '');
    $('#saveAPIStatus').val('pending'); // Default to pending
    $('#saveAPIIsHot').prop('checked', false);
    $('#saveAPIIsFeatured').prop('checked', false);

    // Update modal title để rõ đang lưu loại báo nào
    const modalTitle = isInternational ? 'Lưu bài viết Quốc tế từ API' : 'Lưu bài viết từ API';
    $('#saveAPIArticleModal .modal-title').text(modalTitle);

    const modal = new bootstrap.Modal(document.getElementById('saveAPIArticleModal'));
    modal.show();
}

// Load API Categories based on region
function loadApiCategories(region) {
    // Sử dụng proxy endpoint để tránh CORS (token sẽ được lấy từ settings tự động)
    const proxyUrl = region === 'international'
        ? `/admin/api/external-categories?source=en`
        : `/admin/api/external-categories`;

    const selectBox = $('#apiCategorySelect');
    selectBox.html('<option value="">Đang tải...</option>');

    $.ajax({
        url: proxyUrl,
        method: 'GET',
        success: function (response) {
            selectBox.html('');

            // Xử lý response - có thể là array hoặc object với data/categories
            let categories = [];
            if (Array.isArray(response)) {
                categories = response;
            } else if (response.data) {
                categories = Array.isArray(response.data) ? response.data : response.data.categories || [];
            } else if (response.categories) {
                categories = response.categories;
            }

            categories.forEach(function (cat) {
                const code = cat.code;
                const name = cat.name;
                selectBox.append(`<option value="${code}">${name}</option>`);
            });
        },
        error: function (xhr) {
            selectBox.html('<option value="">Lỗi tải danh mục</option>');
            console.error('Không thể tải danh mục:', xhr);
        }
    });
}

// Display API Articles
function displayApiArticles(articles) {
    const container = $('#apiArticlesList');

    if (!articles || articles.length === 0) {
        container.html('<p class="text-muted text-center">Không có bài viết nào</p>');
        return;
    }

    let html = '<div class="row">';
    articles.forEach((article, index) => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    ${article.thumbnail ? `<img src="${article.thumbnail}" class="card-img-top" style="height: 200px; object-fit: cover;">` : ''}
                    <div class="card-body">
                        <h6 class="card-title">${article.title}</h6>
                        <p class="card-text text-muted small">${article.summary || 'Không có mô tả'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-globe"></i> ${article.source || 'N/A'}<br>
                                <i class="fas fa-calendar"></i> ${updateDateTime(article.published_at) || 'N/A'}
                            </small>
                            <button class="btn btn-sm btn-primary save-api-article" data-index="${index}" data-article-id="${article.tour_id}">
                                <i class="fas fa-save"></i> Lưu
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.html(html);
}

// Save API Article Handler
$(document).on('click', '.save-api-article', function () {
    const index = $(this).data('index');
    const article = window.apiArticlesData[index];

    openSaveExternalArticleModal(article);
});

// =========================
// Bookings Manager
// =========================

async function loadBookings(status = 'all', search = '', page = 1) {
    try {
        const response = await fetch(`/admin/api/bookings?status=${status}&search=${encodeURIComponent(search)}&page=${page}`);
        const result = await response.json();

        if (result.success && result.data) {
            let html = '';
            result.data.forEach((booking) => {
                let badgeClass = 'bg-secondary';
                let statusLabel = booking.status;
                if (booking.status === 'pending') {
                    badgeClass = 'bg-warning text-dark';
                    statusLabel = 'Chờ duyệt';
                } else if (booking.status === 'confirmed') {
                    badgeClass = 'bg-primary';
                    statusLabel = 'Đã duyệt';
                } else if (booking.status === 'completed') {
                    badgeClass = 'bg-success';
                    statusLabel = 'Hoàn thành';
                } else if (booking.status === 'cancelled') {
                    badgeClass = 'bg-danger';
                    statusLabel = 'Đã hủy';
                }

                let actionButtons = `
                    <button class="btn btn-sm btn-info btn-view-booking" data-booking='${JSON.stringify(booking).replace(/'/g, "&#39;")}' title="Xem chi tiết">
                        <i class="fas fa-eye"></i>
                    </button>
                `;

                if (booking.status === 'pending') {
                    actionButtons += `
                        <button class="btn btn-sm btn-success btn-update-booking-status ms-1" data-id="${booking.id}" data-status="confirmed" title="Duyệt">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-danger btn-update-booking-status ms-1" data-id="${booking.id}" data-status="cancelled" title="Hủy">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                } else if (booking.status === 'confirmed') {
                    actionButtons += `
                        <button class="btn btn-sm btn-success btn-update-booking-status ms-1" data-id="${booking.id}" data-status="completed" title="Hoàn thành">
                            <i class="fas fa-check-double"></i>
                        </button>
                        <button class="btn btn-sm btn-danger btn-update-booking-status ms-1" data-id="${booking.id}" data-status="cancelled" title="Hủy">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                }

                const totalPriceFormatted = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(booking.totalPrice);

                html += `
                    <tr>
                        <td>#${booking.id}</td>
                        <td>
                            <strong>${escapeHtml(booking.userName)}</strong><br>
                            <small class="text-muted"><i class="fas fa-envelope"></i> ${escapeHtml(booking.userEmail)}</small><br>
                            <small class="text-muted"><i class="fas fa-phone"></i> ${escapeHtml(booking.userPhone)}</small>
                        </td>
                        <td>
                            <strong>${escapeHtml(booking.tourTitle)}</strong><br>
                            <small class="text-muted"><i class="far fa-calendar-alt"></i> Khởi hành: ${booking.departureDate}</small>
                        </td>
                        <td><strong class="text-primary">${totalPriceFormatted}</strong></td>
                        <td><span class="badge ${badgeClass}">${statusLabel}</span></td>
                        <td>${booking.createdAt}</td>
                        <td>${actionButtons}</td>
                    </tr>
                `;
            });

            if (result.data.length === 0) {
                html = '<tr><td colspan="7" class="text-center text-muted">Không có booking nào</td></tr>';
            }

            $('#bookingsTableBody').html(html);
            renderBookingsPagination(result.pagination);
        }
    } catch (error) {
        console.error('Lỗi tải danh sách bookings:', error);
        $('#bookingsTableBody').html('<tr><td colspan="7" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>');
    }
}

function renderBookingsPagination(pagination) {
    if (!pagination || pagination.pages <= 1) {
        $('#bookingsPagination').html('');
        return;
    }

    let html = '';
    const currentPage = pagination.page;
    const totalPages = pagination.pages;

    // Previous button
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
    `;

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }

    // Next button
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    `;

    $('#bookingsPagination').html(html);
}

async function updateBookingStatus(bookingId, newStatus) {
    try {
        const response = await fetch(`/admin/api/bookings/${bookingId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });
        const result = await response.json();
        if (result.success) {
            alert(result.message || 'Cập nhật trạng thái thành công');
            // Reload list
            const status = $('#bookingsStatusFilter').val() || 'all';
            const search = $('#bookingsSearchInput').val() || '';
            const page = parseInt($('#bookingsPagination .active .page-link').data('page')) || 1;
            loadBookings(status, search, page);
            loadStatistics(); // Reload dashboard stats
        } else {
            alert(result.error || 'Có lỗi xảy ra');
        }
    } catch (error) {
        console.error('Lỗi cập nhật trạng thái:', error);
        alert('Không thể kết nối đến máy chủ.');
    }
}

// Event handlers for Bookings Section
$(document).on('click', '#bookingsPagination .page-link', function (e) {
    e.preventDefault();
    const page = parseInt($(this).data('page'));
    if (page && page > 0) {
        const status = $('#bookingsStatusFilter').val() || 'all';
        const search = $('#bookingsSearchInput').val() || '';
        loadBookings(status, search, page);
    }
});

$(document).on('change', '#bookingsStatusFilter', function () {
    const status = $(this).val();
    const search = $('#bookingsSearchInput').val() || '';
    loadBookings(status, search, 1);
});

$(document).on('submit', '#bookingsSearchForm', function (e) {
    e.preventDefault();
    const status = $('#bookingsStatusFilter').val() || 'all';
    const search = $('#bookingsSearchInput').val().trim();
    loadBookings(status, search, 1);
});

$(document).on('click', '.btn-update-booking-status', function () {
    const bookingId = $(this).data('id');
    const newStatus = $(this).data('status');

    let confirmMsg = 'Bạn có chắc chắn muốn thay đổi trạng thái booking này?';
    if (newStatus === 'confirmed') {
        confirmMsg = 'Bạn có chắc chắn muốn duyệt đơn đặt tour này?';
    } else if (newStatus === 'completed') {
        confirmMsg = 'Bạn có chắc chắn muốn đánh dấu hoàn thành tour này?';
    } else if (newStatus === 'cancelled') {
        confirmMsg = 'Bạn có chắc chắn muốn hủy đơn đặt tour này?';
    }

    if (confirm(confirmMsg)) {
        updateBookingStatus(bookingId, newStatus);
    }
});

$(document).on('click', '.btn-view-booking', function () {
    const booking = $(this).data('booking');

    $('#modalBookingId').text(booking.id);
    $('#modalBookingCustomer').text(booking.userName);
    $('#modalBookingEmail').text(booking.userEmail);
    $('#modalBookingPhone').text(booking.userPhone || 'N/A');
    $('#modalBookingTour').text(booking.tourTitle);
    $('#modalBookingDeparture').text(booking.departureDate);
    $('#modalBookingPrice').text(new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(booking.totalPrice));

    let badgeClass = 'bg-secondary';
    let statusLabel = booking.status;
    if (booking.status === 'pending') {
        badgeClass = 'bg-warning text-dark';
        statusLabel = 'Chờ duyệt';
    } else if (booking.status === 'confirmed') {
        badgeClass = 'bg-primary';
        statusLabel = 'Đã duyệt';
    } else if (booking.status === 'completed') {
        badgeClass = 'bg-success';
        statusLabel = 'Hoàn thành';
    } else if (booking.status === 'cancelled') {
        badgeClass = 'bg-danger';
        statusLabel = 'Đã hủy';
    }

    $('#modalBookingStatus').html(`<span class="badge ${badgeClass}">${statusLabel}</span>`);
    $('#modalBookingCreated').text(booking.createdAt);

    const modal = new bootstrap.Modal(document.getElementById('viewBookingModal'));
    modal.show();
});

let bookingChartInstance = null;

async function initializeBookingChart() {
    const ctx = document.getElementById('bookingChart');
    if (!ctx) return;

    try {
        const response = await fetch('/admin/api/bookings/statistics');
        const result = await response.json();

        if (result.success && result.data && result.data.chart_data) {
            const chartData = result.data.chart_data;

            if (bookingChartInstance) {
                bookingChartInstance.destroy();
            }

            bookingChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.labels,
                    datasets: [
                        {
                            label: 'Doanh thu (VND)',
                            data: chartData.revenue,
                            borderColor: '#2ecc71',
                            backgroundColor: 'rgba(46, 204, 113, 0.1)',
                            yAxisID: 'yRevenue',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Số lượt đặt',
                            data: chartData.bookings,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            yAxisID: 'yBookings',
                            type: 'bar',
                            barThickness: 15
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        yRevenue: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Doanh thu (đ)'
                            },
                            beginAtZero: true
                        },
                        yBookings: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Lượt đặt'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Lỗi khởi tạo biểu đồ bookings:', error);
    }
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