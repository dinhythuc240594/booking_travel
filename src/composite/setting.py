
from composite.abstract_setting import AbstractSettingNode
from typing import List
from database import (
    Setting,
)


class SettingLeaf(AbstractSettingNode):

    """Leaf: Một cấu hình đơn lẻ (VD: smtp_port)"""
    def __init__(self, setting: Setting):
        self.setting = setting

    def to_dict(self) -> dict:
        return {
            self.setting.key: {
                'value': self.setting.value,
                'description': self.setting.description,
                'category': self.setting.category
            }
        }


class SettingCategoryComposite(AbstractSettingNode):

    """Composite: Một nhóm cấu hình (VD: Thư mục API Settings, SMTP Settings)"""
    def __init__(self, category_name: str):
        self.category_name = category_name
        self.children: List[AbstractSettingNode] = []

    def add(self, component: AbstractSettingNode):
        self.children.append(component)

    def to_dict(self) -> dict:
        """Gom toàn bộ dữ liệu của các cấu hình con (trả về JSON cho Frontend)"""
        category_data = {}
        for child in self.children:
            category_data.update(child.to_dict())
        return {self.category_name: category_data}