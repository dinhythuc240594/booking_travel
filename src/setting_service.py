from database import get_session, Setting
from command.component import DBTransactionInvoker
from command.setting import BulkUpdateSettingsCommand
from composite.setting import SettingLeaf, SettingCategoryComposite

class SettingService:
    
    @staticmethod
    def get_settings_grouped(category_filter: str = None) -> dict:
        """Sử dụng Composite Pattern để nhóm Settings theo danh mục"""
        session = get_session()
        try:
            query = session.query(Setting)
            if category_filter:
                query = query.filter(Setting.category == category_filter)
            settings = query.all()

            # Phân loại vào Composite
            categories = {}
            for s in settings:
                cat_name = s.category or 'uncategorized'
                if cat_name not in categories:
                    categories[cat_name] = SettingCategoryComposite(cat_name)
                categories[cat_name].add(SettingLeaf(s))

            # Xuất dữ liệu
            result = {}
            for composite in categories.values():
                result.update(composite.to_dict())
            
            # Trả về format phẳng (nếu frontend cần giống cũ) hoặc phân cấp
            flat_result = {}
            for group in result.values():
                flat_result.update(group)
            return flat_result
        finally:
            session.close()

    @staticmethod
    def bulk_update(settings_data: dict) -> bool:
        """Sử dụng Command Pattern để cập nhật cài đặt an toàn"""
        session = get_session()
        invoker = DBTransactionInvoker()
        command = BulkUpdateSettingsCommand(settings_data)
        
        try:
            invoker.execute_transaction(session, [command])
            return True
        except Exception as e:
            return False
        finally:
            session.close()