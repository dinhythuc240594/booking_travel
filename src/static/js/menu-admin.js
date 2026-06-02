// Menu Manager Configuration - Tự động phát hiện tab hiện tại
const menuConfig = {
    // Cấu hình cho menu thường
    'menu-manager': {
        apiBase: '/admin/api/menu-items',
        selectors: {
            addBtn: '#addMenuBtn',
            saveBtn: '#saveMenuBtn',
            resetBtn: '#resetMenuBtn',
            previewBtn: '#previewMenuBtn',
            treeList: '#menuTreeList',
            treeView: '#menuTreeView',
            modal: '#menuModal',
            modalTitle: '#menuModalTitle',
            form: '#menuForm',
            formId: '#menuId',
            formName: '#menuName',
            formSlug: '#menuSlug',
            formParent: '#menuParent',
            formIcon: '#menuIcon',
            formOrder: '#menuOrder',
            formVisible: '#menuVisible',
            previewModal: '#previewModal',
            previewList: '#previewMenuList'
        }
    },
    // Cấu hình cho menu quốc tế
    'en-menu-manager': {
        apiBase: '/admin/api/international-menu-items',
        selectors: {
            addBtn: '#addEnMenuBtn',
            saveBtn: '#saveEnMenuBtn',
            resetBtn: '#resetEnMenuBtn',
            previewBtn: '#previewEnMenuBtn',
            treeList: '#enMenuTreeList',
            treeView: '#enMenuTreeView',
            modal: '#enMenuModal',
            modalTitle: '#enMenuModalTitle',
            form: '#enMenuForm',
            formId: '#enMenuId',
            formName: '#enMenuName',
            formSlug: '#enMenuSlug',
            formParent: '#enMenuParent',
            formIcon: '#enMenuIcon',
            formOrder: '#enMenuOrder',
            formVisible: '#enMenuVisible',
            previewModal: '#enPreviewModal',
            previewList: '#enPreviewMenuList'
        }
    }
};

// Lấy config dựa trên section hiện tại
function getMenuConfig() {
    const activeSection = $('.content-section.active').attr('id');
    return menuConfig[activeSection] || menuConfig['menu-manager'];
}

// Helper để lấy selector từ config
function getSelector(key) {
    const config = getMenuConfig();
    return config.selectors[key];
}

// Helper để lấy API base URL
function getApiBase() {
    const config = getMenuConfig();
    return config.apiBase;
}

$(document).ready(function() {
    // Chỉ khởi tạo khi ở trong section menu manager
    function initMenuManager() {
        const activeSection = $('.content-section.active').attr('id');
        if (activeSection !== 'menu-manager' && activeSection !== 'en-menu-manager') {
            return;
        }
        
        const config = getMenuConfig();
        
        // Check and init default menu items if empty
        checkAndInitDefaultMenus();
        
        // Load menu data
        loadMenuTable();
        loadMenuTree();
        loadParentMenuOptions();
        
        // Initialize drag & drop
        initDragAndDrop();
        
        // Add Menu button
        $(config.selectors.addBtn).off('click').on('click', function() {
            openMenuModal('add', null);
        });
        
        // Save menu
        $(config.selectors.saveBtn).off('click').on('click', function() {
            saveMenu();
        });
        
        // Auto generate slug
        $(config.selectors.formName).off('input').on('input', function() {
            const name = $(this).val();
            const slug = slugify(name);
            $(config.selectors.formSlug).val(slug);
        });
        
        // Preview menu
        $(config.selectors.previewBtn).off('click').on('click', function() {
            previewMenu();
        });
        
        // Reset menu
        $(config.selectors.resetBtn).off('click').on('click', function() {
            if (confirm('Bạn có chắc muốn reset tất cả menu về mặc định? Thao tác này sẽ xóa tất cả menu hiện tại và tạo lại menu mặc định!')) {
                resetMenuToDefault();
            }
        });
    }
    
    // Khởi tạo ngay nếu section đã active
    initMenuManager();
    
    // Khởi tạo lại khi chuyển section
    $(document).on('click', '.sidebar-menu a[data-section]', function() {
        setTimeout(initMenuManager, 100);
    });
    
    // Edit menu (delegate event)
    $(document).on('click', '.btn-edit-menu', function() {
        const menuId = parseInt($(this).data('id'));
        openMenuModal('edit', menuId);
    });
    
    // Delete menu (delegate event)
    $(document).on('click', '.btn-delete-menu', function() {
        const menuId = parseInt($(this).data('id'));
        deleteMenu(menuId);
    });
    
    // Toggle visibility (delegate event)
    $(document).on('change', '.menu-visibility-toggle', function() {
        const menuId = parseInt($(this).data('id'));
        const visible = $(this).is(':checked');
        updateMenuVisibility(menuId, visible);
    });
    
    // Toggle expand/collapse children (delegate event)
    $(document).on('click', '.menu-item-expand.has-children', function(e) {
        e.stopPropagation();
        const menuId = $(this).data('menu-id');
        const $container = $(`.menu-children-container[data-parent-id="${menuId}"]`);
        const $icon = $(this).find('i');
        
        if ($container.hasClass('expanded')) {
            $container.removeClass('expanded');
            $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        } else {
            $container.addClass('expanded');
            $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        }
    });
    
    // Move menu up (delegate event)
    $(document).on('click', '.btn-move-up', function(e) {
        e.stopPropagation();
        const menuId = parseInt($(this).data('id'));
        const isParent = $(this).data('is-parent') === true;
        moveMenuUp(menuId, isParent);
    });
    
    // Move menu down (delegate event)
    $(document).on('click', '.btn-move-down', function(e) {
        e.stopPropagation();
        const menuId = parseInt($(this).data('id'));
        const isParent = $(this).data('is-parent') === true;
        moveMenuDown(menuId, isParent);
    });
    
    // Add Submenu from menu item (delegate event)
    $(document).on('click', '.btn-add-submenu', function(e) {
        e.stopPropagation();
        const parentId = parseInt($(this).data('id'));
        const level = parseInt($(this).data('level')) || 1;
        
        // Kiểm tra level
        if (level >= 4) {
            showToast('Cảnh báo', 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.', 'warning');
            return;
        }
        
        openMenuModal('add-submenu', null, parentId);
    });
});

// Check and init default menu items
async function checkAndInitDefaultMenus() {
    try {
        const apiBase = getApiBase();
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data && result.data.length === 0) {
            // Bảng rỗng, tự động init default menu items
            const initResponse = await fetch(`${apiBase}/init-default`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const initResult = await initResponse.json();
            if (initResult.success) {
                console.log('Đã tự động khởi tạo menu items mặc định');
            }
        }
    } catch (error) {
        console.error('Lỗi kiểm tra menu items:', error);
    }
}

// Render menu item recursively with all levels
function renderMenuWithChildren(menu, allMenus, level = 1) {
    const children = allMenus.filter(m => m.parent_id === menu.id)
                              .sort((a, b) => a.order - b.order);
    const hasChildren = children.length > 0;
    const isParent = level === 1;
    
    let html = renderMenuRow(menu, hasChildren, isParent, level);
    
    if (hasChildren) {
        // Mặc định expand khi có children
        html += `<div class="menu-children-container expanded" data-parent-id="${menu.id}">`;
        children.forEach(child => {
            html += renderMenuWithChildren(child, allMenus, level + 1);
        });
        html += `</div>`;
    }
    
    return html;
}

// Load menu table with tree view
async function loadMenuTable() {
    try {
        const apiBase = getApiBase();
        const treeListSelector = getSelector('treeList');
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            const menus = result.data;
            
            // Build tree structure - chỉ lấy parent items (level 1)
            const parentMenus = menus.filter(m => m.parent_id === null)
                                     .sort((a, b) => a.order - b.order);
            
            let html = '';
            
            // Render đệ quy tất cả các cấp
            parentMenus.forEach(parent => {
                html += renderMenuWithChildren(parent, menus, 1);
            });
            
            if (menus.length === 0) {
                html = '<div class="text-center text-muted p-4">Chưa có menu nào. Nhấn "Thêm Menu" để tạo mới.</div>';
            }
            
            $(treeListSelector).html(html);
            
            // Initialize sortable after rendering
            initDragAndDrop();
        }
    } catch (error) {
        console.error('Lỗi tải menu:', error);
        $(getSelector('treeList')).html('<div class="text-center text-danger p-4">Lỗi tải dữ liệu</div>');
    }
}

// Render menu row
function renderMenuRow(menu, hasChildren, isParent, level = null) {
    const icon = menu.icon ? `<i class="${menu.icon}"></i> ` : '';
    const checked = menu.visible ? 'checked' : '';
    const menuLevel = level || menu.level || 1;
    const rowClass = isParent ? 'parent-item' : `child-item level-${menuLevel}`;
    const hiddenClass = !menu.visible ? 'hidden-item' : '';
    const canAddSubmenu = menuLevel < 4; // Cho phép thêm submenu nếu level < 4
    // Nếu có children và container expanded, hiển thị chevron-up, ngược lại chevron-down
    const expandIcon = hasChildren ? '<i class="fas fa-chevron-up"></i>' : '<i class="fas fa-minus" style="opacity: 0.3;"></i>';
    
    return `
        <div class="menu-item-row ${rowClass} ${hiddenClass}" data-id="${menu.id}" data-parent-id="${menu.parent_id || ''}" data-level="${menuLevel}">
            <div class="menu-item-handle">
                <i class="fas fa-grip-vertical"></i>
            </div>
            <div class="menu-item-expand ${hasChildren ? 'has-children' : ''}" data-menu-id="${menu.id}">
                ${expandIcon}
            </div>
            <div class="menu-item-content">
                <div class="menu-item-info">
                    <div class="menu-item-name">
                        ${icon}${menu.name}
                        ${!menu.visible ? '<span class="badge bg-secondary ms-2">Ẩn</span>' : ''}
                        <!-- <span class="badge bg-info ms-2">Cấp ${level}</span> -->
                    </div>
                    <div class="menu-item-meta">
                        <code>${menu.slug}</code> | Thứ tự: ${menu.order}
                    </div>
                </div>
                <div class="menu-item-actions">
                    ${canAddSubmenu ? `
                    <button class="btn btn-sm btn-success btn-action btn-add-submenu me-2" data-id="${menu.id}" data-level="${level}" title="Thêm Submenu" style="display: none">
                        <i class="fas fa-plus-circle"></i>
                    </button>
                    ` : ''}
                    <label class="visibility-switch me-2">
                        <input type="checkbox" class="menu-visibility-toggle" data-id="${menu.id}" ${checked}>
                        <span class="visibility-slider"></span>
                    </label>
                    <button class="btn btn-sm btn-info btn-action btn-edit-menu" data-id="${menu.id}" title="Sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger btn-action btn-delete-menu" data-id="${menu.id}" title="Xóa">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                                    <div class="btn-group me-2" role="group">
                        <button class="btn btn-sm btn-secondary btn-move-up" data-id="${menu.id}" data-is-parent="${isParent}" title="Lên">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                        <button class="btn btn-sm btn-secondary btn-move-down" data-id="${menu.id}" data-is-parent="${isParent}" title="Xuống">
                            <i class="fas fa-arrow-down"></i>
                        </button>
                    </div>
            </div>
        </div>
    `;
}

// Initialize drag and drop
function initDragAndDrop() {
    if (typeof $.ui !== 'undefined' && $.ui.sortable) {
        const treeListSelector = getSelector('treeList');
        // Destroy existing sortable instances to avoid conflicts
        if ($(treeListSelector).hasClass('ui-sortable')) {
            $(treeListSelector).sortable('destroy');
        }
        $('.menu-children-container').each(function() {
            if ($(this).hasClass('ui-sortable')) {
                $(this).sortable('destroy');
            }
        });
        
        // Make parent items sortable
        $(treeListSelector).sortable({
            handle: '.menu-item-handle',
            items: '.menu-item-row.parent-item',
            tolerance: 'pointer',
            cursor: 'move',
            placeholder: 'menu-item-placeholder',
            opacity: 0.8,
            axis: 'y',
            helper: function(e, item) {
                // Clone item with children container
                const $clone = item.clone();
                const $children = item.next('.menu-children-container');
                if ($children.length) {
                    const $childrenClone = $children.clone();
                    $clone.append($childrenClone);
                }
                $clone.css('width', item.width());
                return $clone;
            },
            start: function(e, ui) {
                ui.placeholder.height(ui.item.height());
                // Hide children container while dragging parent
                const $children = ui.item.next('.menu-children-container');
                if ($children.length) {
                    $children.hide();
                }
            },
            stop: function(e, ui) {
                // Show children container after drop
                const $children = ui.item.next('.menu-children-container');
                if ($children.length) {
                    $children.show();
                }
                // Reinitialize child sortables after parent move
                initChildSortables();
            },
            update: function(event, ui) {
                saveMenuOrder();
            }
        });
        
        // Initialize child items sortable
        initChildSortables();
    }
}

// Initialize child items sortable
function initChildSortables() {
    $('.menu-children-container').each(function() {
        const $container = $(this);
        
        // Destroy existing sortable if exists
        if ($container.hasClass('ui-sortable')) {
            $container.sortable('destroy');
        }
        
        // Make child items sortable within their container
        $container.sortable({
            handle: '.menu-item-handle',
            items: '.menu-item-row.child-item',
            tolerance: 'pointer',
            cursor: 'move',
            placeholder: 'menu-item-placeholder',
            opacity: 0.8,
            axis: 'y',
            connectWith: '.menu-children-container',
            receive: function(event, ui) {
                // Update parent_id when child is moved to different parent
                const newParentId = parseInt($container.data('parent-id'));
                const childId = parseInt(ui.item.data('id'));
                
                // Update data attribute
                ui.item.attr('data-parent-id', newParentId);
                
                // Update visual class if needed
                ui.item.removeClass('parent-item').addClass('child-item');
                
                // Ensure the container is expanded
                if (!$container.hasClass('expanded')) {
                    $container.addClass('expanded');
                    // Update expand icon
                    const $parentRow = $(`.menu-item-row.parent-item[data-id="${newParentId}"]`);
                    const $expandIcon = $parentRow.find('.menu-item-expand i');
                    if ($expandIcon.length) {
                        $expandIcon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
                    }
                }
            },
            start: function(e, ui) {
                ui.placeholder.height(ui.item.height());
            },
            update: function(event, ui) {
                // Check if item was moved to different parent
                const $item = ui.item;
                const currentParentId = parseInt($container.data('parent-id'));
                const itemParentId = parseInt($item.data('parent-id')) || null;
                
                if (itemParentId !== currentParentId) {
                    // Item moved to different parent, update parent_id
                    $item.attr('data-parent-id', currentParentId);
                }
                
                saveMenuOrder();
            }
        });
    });
}

// Save menu order after drag & drop - recursive function to collect all levels
function collectMenuItems($container, parentId, items) {
    let order = 0;
    
    $container.children('.menu-item-row').each(function() {
        const $row = $(this);
        order++;
        const menuId = parseInt($row.data('id'));
        const rowParentId = parseInt($row.data('parent-id')) || null;
        
        // Use the provided parentId (from container) or the row's parent_id
        const finalParentId = parentId !== undefined ? parentId : rowParentId;
        
        items.push({
            id: menuId,
            parent_id: finalParentId,
            order: order
        });
        
        // Recursively collect children
        const $childrenContainer = $row.next('.menu-children-container[data-parent-id="' + menuId + '"]');
        if ($childrenContainer.length) {
            collectMenuItems($childrenContainer, menuId, items);
        }
    });
}

// Save menu order after drag & drop
async function saveMenuOrder() {
    const items = [];
    
    // Collect all menu items recursively starting from root
    const $rootContainer = $(getSelector('treeList'));
    collectMenuItems($rootContainer, null, items);
    
    try {
        const apiBase = getApiBase();
        const response = await fetch(`${apiBase}/update-order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items: items })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Thành công', 'Đã cập nhật thứ tự menu', 'success');
            // Reload để đảm bảo sync
            setTimeout(() => {
                loadMenuTable();
                loadMenuTree();
            }, 500);
        } else {
            showToast('Lỗi', result.error || 'Không thể cập nhật thứ tự', 'warning');
            // Reload để revert
            loadMenuTable();
        }
    } catch (error) {
        console.error('Lỗi cập nhật thứ tự:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi cập nhật thứ tự', 'warning');
        // Reload để revert
        loadMenuTable();
    }
}

// Move menu item up
function moveMenuUp(menuId, isParent) {
    const $currentItem = $(`.menu-item-row[data-id="${menuId}"]`);
    
    if (!$currentItem.length) {
        showToast('Lỗi', 'Không tìm thấy menu item', 'warning');
        return;
    }
    
    if (isParent) {
        // Move parent item up
        // Find previous parent, skipping any children containers
        let $prevParent = null;
        let $prev = $currentItem.prev();
        
        while ($prev.length) {
            if ($prev.hasClass('menu-item-row') && $prev.hasClass('parent-item')) {
                $prevParent = $prev;
                break;
            }
            $prev = $prev.prev();
        }
        
        if ($prevParent && $prevParent.length) {
            // Get children container of current item
            const $currentChildren = $currentItem.next('.menu-children-container');
            
            // Get children container of previous parent (if exists)
            const $prevChildren = $prevParent.next('.menu-children-container');
            
            // Move current item before previous parent
            $currentItem.insertBefore($prevParent);
            
            // Move children container back after current item
            if ($currentChildren.length) {
                $currentChildren.insertAfter($currentItem);
            }
            
            // Reinitialize drag & drop
            initDragAndDrop();
            
            // Save order
            saveMenuOrder();
        } else {
            showToast('Thông báo', 'Menu đã ở vị trí đầu tiên', 'info');
        }
    } else {
        // Move child item up
        const $parentRow = $currentItem.closest('.menu-children-container').prev('.menu-item-row.parent-item');
        const $childrenContainer = $currentItem.parent('.menu-children-container');
        
        if (!$childrenContainer.length) {
            showToast('Lỗi', 'Không tìm thấy container', 'warning');
            return;
        }
        
        const $prevChild = $currentItem.prev('.menu-item-row.child-item');
        
        if ($prevChild.length) {
            // Swap positions
            $currentItem.insertBefore($prevChild);
            
            // Reinitialize drag & drop
            initDragAndDrop();
            
            // Save order
            saveMenuOrder();
        } else {
            showToast('Thông báo', 'Menu đã ở vị trí đầu tiên trong nhóm', 'info');
        }
    }
}

// Move menu item down
function moveMenuDown(menuId, isParent) {
    const $currentItem = $(`.menu-item-row[data-id="${menuId}"]`);
    
    if (!$currentItem.length) {
        showToast('Lỗi', 'Không tìm thấy menu item', 'warning');
        return;
    }
    
    if (isParent) {
        // Move parent item down
        // Need to find next parent, skipping any children containers
        let $nextParent = null;
        let $next = $currentItem.next();
        
        while ($next.length) {
            if ($next.hasClass('menu-item-row') && $next.hasClass('parent-item')) {
                $nextParent = $next;
                break;
            }
            $next = $next.next();
        }
        
        if ($nextParent && $nextParent.length) {
            // Get children container of current item
            const $currentChildren = $currentItem.next('.menu-children-container');
            
            // Get children container of next parent
            const $nextChildren = $nextParent.next('.menu-children-container');
            
            // Move current item after next parent
            if ($nextChildren.length) {
                $currentItem.insertAfter($nextChildren);
            } else {
                $currentItem.insertAfter($nextParent);
            }
            
            // Move children container back after current item
            if ($currentChildren.length) {
                $currentChildren.insertAfter($currentItem);
            }
            
            // Reinitialize drag & drop
            initDragAndDrop();
            
            // Save order
            saveMenuOrder();
        } else {
            showToast('Thông báo', 'Menu đã ở vị trí cuối cùng', 'info');
        }
    } else {
        // Move child item down
        const $childrenContainer = $currentItem.parent('.menu-children-container');
        
        if (!$childrenContainer.length) {
            showToast('Lỗi', 'Không tìm thấy container', 'warning');
            return;
        }
        
        const $nextChild = $currentItem.next('.menu-item-row.child-item');
        
        if ($nextChild.length) {
            // Swap positions
            $currentItem.insertAfter($nextChild);
            
            // Reinitialize drag & drop
            initDragAndDrop();
            
            // Save order
            saveMenuOrder();
        } else {
            showToast('Thông báo', 'Menu đã ở vị trí cuối cùng trong nhóm', 'info');
        }
    }
}

// Load menu tree
async function loadMenuTree() {
    try {
        const apiBase = getApiBase();
        const treeViewSelector = getSelector('treeView');
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            const menus = result.data;
            const parentMenus = menus.filter(m => m.parent_id === null && m.visible)
                                      .sort((a, b) => a.order - b.order);
            
            let html = '<ul class="menu-tree">';
            
            parentMenus.forEach(parent => {
                const children = menus.filter(m => m.parent_id === parent.id && m.visible)
                                      .sort((a, b) => a.order - b.order);
                
                html += `
                    <li>
                        <div class="menu-tree-item parent">
                            ${parent.icon ? `<i class="${parent.icon}"></i>` : ''} 
                            <strong>${parent.name}</strong> 
                            <span class="badge bg-secondary">${parent.order}</span>
                            ${parent.visible ? '<span class="badge bg-success">Hiện</span>' : '<span class="badge bg-danger">Ẩn</span>'}
                        </div>
                `;
                
                if (children.length > 0) {
                    html += '<ul class="menu-tree-children">';
                    children.forEach(child => {
                        html += `
                            <li>
                                ${child.name} 
                                <span class="badge bg-secondary">${child.order}</span>
                                ${child.visible ? '<span class="badge bg-success">Hiện</span>' : '<span class="badge bg-danger">Ẩn</span>'}
                            </li>
                        `;
                    });
                    html += '</ul>';
                }
                
                html += '</li>';
            });
            
            html += '</ul>';
            $(treeViewSelector).html(html);
        }
    } catch (error) {
        console.error('Lỗi tải menu tree:', error);
    }
}

// Load parent menu options
async function loadParentMenuOptions() {
    try {
        const apiBase = getApiBase();
        const formParentSelector = getSelector('formParent');
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            // Lấy tất cả menu có level < 4 (có thể làm parent)
            const availableParents = result.data.filter(m => (m.level || 1) < 4)
                                               .sort((a, b) => (a.order || 0) - (b.order || 0));
            
            let html = '<option value="">-- Menu cấp 1 --</option>';
            
            // Nhóm theo level để hiển thị rõ hơn
            const menusByLevel = {};
            availableParents.forEach(menu => {
                const level = menu.level || 1;
                if (!menusByLevel[level]) {
                    menusByLevel[level] = [];
                }
                menusByLevel[level].push(menu);
            });
            
            // Hiển thị theo thứ tự level
            Object.keys(menusByLevel).sort().forEach(level => {
                const levelMenus = menusByLevel[level];
                levelMenus.forEach(menu => {
                    const indent = '&nbsp;'.repeat((parseInt(level) - 1) * 4);
                    html += `<option value="${menu.id}">${indent}${menu.name} (Cấp ${level})</option>`;
                });
            });
            
            $(formParentSelector).html(html);
        }
    } catch (error) {
        console.error('Lỗi tải parent menu options:', error);
    }
}

// Open menu modal
async function openMenuModal(mode, menuId, parentId = null) {
    const config = getMenuConfig();
    const formSelector = getSelector('form');
    const formIdSelector = getSelector('formId');
    const modalTitleSelector = getSelector('modalTitle');
    const formParentSelector = getSelector('formParent');
    const formVisibleSelector = getSelector('formVisible');
    const formNameSelector = getSelector('formName');
    const formSlugSelector = getSelector('formSlug');
    const formIconSelector = getSelector('formIcon');
    const formOrderSelector = getSelector('formOrder');
    const modalSelector = getSelector('modal');
    
    $(formSelector)[0].reset();
    $(formIdSelector).val('');
    
    // Load parent menu options first
    await loadParentMenuOptions();
    
    if (mode === 'add') {
        $(modalTitleSelector).text('Thêm Menu Mới');
        $(formParentSelector).val('').prop('disabled', false);
        $(formVisibleSelector).prop('checked', true);
    } else if (mode === 'add-submenu') {
        $(modalTitleSelector).text('Thêm Submenu');
        $(formVisibleSelector).prop('checked', true);
        
        // Nếu có parentId, tự động set và disable select
        if (parentId) {
            $(formParentSelector).val(parentId).prop('disabled', true);
            
            // Lấy thông tin parent để hiển thị
            try {
                const apiBase = getApiBase();
                const response = await fetch(apiBase);
                const result = await response.json();
                
                if (result.success && result.data) {
                    const parentMenu = result.data.find(m => m.id === parentId);
                    if (parentMenu) {
                        const parentLevel = parentMenu.level || 1;
                        if (parentLevel >= 4) {
                            showToast('Cảnh báo', 'Không thể tạo menu quá 4 cấp. Menu cha đã đạt cấp tối đa.', 'warning');
                            return;
                        }
                        $(modalTitleSelector).text(`Thêm Submenu cho "${parentMenu.name}" (Cấp ${parentLevel + 1})`);
                    }
                }
            } catch (error) {
                console.error('Lỗi tải thông tin parent menu:', error);
            }
        } else {
            // Nếu không có parentId, cho phép chọn parent
            $(formParentSelector).val('').prop('disabled', false);
        }
    } else if (mode === 'edit' && menuId) {
        $(modalTitleSelector).text('Chỉnh sửa Menu');
        $(formParentSelector).prop('disabled', false);
        try {
            const apiBase = getApiBase();
            const response = await fetch(apiBase);
            const result = await response.json();
            
            if (result.success && result.data) {
                const menu = result.data.find(m => m.id === menuId);
                if (menu) {
                    $(formIdSelector).val(menu.id);
                    $(formNameSelector).val(menu.name);
                    $(formSlugSelector).val(menu.slug);
                    $(formParentSelector).val(menu.parent_id || '');
                    $(formIconSelector).val(menu.icon || '');
                    $(formOrderSelector).val(menu.order);
                    $(formVisibleSelector).prop('checked', menu.visible);
                }
            }
        } catch (error) {
            console.error('Lỗi tải menu:', error);
        }
    }
    
    const modalElement = document.querySelector(modalSelector);
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

// Save menu
async function saveMenu() {
    const apiBase = getApiBase();
    const formIdSelector = getSelector('formId');
    const formParentSelector = getSelector('formParent');
    const formNameSelector = getSelector('formName');
    const formSlugSelector = getSelector('formSlug');
    const formIconSelector = getSelector('formIcon');
    const formOrderSelector = getSelector('formOrder');
    const formVisibleSelector = getSelector('formVisible');
    const modalSelector = getSelector('modal');
    
    const menuId = $(formIdSelector).val();
    const parentId = $(formParentSelector).val() ? parseInt($(formParentSelector).val()) : null;
    
    // Kiểm tra level nếu có parent_id
    if (parentId) {
        try {
            const response = await fetch(apiBase);
            const result = await response.json();
            
            if (result.success && result.data) {
                const parentMenu = result.data.find(m => m.id === parentId);
                if (parentMenu) {
                    const parentLevel = parentMenu.level || 1;
                    if (parentLevel >= 4) {
                        showToast('Lỗi', 'Không thể tạo menu quá 4 cấp. Menu cha đã đạt cấp tối đa.', 'warning');
                        return;
                    }
                }
            }
        } catch (error) {
            console.error('Lỗi kiểm tra level:', error);
        }
    }
    
    const menuData = {
        name: $(formNameSelector).val().trim(),
        slug: $(formSlugSelector).val().trim(),
        parent_id: parentId,
        icon: $(formIconSelector).val().trim() || null,
        order: parseInt($(formOrderSelector).val()) || 1,
        visible: $(formVisibleSelector).is(':checked')
    };
    
    if (!menuData.name) {
        alert('Vui lòng nhập tên menu!');
        return;
    }
    
    if (!menuData.slug) {
        menuData.slug = slugify(menuData.name);
    }
    
    try {
        let response;
        if (menuId) {
            // Update existing menu
            response = await fetch(`${apiBase}/${menuId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(menuData)
            });
        } else {
            // Add new menu
            response = await fetch(apiBase, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(menuData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Thành công', result.message || (menuId ? 'Đã cập nhật menu' : 'Đã thêm menu mới'), 'success');
            const modalElement = document.querySelector(modalSelector);
            bootstrap.Modal.getInstance(modalElement).hide();
            loadMenuTable();
            loadMenuTree();
            loadParentMenuOptions();
        } else {
            showToast('Lỗi', result.error || 'Không thể lưu menu', 'warning');
        }
    } catch (error) {
        console.error('Lỗi lưu menu:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi lưu menu', 'warning');
    }
}

// Slugify function
function slugify(text) {
    const from = "àáäâãèéëêìíïîòóöôõùúüûñçăắằẳẵặâấầẩẫậđèéẹẻẽêếềểễệìíịỉĩòóọỏõôốồổỗộơớờởỡợùúụủũưứừửữựỳýỵỷỹ";
    const to = "aaaaaeeeeiiiioooooouuuuncaaaaaaaaaaaadeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyy";
    
    let slug = text.toLowerCase();
    
    for (let i = 0; i < from.length; i++) {
        slug = slug.replace(new RegExp(from[i], 'g'), to[i]);
    }
    
    slug = slug.replace(/[^a-z0-9 -]/g, '')
               .replace(/\s+/g, '-')
               .replace(/-+/g, '-')
               .replace(/^-+/, '')
               .replace(/-+$/, '');
    
    return slug;
}

// Delete menu
async function deleteMenu(menuId) {
    try {
        const apiBase = getApiBase();
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            const menu = result.data.find(m => m.id === menuId);
            if (!menu) {
                showToast('Lỗi', 'Không tìm thấy menu', 'warning');
                return;
            }
            
            const childCount = result.data.filter(m => m.parent_id === menuId).length;
            
            let confirmMsg = `Bạn có chắc muốn xóa menu "${menu.name}"?`;
            if (childCount > 0) {
                confirmMsg += `\n\nLưu ý: Menu này có ${childCount} submenu, tất cả sẽ bị xóa!`;
            }
            
            if (confirm(confirmMsg)) {
                const deleteResponse = await fetch(`${apiBase}/${menuId}`, {
                    method: 'DELETE'
                });
                
                const deleteResult = await deleteResponse.json();
                
                if (deleteResult.success) {
                    showToast('Thành công', 'Đã xóa menu', 'success');
                    loadMenuTable();
                    loadMenuTree();
                    loadParentMenuOptions();
                } else {
                    showToast('Lỗi', deleteResult.error || 'Không thể xóa menu', 'warning');
                }
            }
        }
    } catch (error) {
        console.error('Lỗi xóa menu:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi xóa menu', 'warning');
    }
}

// Preview menu
async function previewMenu() {
    try {
        const apiBase = getApiBase();
        const previewListSelector = getSelector('previewList');
        const previewModalSelector = getSelector('previewModal');
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            const menus = result.data;
            const parentMenus = menus.filter(m => m.parent_id === null && m.visible)
                                      .sort((a, b) => a.order - b.order);
            
            let html = '<div class="preview-header"><h4><i class="fas fa-eye"></i> Xem trước Menu</h4></div>';
            html += '<nav class="main-nav-preview">';
            html += '<ul class="nav-menu-preview">';
            
            parentMenus.forEach(menu => {
                const children = menus.filter(m => m.parent_id === menu.id && m.visible)
                                      .sort((a, b) => a.order - b.order);
                const hasChildren = children.length > 0;
                const icon = menu.icon ? `<i class="${menu.icon}"></i>` : '<i class="fas fa-circle" style="font-size: 6px;"></i>';
                
                html += `<li>`;
                html += `<a href="#${menu.slug}">${icon} <span>${menu.name}</span>${hasChildren ? ' <i class="fas fa-chevron-down" style="font-size: 10px; margin-left: 5px;"></i>' : ''}</a>`;
                
                if (hasChildren) {
                    html += '<ul class="submenu-preview">';
                    children.forEach(child => {
                        html += `<li><a href="#${child.slug}"><i class="fas fa-angle-right" style="font-size: 10px; margin-right: 5px;"></i>${child.name}</a></li>`;
                    });
                    html += '</ul>';
                }
                
                html += '</li>';
            });
            
            html += '</ul>';
            html += '</nav>';
            
            $(previewListSelector).html(html);
            
            const previewModalElement = document.querySelector(previewModalSelector);
            const modal = new bootstrap.Modal(previewModalElement);
            modal.show();
        }
    } catch (error) {
        console.error('Lỗi tải menu preview:', error);
    }
}

// Update menu visibility
async function updateMenuVisibility(menuId, visible) {
    try {
        const apiBase = getApiBase();
        const response = await fetch(`${apiBase}/${menuId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ visible: visible })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Thành công', 'Đã cập nhật trạng thái hiển thị', 'success');
            loadMenuTable();
            loadMenuTree();
        } else {
            showToast('Lỗi', result.error || 'Không thể cập nhật', 'warning');
        }
    } catch (error) {
        console.error('Lỗi cập nhật visibility:', error);
        showToast('Lỗi', 'Có lỗi xảy ra', 'warning');
    }
}

// Reset menu to default
async function resetMenuToDefault() {
    try {
        const apiBase = getApiBase();
        // Xóa tất cả menu items
        const response = await fetch(apiBase);
        const result = await response.json();
        
        if (result.success && result.data) {
            // Xóa từng menu item
            for (const menu of result.data) {
                await fetch(`${apiBase}/${menu.id}`, {
                    method: 'DELETE'
                });
            }
            
            // Init default menu items
            const initResponse = await fetch(`${apiBase}/init-default`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const initResult = await initResponse.json();
            
            if (initResult.success) {
                showToast('Thành công', 'Đã reset menu về mặc định', 'success');
                loadMenuTable();
                loadMenuTree();
                loadParentMenuOptions();
            } else {
                showToast('Lỗi', initResult.error || 'Không thể reset menu', 'warning');
            }
        }
    } catch (error) {
        console.error('Lỗi reset menu:', error);
        showToast('Lỗi', 'Có lỗi xảy ra khi reset menu', 'warning');
    }
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
    
    setTimeout(function() {
        toastEl.remove();
    }, 5000);
}
