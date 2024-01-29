from __future__ import annotations
from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

"""
This component holds all the level up logic of our character.
"""

class Level(BaseComponent):
    parent: Actor

    """
    The current level of the Entity defaults to 1,
    The current experience of the Entity defaults to 0

    We have to set a level up base number for leveling up.
    level_up_factor: The number to multiply against the Entity's current level.
    The xp_given is determinated by how much XP will gain the player for killing an entity.
    """

    def __init__(
        self,
        current_level:int=1,
        current_xp: int = 0,
        level_up_base:int = 0,
        level_up_factor:int = 150,
        xp_given :int = 0,

    ):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor
        self.xp_given = xp_given
    

    # How much experience the player needs until hitting the next level.
    @property
    def experience_to_next_level(self)->int:
        return self.level_up_base + self.current_level * self.level_up_factor
    
    # The player needs to level up?
    @property
    def requires_level_up(self)->bool:
        return self.current_xp > self.experience_to_next_level
    

    # If the current_xp is higher than the experience_to_next_level, the player levels up.
    def add_xp(self, xp:int)->None:
        if xp == 0 or self.level_up_base ==0:
            return
        
        self.current_xp += xp

        self.engine.message_log.add_message(f"You gain {xp} experience points.")

        if self.requires_level_up:
            self.engine.message_log.add_message(
                f"You advance to level {self.current_level+1}!"
            )
    
    def increase_level(self) ->None:
        self.current_xp -= self.experience_to_next_level

    def increase_max_hp(self,amount:int = 20)->None:
        self.parent.fighter.max_hp +=amount
        self.parent.fighter.hp += amount
        self.engine.message_log.add_message("Your Health Improves!")

        self.increase_level()

    def increase_power(self,amount:int = 1)->None:
        self.parent.fighter.power += amount

        self.engine.message_log.add_message("You Feel Stronger!")
        self.increase_level()
    
    def increase_defense(self,amount:int = 1)->None:
        self.parent.fighter.defense +=amount
        self.engine.message_log.add_message("Your movements are getting swifter!")

        self.increase_level()