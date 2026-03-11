import xml.etree.ElementTree as ET
import os

class CardTextLoader:
    def __init__(self):
        self.card_data = {}
        self._load()

    def _load(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'CardDefs.xml')
        if not os.path.exists(xml_path):
            # Try alternative path
            xml_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'fireplace', 'cards', 'CardDefs.xml'
            )

        if not os.path.exists(xml_path):
            print(f"Warning: CardDefs.xml not found at {xml_path}")
            return

        tree = ET.parse(xml_path)
        root = tree.getroot()

        for entity in root.findall('Entity'):
            card_id = entity.get('CardID')
            if not card_id:
                continue

            card_info = {}
            for tag in entity.findall('Tag'):
                name = tag.get('name')
                if name == 'CARDNAME':
                    card_info['name'] = self._get_locale_text(tag, 'zhCN')
                elif name == 'CARDTEXT':
                    card_info['text'] = self._get_locale_text(tag, 'zhCN')

            if card_info:
                self.card_data[card_id] = card_info

    def _get_locale_text(self, tag, locale='zhCN'):
        """获取指定语言的文本"""
        # 尝试指定语言
        text = tag.find(locale)
        if text is not None and text.text:
            return text.text

        # 回退到英文
        text = tag.find('enUS')
        if text is not None and text.text:
            return text.text

        return None

    def get_name(self, card_id):
        """获取卡牌中文名"""
        if card_id in self.card_data:
            return self.card_data[card_id].get('name')
        return None

    def get_text(self, card_id):
        """获取卡牌中文描述"""
        if card_id in self.card_data:
            return self.card_data[card_id].get('text')
        return None

    def get_card_info(self, card_id):
        """获取卡牌完整中文信息"""
        return self.card_data.get(card_id, {})

# 全局实例
card_text_loader = CardTextLoader()
