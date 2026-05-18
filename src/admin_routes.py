
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
                     template_folder='templates')


class Dashboard(base.BaseView):

    def get(self):
        return 'Dashboard'


admin_bp.add_url_rule('/dashboard', 'dashboard', Dashboard.as_view('dashboard'))
