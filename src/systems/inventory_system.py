# File: src/systems/inventory_system.py
from typing import Optional
from src.models.actor import Actor
from src.models.item import Item
from src.systems.growth_system import GrowthSystem

class InventorySystem:
    """
    아이템 획득, 장착, 해제 및 인벤토리 관리를 담당하는 시스템.
    """

    @staticmethod
    def add_item(actor: Actor, item: Item):
        """인벤토리에 아이템 추가"""
        actor.inventory.append(item)
        print(f"[System] {actor.name}이(가) '{item.name}'을(를) 획득했습니다.")

    @staticmethod
    def equip_item(actor: Actor, item: Item) -> bool:
        """
        아이템을 장착합니다.
        1. 인벤토리에 있는지 확인
        2. 해당 슬롯이 비어있지 않다면 기존 장비 해제
        3. 장착 및 스탯 갱신
        """
        if item not in actor.inventory:
            print("[System] 소지하고 있지 않은 아이템입니다.")
            return False

        slot = item.slot
        if slot not in actor.equipment:
            print(f"[System] 착용할 수 없는 슬롯입니다: {slot}")
            return False

        # 이미 무언가 장착 중이라면 먼저 해제 (Swap)
        current_equipped = actor.equipment[slot]
        if current_equipped:
            InventorySystem.unequip_item(actor, slot)

        # 장착 로직
        actor.equipment[slot] = item
        actor.inventory.remove(item) # 인벤토리에서는 제거 (장비창으로 이동)
        
        # 장착 후 스탯 갱신 (최대 체력 등 변동 가능성)
        GrowthSystem.refresh_stats(actor)
        
        print(f"[System] {item.name}을(를) 장착했습니다.")
        return True

    @staticmethod
    def unequip_item(actor: Actor, slot: str) -> bool:
        """특정 슬롯의 아이템을 해제하여 인벤토리로 되돌립니다."""
        item = actor.equipment.get(slot)
        if not item:
            print("[System] 해당 슬롯에는 장비가 없습니다.")
            return False

        actor.equipment[slot] = None
        actor.inventory.append(item) # 다시 인벤토리로
        
        GrowthSystem.refresh_stats(actor)
        
        print(f"[System] {item.name} 장착을 해제했습니다.")
        return True