from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    parent: Actor

    # Weapon and armor attributes will hold the actual equippable entity.
    # Both can be set to none, cause it represents that nothing is equipped in those slots.
    def __init__(self, weapon: Optional[Item] = None, armor: Optional[Item] = None):
        self.weapon = weapon
        self.armor = armor


    """
    Experimental Stuff:
    These properties do the same thing, just for different things. 
    Both calculate the “bonus” gifted by equipment to either defense or power, 
    based on what's equipped. Notice that we take the “power” bonus from both weapons and armor
    , and the same applies to the “defense” bonus. 
    
    
    Test It:
    This opens the posibility to create weapons that increase both attack and defense 
    (maybe some sort of spiked shield) and armor that increases attack (something magical,
    maybe). 
    """
    @property
    def defense_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.defense_bonus

        return bonus

    @property
    def power_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.power_bonus

        return bonus


    # To check if an Item is equipped by the player or not.
    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item

    # Messages that will appear when the player adds or removes an Item of Equipment.
    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    # Method that get called when the player selects an equippable item.
        
    """
     It checks the equipment's type (to know which slot to put it in), and then checks to see 
     if the same item is already equipped to that slot.
     If it is, the player presumably wants to remove it. If not, the player wants to equip it.
    """
    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            slot = "weapon"
        else:
            slot = "armor"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)