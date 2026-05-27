from flask import Flask, request, session
from flask.views import MethodView

class BaseView(MethodView):
    """Base view - all views will inherit from this class"""
    pass