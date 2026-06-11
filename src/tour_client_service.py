
from werkzeug.debug import console
import os
import re
import json
import shutil
from flask import jsonify

from database import (
    UserRole, 
    get_session, 
    Tour, 
    TourStatus
)
from command.component import DBTransactionInvoker
from command.tour import CreateTourCommand, UpdateTourCommand, SoftDeleteTourCommand, ApproveTourCommand, RejectTourCommand


class TourClientService:
    
    @staticmethod
    def get_tours_by_location(location_id: int):
        session = get_session()
        try:
            tours = session.query(Tour).filter(Tour.location_id == location_id).all()

            result = []
            for tour in tours:
                # Get category name
                category_name = tour.category.category_name if tour.category else None
                
                result.append({
                    'tour_id': tour.tour_id,
                    'title': tour.title,
                    'location': tour.location.name if tour.location else None,
                    'category_name': category_name,
                    'price_per_adult': tour.price_per_adult,
                    'price_per_child': tour.price_per_child,
                    'duration_days': tour.duration_days,
                    'thumbnail': tour.thumbnail
                })
            return result
        finally:
            session.close()

    
    @staticmethod
    def get_tour_by_id(tour_id: int):
        """Lấy chi tiết một tour cụ thể"""
        session = get_session()
        try:
            tour = session.query(Tour).filter(Tour.tour_id == tour_id).first()
            if tour:
                return {
                    'tour_id': tour.tour_id,
                    'title': tour.title,
                    'content': tour.content,
                    'summary': tour.summary,
                    'thumbnail': tour.thumbnail,
                    'images': json.loads(tour.images) if tour.images else [],
                    'location': tour.location.name if tour.location else None,
                    'category_name': tour.category.category_name if tour.category else None,
                    'duration_days': tour.duration_days,
                    'price_per_adult': tour.price_per_adult,
                    'price_per_child': tour.price_per_child,
                    'departure_date': tour.departure_date.isoformat() if tour.departure_date else None,
                    'return_date': tour.return_date.isoformat() if tour.return_date else None
                }
            return None
        finally:
            session.close()


    @staticmethod
    def get_by_category_name(category_name: str):
        session = get_session()
        try:
            if category_name == 'all':
                return session.query(Tour).filter(
                    Tour.is_deleted == False
                ).all()
            return session.query(Tour).filter(
                Tour.category_name == category_name,
                Tour.is_deleted == False
            ).all()
        finally:
            session.close()
