
"""
client router - define routes for client
"""

from flask import Blueprint, render_template, request, jsonify, abort, make_response, session
import json
import base
import client_controller


# Create Blueprint for client with url_prefix is empty to redirect route
# and template_folder for html files in folder client
client_bp = Blueprint('client', __name__, 
                     url_prefix='',
                     template_folder='templates')


controller = client_controller.Controller


class BaseClientView(base.BaseView, controller):
    
    def __init__(self):
        super().__init__()

class Home(BaseClientView):
    
    def get(self):
        data = self.list_tour(limit=10, offset=0)
        return jsonify({
            'tours': data,
            'self': 'home'
        })


class Search(BaseClientView):
    
    def get(self):
        keyword = request.args.get('q', '').strip()
        page = request.args.get('page', 1)
        data = self.search_tours(keyword, page)
        
        return jsonify({
            'tours': data,
            'self': 'search',
            'keyword': keyword,
            'page': page
        })


class Tours(BaseClientView):
    
    def get(self):
        data = self.list_tour(limit=10, offset=0)
        
        return jsonify({
            'tours': data,
            'self': 'tours'
        })


class ToursDetail(BaseClientView):
    
    def get(self, tours_slug):
        data = self.tours_detail(tours_slug)
        
        if not data:
            abort(404)

        tour = data.get("tour")
        is_saved = data.get("is_saved")
        user_id = data.get("user_id")

        return jsonify({
            'tour': tour,
            'is_saved': is_saved,
            'user_id': user_id,
        })


class Login(BaseClientView):
    
    def get(self):
        return render_template('client/login.html')
    
    def post(self):
        self.check_login()


class Register(BaseClientView):
    
    def get(self):
        return render_template('client/register.html')
    
    def post(self):
        self.register()


class ForgotPassword(BaseClientView):
    
    def get(self):
        return render_template('client/forgot_password.html')
    
    def post(self):
        self.forgot_password()


class Introducing(BaseClientView):
    
    def get(self):
        return render_template('client/introducing.html')


class Security(BaseClientView):
    
    def get(self):
        return render_template('client/security.html')


class Term(BaseClientView):
    
    def get(self):
        return render_template('client/term_of_service.html')


class Contact(BaseClientView):
    
    def get(self):
        return render_template('client/contact.html')


class Guide(BaseClientView):
    
    def get(self):
        return render_template('client/guide.html')


client_bp.add_url_rule('/', 'home', Home.as_view('home'))
client_bp.add_url_rule('/home', 'home1', Home.as_view('home1'))
client_bp.add_url_rule('/search', 'search', Search.as_view('search'))
client_bp.add_url_rule('/tours', 'tours', Tours.as_view('tours'))
client_bp.add_url_rule('/tour/<tours_slug>', 'tours_detail', ToursDetail.as_view('tours_detail'))

client_bp.add_url_rule('/signin', 'user_login', Login.as_view('user_login'))
client_bp.add_url_rule('/signup', 'register', Register.as_view('register'))
client_bp.add_url_rule('/forgot_password', 'forgot_password', ForgotPassword.as_view('forgot_password'))

client_bp.add_url_rule('/introducing', 'introducing', Introducing.as_view('introducing'))
client_bp.add_url_rule('/security', 'security', Security.as_view('security'))
client_bp.add_url_rule('/term', 'term_of_service', Term.as_view('term_of_service'))
client_bp.add_url_rule('/contact', 'contact', Contact.as_view('contact'))
client_bp.add_url_rule('/guide', 'guide', Guide.as_view('guide'))