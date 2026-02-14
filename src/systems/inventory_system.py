# File: src/systems/inventory_system.py
from typing import Optional
from src.models.actor import Actor
from src.models.item import Item
from src.systems.growth_system import GrowthSystem

class InventorySystem:
    """
    아이템 획득, 장착, 해제 등을 관리하는 시스템.
    장비 변경 시 Actor의 Dirty Flag를 켜서 스탯 재계산을 유도합니다.
    """

    @staticmethod
    def add_item(actor: Actor, item: Item):
        """인벤토리에 아이템을 추가합니다."""
        actor.inventory.append(item)
        # 획득만으로는 스탯이 변하지 않으므로 dirty 처리 안 함

    @staticmethod
    def equip_item(actor: Actor, item: Item) -> bool:
        """
        아이템을 장착하고 스탯을 갱신합니다.
        """
        if item not in actor.inventory:
            return False
            
        slot = item.slot
        if not slot:
            return False
            
        # 기존 장착 해제
        if actor.equipment.get(slot):
            InventorySystem.unequip_item(actor, slot)
            
        # 장착
        actor.equipment[slot] = item
        actor.inventory.remove(item)
        
        # [최적화] 장비 변경 발생 -> Dirty Flag On
        actor.mark_dirty()
        
        # HP/MP 최대치 갱신 (내부적으로 get_scaled_stat 호출 시 재계산됨)
        GrowthSystem.refresh_stats(actor)
        return True

    @staticmethod
    def unequip_item(actor: Actor, slot: str) -> bool:
        """
        아이템을 해제하고 인벤토리로 되돌립니다.
        """
        item = actor.equipment.get(slot)
        if not item:
            return False
            
        actor.equipment[slot] = None
        actor.inventory.append(item)
        
        # [최적화] 장비 해제 발생 -> Dirty Flag On
        actor.mark_dirty()
        
        GrowthSystem.refresh_stats(actor)
        return True