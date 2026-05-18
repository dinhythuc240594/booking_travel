from flask import Flask, request, session
from flask.views import MethodView

class BaseView(MethodView):

    site = ''

    def __init__(self):
        self.site = self.get_locale()

    #### 2026-01-15 - add function getlocale to separate site ####
    def get_locale(self):
        if 'site' in session:
            print('return site lang')
            return session['site']
        session['site'] = 'vn'
        return session['site']