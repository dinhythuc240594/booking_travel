import database as db
from command_partern import DBTransactionInvoker, CreateTourCommand, UpdateTourPriceCommand
from composite_partern import LocationCompositeNode, TourLeafNode

class TourService:
    
    @staticmethod
    def create_tour(location_id: int, name: str, description: str, duration_days: int, price_per_person: float) -> bool:
        """Sử dụng Command Pattern để tạo Tour"""
        session = db.get_session()
        invoker = DBTransactionInvoker()
        
        command = CreateTourCommand(
            location_id=location_id, 
            name=name, 
            description=description, 
            duration_days=duration_days, 
            price_per_person=price_per_person
        )
        
        try:
            invoker.execute_transaction(session, [command])
            return True
        except Exception as e:
            return False
        finally:
            session.close()

    @staticmethod
    def get_tours_by_location_tree(location_id: int):
        """Sử dụng Composite Pattern để dựng cây Danh sách Tour theo Địa điểm"""
        session = db.get_session()
        try:
            # 1. Lấy thông tin Location
            location = session.query(db.Location).get(location_id)
            if not location:
                return None
            
            # 2. Khởi tạo Node Gốc (Composite)
            location_node = LocationCompositeNode(location)
            
            # 3. Lấy tất cả các Tour thuộc Location này và add vào (Leaves)
            tours = session.query(db.Tours).filter(db.Tours.location_id == location_id).all()
            for tour in tours:
                location_node.add_child(TourLeafNode(tour))
                
            # Trả về chuỗi hiển thị và tổng số lượng để dùng ở API hoặc render HTML
            return {
                "total_tours": location_node.get_tour_count(),
                "structure": location_node.show_tours()
            }
        finally:
            session.close()

    @staticmethod
    def update_tour_price(tour_id: int, new_price: float) -> bool:
        session = db.get_session()
        try:
            command = UpdateTourPriceCommand(tour_id=tour_id, new_price=new_price)
            invoker = DBTransactionInvoker()
            invoker.execute_transaction(session, [command])
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật giá Tour: {e}")
            return False
        finally:
            session.close()