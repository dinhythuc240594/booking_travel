
"""
client router - define routes for client
"""

from flask import Blueprint, render_template, request, jsonify, abort, make_response, session, redirect
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
        data = self.list_tour()
        return jsonify({
            'tours': data,
            'self': 'home'
        })


class Search(BaseClientView):
    
    def get(self):
        data = self.search_tours()
        
        return jsonify({
            'tours': data,
            'self': 'search',
        })


class Tours(BaseClientView):
    
    def get(self):
        data = self.list_tour()
        
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
        related_tours = data.get("related_tours", [])

        return jsonify({
            'tour': tour,
            'is_saved': is_saved,
            'user_id': user_id,
            'relatedTours': related_tours
        })


class Profile(BaseClientView):

    def get(self):
        return self.profile_user()

    def post(self):
        return self.profile_user()


class Login(BaseClientView):
    
    def post(self):
        data = self.check_login()
        return data


class Register(BaseClientView):
    
    def post(self):
        data = self.register()
        return data


class ForgotPassword(BaseClientView):
    
    def post(self):
        return self.forgot_password()


class ResetPassword(BaseClientView):
    
    def get(self):
        import os
        token = request.args.get('token', '')
        frontend_url = os.environ.get('FRONTEND_URL') or 'http://localhost:3000'
        return redirect(f"{frontend_url}/reset-password?token={token}")

    def post(self):
        return self.reset_password_api()


class Bookings(BaseClientView):
    
    def get(self):
        return self.bookings()

    def post(self):
        return self.create_booking()


class CancelBooking(BaseClientView):
    
    def post(self, booking_id):
        return self.cancel_booking_route(booking_id)


class Location(BaseClientView):

    def get(self):
        return self.locations()


client_bp.add_url_rule('/search', 'search', Search.as_view('search'))
client_bp.add_url_rule('/tours', 'tours', Tours.as_view('tours'))
client_bp.add_url_rule('/tours/<tours_slug>', 'tours_detail', ToursDetail.as_view('tours_detail'))
client_bp.add_url_rule('/locations', 'locations', Location.as_view('locations'))
client_bp.add_url_rule('/bookings', 'bookings', Bookings.as_view('bookings'))
client_bp.add_url_rule('/bookings/cancel/<int:booking_id>', 'cancel_booking', CancelBooking.as_view('cancel_booking'))

client_bp.add_url_rule('/profile', 'profile', Profile.as_view('profile'))
client_bp.add_url_rule('/signin', 'signin', Login.as_view('signin'))
client_bp.add_url_rule('/signup', 'signup', Register.as_view('signup'))
client_bp.add_url_rule('/forgot_password', 'forgot_password', ForgotPassword.as_view('forgot_password'))
client_bp.add_url_rule('/reset_password', 'reset_password', ResetPassword.as_view('reset_password'))