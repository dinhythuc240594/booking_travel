from command.component import DatabaseCommand
import datetime

from database import Setting


class BulkUpdateSettingsCommand(DatabaseCommand):

    """Lệnh cập nhật cấu hình hệ thống (Settings) hàng loạt"""
    def __init__(self, settings_data: dict):
        self.settings_data = settings_data
        self.old_values = {}
        self.newly_created_keys = []

    def execute(self, session) -> None:
        for key, value in self.settings_data.items():
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                self.old_values[key] = setting.value
                setting.value = value if value else None
                setting.updated_at = datetime.datetime.utcnow()
            else:
                category = 'api' if 'api' in key.lower() or 'token' in key.lower() else ('smtp' if 'mail' in key.lower() or 'smtp' in key.lower() else 'general')
                new_setting = Setting(key=key, value=value if value else None, category=category)
                session.add(new_setting)
                self.newly_created_keys.append(key)
        session.flush()

    def undo(self, session) -> None:
        for key, old_val in self.old_values.items():
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                setting.value = old_val
        for key in self.newly_created_keys:
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                session.delete(setting)

