"""
admin router - define routes for admin
"""

from flask import Blueprint, render_template, request, jsonify, abort, make_response

import base
import admin_controller

# Create Blueprint for admin with url_prefix is "/admin" to redirect route
# and template_folder for html files in folder admin
admin_bp = Blueprint('admin', __name__, 
                     url_prefix='/admin',
                     template_folder='templates/admin')

controller = admin_controller.AdminController

class BaseAdminView(base.BaseView, controller):
    def __init__(self):
        super().__init__()

# =========================================================
# 1. AUTH & DASHBOARD PAGES
# =========================================================

class Login(BaseAdminView):
    def get(self):
        return self.login()

    def post(self):
        return self.login()

class Logout(BaseAdminView):
    def get(self):
        return self.logout()

class Dashboard(BaseAdminView):
    def get(self):
        return self.dashboard()

class EditorDashboard(BaseAdminView):
    def get(self):
        return self.editor_dashboard()

class Profile(BaseAdminView):
    def get(self):
        return self.profile()


# =========================================================
# 2. TOUR MANAGEMENT PAGES
# =========================================================

class TourList(BaseAdminView):

    def get(self):
        return self.tour_list()

class TourCreate(BaseAdminView):
    
    def get(self):
        return self.tour_create()
    
    def post(self):
        return self.tour_create()

class ToursEdit(BaseAdminView):

    def get(self, tour_id):
        return self.tours_edit(tour_id)
    
    def post(self, tour_id):
        return self.tours_edit(tour_id)

class ToursApprove(BaseAdminView):

    def post(self, tour_id):
        return self.tours_approve(tour_id)

class ToursReject(BaseAdminView):

    def post(self, tour_id):
        return self.tours_reject(tour_id)

class TourDelete(BaseAdminView):

    def post(self, tour_id):
        return self.tour_delete(tour_id)


# =========================================================
# 3. API ROUTES (TOURS & DASHBOARD)
# =========================================================

class ApiTourList(BaseAdminView):

    def get(self):
        return self.api_tour_list()

class ApiMyTour(BaseAdminView):

    def get(self):
        return self.api_my_tour()

class ApiCurrentUser(BaseAdminView):

    def get(self):
        return self.api_current_user()

class ApiEditorNotifications(BaseAdminView):

    def get(self):
        return self.api_editor_notifications()

class ApiStatistics(BaseAdminView):

    def get(self):
        return self.api_statistics()

class ApiStatisticsEditor(BaseAdminView):

    def get(self):
        return self.api_statistics_editor()

class ApiPendingTour(BaseAdminView):

    def get(self):
        return self.api_pending_tour()

class ApiApprovedTour(BaseAdminView):

    def get(self):
        return self.api_approved_tour()

class ApiRejectedTour(BaseAdminView):

    def get(self):
        return self.api_rejected_tour()


class ApiApiTour(BaseAdminView):

    def get(self):
        return self.api_api_tour()


class ApiChartData(BaseAdminView):

    def get(self):
        return self.api_chart_data()


class ApiTourDetail(BaseAdminView):

    def get(self, tour_id):
        return self.api_tour_detail(tour_id)


class ApiCreateTour(BaseAdminView):

    def post(self):
        return self.api_create_tour()


class ApiEditTour(BaseAdminView):

    def post(self, tour_id):
        return self.api_edit_tour(tour_id)


class ApiUploadImage(BaseAdminView):

    def post(self):
        return self.api_upload_image()


# =========================================================
# 4. API ROUTES (USERS & SETTINGS)
# =========================================================

class ApiUsersList(BaseAdminView):
    def get(self):
        return self.api_users_list()


class ApiCreateUser(BaseAdminView):
    def post(self):
        return self.api_create_user()


class ApiUpdateUser(BaseAdminView):

    def post(self):
        return self.api_update_user() # Hỗ trợ POST dự phòng


class ApiToggleUserStatus(BaseAdminView):

    def post(self, user_id):
        return self.api_toggle_user_status(user_id)


class ApiSettings(BaseAdminView):

    def get(self):
        return self.api_get_settings()
    
    def post(self):
        return self.api_update_settings()


class ApiTestEmail(BaseAdminView):

    def post(self):
        return self.api_test_email()


# Auth & Pages
admin_bp.add_url_rule('/login', 'login', Login.as_view('login'))
admin_bp.add_url_rule('/logout', 'logout', Logout.as_view('logout'))
admin_bp.add_url_rule('/dashboard', 'dashboard', Dashboard.as_view('dashboard'))
admin_bp.add_url_rule('/editor-dashboard', 'editor_dashboard', EditorDashboard.as_view('editor_dashboard'))
admin_bp.add_url_rule('/profile', 'profile', Profile.as_view('profile'))

# Tour Pages
admin_bp.add_url_rule('/tour', 'tour_list', TourList.as_view('tour_list'))
admin_bp.add_url_rule('/tours', 'tours_list', TourList.as_view('tours_list')) # Alias chống lỗi url_for('admin.tours_list')
admin_bp.add_url_rule('/tour/create', 'tour_create', TourCreate.as_view('tour_create'))
admin_bp.add_url_rule('/tour/<int:tour_id>/edit', 'tours_edit', ToursEdit.as_view('tours_edit'))
admin_bp.add_url_rule('/tour/<int:tour_id>/approve', 'tours_approve', ToursApprove.as_view('tours_approve'))
admin_bp.add_url_rule('/tour/<int:tour_id>/reject', 'tours_reject', ToursReject.as_view('tours_reject'))
admin_bp.add_url_rule('/tour/<int:tour_id>/delete', 'tour_delete', TourDelete.as_view('tour_delete'))

# API Tours & Dashboards
admin_bp.add_url_rule('/api/tour', 'api_tour_list', ApiTourList.as_view('api_tour_list'))
admin_bp.add_url_rule('/api/my-tour', 'api_my_tour', ApiMyTour.as_view('api_my_tour'))
admin_bp.add_url_rule('/api/current-user', 'api_current_user', ApiCurrentUser.as_view('api_current_user'))
admin_bp.add_url_rule('/api/editor-notifications', 'api_editor_notifications', ApiEditorNotifications.as_view('api_editor_notifications'))
admin_bp.add_url_rule('/api/statistics', 'api_statistics', ApiStatistics.as_view('api_statistics'))
admin_bp.add_url_rule('/api/statistics/editor', 'api_statistics_editor', ApiStatisticsEditor.as_view('api_statistics_editor'))
admin_bp.add_url_rule('/api/tour/pending', 'api_pending_tour', ApiPendingTour.as_view('api_pending_tour'))
admin_bp.add_url_rule('/api/tour/approved', 'api_approved_tour', ApiApprovedTour.as_view('api_approved_tour'))
admin_bp.add_url_rule('/api/tour/rejected', 'api_rejected_tour', ApiRejectedTour.as_view('api_rejected_tour'))
admin_bp.add_url_rule('/api/tour/external', 'api_api_tour', ApiApiTour.as_view('api_api_tour'))
admin_bp.add_url_rule('/api/chart-data', 'api_chart_data', ApiChartData.as_view('api_chart_data'))
admin_bp.add_url_rule('/api/tour/<int:tour_id>', 'api_tour_detail', ApiTourDetail.as_view('api_tour_detail'))
admin_bp.add_url_rule('/api/tour/create', 'api_create_tour', ApiCreateTour.as_view('api_create_tour'))
admin_bp.add_url_rule('/api/tour/<int:tour_id>/edit', 'api_edit_tour', ApiEditTour.as_view('api_edit_tour'))
admin_bp.add_url_rule('/api/upload-image', 'api_upload_image', ApiUploadImage.as_view('api_upload_image'))

# API Users & Settings
admin_bp.add_url_rule('/api/users', 'api_users_list', ApiUsersList.as_view('api_users_list'))
admin_bp.add_url_rule('/api/users/create', 'api_create_user', ApiCreateUser.as_view('api_create_user'))
admin_bp.add_url_rule('/api/users/update', 'api_update_user', ApiUpdateUser.as_view('api_update_user'))
admin_bp.add_url_rule('/api/users/<int:user_id>/toggle-status', 'api_toggle_user_status', ApiToggleUserStatus.as_view('api_toggle_user_status'))
admin_bp.add_url_rule('/api/settings', 'api_settings', ApiSettings.as_view('api_settings'))
admin_bp.add_url_rule('/api/settings/test-email', 'api_test_email', ApiTestEmail.as_view('api_test_email'))