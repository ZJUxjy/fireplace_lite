#!/usr/bin/env python3
"""
卡牌信息查询脚本
用法: python show_card.py <卡牌ID>
示例: python show_card.py GIL_833
"""

import sys
import xml.etree.ElementTree as ET
from hearthstone.enums import CardType, CardClass, Rarity, Race, CardSet

# 枚举映射
CARD_TYPE_NAMES = {ct.value: ct.name for ct in CardType}
CLASS_NAMES = {cc.value: cc.name for cc in CardClass}
RARITY_NAMES = {r.value: r.name for r in Rarity}
RACE_NAMES = {r.value: r.name for r in Race}
CARD_SET_NAMES = {cs.value: cs.name for cs in CardSet}

# GameTag 常用映射
TAG_NAMES = {
    45: "HEALTH (生命值)",
    47: "ATK (攻击力)",
    48: "COST (费用)",
    114: "ELITE (橙卡)",
    183: "CARD_SET (扩展包)",
    185: "CARDNAME (卡牌名)",
    184: "CARDTEXT (卡牌描述)",
    190: "TAUNT (嘲讽)",
    199: "CLASS (职业)",
    200: "CARDRACE (种族)",
    202: "CARDTYPE (卡牌类型)",
    203: "RARITY (稀有度)",
    218: "BATTLECRY (战吼)",
    219: "CHARGE (冲锋)",
    215: "DIVINE_SHIELD (圣盾)",
    220: "DEATHRATTLE (亡语)",
    32: "TRIGGER_VISUAL (触发效果)",
    321: "COLLECTIBLE (可收集)",
    342: "ARTISTNAME (画家)",
    351: "FLAVORTEXT (趣味文字)",
    1427: "SPELLBURST (法术迸发)",
    1211: "ELUSIVE (无法被指定)",
    1720: "TRADEABLE (可交易)",
    2332: "DREDGE",
    3318: "MINIATURIZE (微型)",
    2247: "COLOSSAL (巨型)",
    2821: "OVERHEAL (过量治疗)",
    2772: "TITAN (泰坦)",
    1085: "REBORN (复生)",
    189: "FREEZE (冻结)",
    191: "STEALTH (潜行)",
    192: "CANT_ATTACK (不能攻击)",
    193: "WINDFURY (风怒)",
    208: "SECRET (奥秘)",
    237: "DIVINE_SHIELD (圣盾)",
    239: "POISONOUS (剧毒)",
    365: "SPELLPOWER (法术强度)",
    426: "LIFESTEAL (吸血)",
    453: "RUSH (突袭)",
    567: "MAGNETIC (磁力)",
    596: "ECHO (回响)",
    976: "INVOKETWICE (双倍祈求)",
    1144: "QUEST (任务)",
    1262: "OVERLOAD (过载)",
    1406: "COMBO (连击)",
    1466: "CORRUPT (腐蚀)",
    1717: "DORMANT (休眠)",
}


def get_localized_text(tag, lang='zhCN'):
    """获取指定语言的文本"""
    for child in tag:
        if child.tag == lang:
            return child.text or ''
    # 如果没有找到指定语言，返回 enUS
    for child in tag:
        if child.tag == 'enUS':
            return child.text or ''
    return ''


def get_tag_value(tag):
    """获取 Tag 的值"""
    if tag.get('type') == 'Int':
        return tag.get('value')
    elif tag.get('type') == 'String':
        return tag.text or ''
    elif tag.get('type') == 'LocString':
        return get_localized_text(tag)
    return tag.get('value', '')


def format_card_text(text):
    """格式化卡牌描述文本"""
    import html
    import re
    text = html.unescape(text)
    text = text.replace('<b>', '\033[1m')
    text = text.replace('</b>', '\033[0m')
    text = text.replace('[x]', '')
    text = text.replace('_', ' ')
    # 删除所有换行符
    text = text.replace('\n', '')
    # 清理多余空格
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.strip()


def show_card(card_id):
    """显示卡牌信息"""
    try:
        tree = ET.parse('/home/xjingyao/code/fireplace/fireplace/cards/CardDefs.xml')
    except FileNotFoundError:
        print("错误: 找不到 CardDefs.xml 文件")
        return

    root = tree.getroot()

    for entity in root.findall('.//Entity'):
        if entity.get('CardID') == card_id:
            print("\n" + "=" * 60)
            print(f"  卡牌ID: {card_id}")
            print(f"  DBF ID: {entity.get('ID')}")
            print("=" * 60)

            # 收集所有 Tag
            tags = {}
            for tag in entity.findall('Tag'):
                enum_id = int(tag.get('enumID'))
                if enum_id not in tags:
                    tags[enum_id] = tag

            # 基础信息
            print("\n【基础信息】")
            if 185 in tags:
                print(f"  名称: {get_localized_text(tags[185])} ({get_localized_text(tags[185], 'enUS')})")

            if 199 in tags:
                class_val = int(tags[199].get('value'))
                print(f"  职业: {CLASS_NAMES.get(class_val, class_val)}")

            if 202 in tags:
                type_val = int(tags[202].get('value'))
                print(f"  类型: {CARD_TYPE_NAMES.get(type_val, type_val)}")

            if 203 in tags:
                rarity_val = int(tags[203].get('value'))
                rarity_cn = {1: '普通', 3: '稀有', 4: '史诗', 5: '传说'}
                print(f"  稀有度: {rarity_cn.get(rarity_val, RARITY_NAMES.get(rarity_val, rarity_val))}")

            if 183 in tags:
                set_val = int(tags[183].get('value'))
                print(f"  扩展包: {CARD_SET_NAMES.get(set_val, set_val)}")

            # 数值属性
            print("\n【数值属性】")
            if 48 in tags:
                print(f"  费用: {tags[48].get('value')}")
            if 47 in tags:
                print(f"  攻击力: {tags[47].get('value')}")
            if 45 in tags:
                print(f"  生命值: {tags[45].get('value')}")
            if 200 in tags:
                race_val = int(tags[200].get('value'))
                race_cn = {20: '野兽', 14: '鱼人', 15: '恶魔', 17: '机械', 18: '元素',
                          23: '龙', 24: '图腾', 25: '海盗', 26: '野猪人'}
                print(f"  种族: {race_cn.get(race_val, RACE_NAMES.get(race_val, race_val))}")

            # 关键词
            print("\n【关键词】")
            keyword_cn = {
                190: '嘲讽', 218: '战吼', 219: '冲锋', 215: '圣盾', 220: '亡语',
                189: '冻结', 193: '风怒', 208: '奥秘', 239: '剧毒', 426: '吸血',
                453: '突袭', 1085: '复生', 1427: '法术迸发', 1211: '无法被指定',
                1720: '可交易', 2772: '泰坦', 596: '回响', 567: '磁力',
                2821: '过量治疗', 191: '潜行'
            }
            keywords = []
            for tag_id, cn_name in keyword_cn.items():
                if tag_id in tags and tags[tag_id].get('value') == '1':
                    keywords.append(cn_name)
            if keywords:
                print(f"  {', '.join(keywords)}")
            else:
                print("  (无)")

            # 卡牌描述
            if 184 in tags:
                print("\n【卡牌效果】")
                text = format_card_text(get_localized_text(tags[184]))
                print(f"  {text}")

            # 趣味文字
            if 351 in tags:
                print("\n【趣味文字】")
                text = format_card_text(get_localized_text(tags[351]))
                print(f"  {text}")

            # 画家
            if 342 in tags:
                print(f"\n【画家】 {tags[342].text}")

            print("\n" + "=" * 60)
            return

    print(f"未找到卡牌: {card_id}")


def main():
    if len(sys.argv) < 2:
        print("用法: python show_card.py <卡牌ID>")
        print("示例: python show_card.py GIL_833")
        print("\n也可以直接运行进入交互模式:")
        card_id = input("请输入卡牌ID: ").strip()
        if card_id:
            show_card(card_id)
    else:
        show_card(sys.argv[1])


if __name__ == '__main__':
    main()
