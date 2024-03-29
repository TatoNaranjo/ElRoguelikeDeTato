#Import and inherit from BaseComponent.
from __future__ import annotations

from resources import color
from components.base_component import BaseComponent

from resources.render_order import RenderOrder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resources.entity import Actor
class Fighter(BaseComponent):
    parent: Actor
    """
    Hp -> Represents the entity's hit points.
    Defense -> Represents how much taken damage will be reduced.
    Power -> The Entity's Raw Attack Power.
    """
    def __init__(self, hp:int, base_defense:int, base_power:int):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power

    @property
    def hp(self)->int:
        return self._hp
    
    #When the actor die we use this die method to do several things:
    """
    Print out a message indicating the death of the entity.
    Set the entity character to %
    Set its color to red
    Set Blocks movement to false, so that entities can walk over the corpse
    remove the AI rom the entity. It'll be marked and won't take more turns
    Change the name to remains of {entity.name}
    """
    @hp.setter
    def hp(self,value:int)->None:
        #The HP will never be set to 0
        self._hp = max(0,min(value,self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()
    
    @property
    def defense(self) ->int:
        return self.base_defense+self.defense_bonus

    @property
    def power(self) ->int:
        return self.base_power+self.power_bonus
    
    @property
    def defense_bonus(self) ->int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0
    @property
    def power_bonus(self) ->int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        else:
            return 0
        

    def die(self)-> None:
        if self.engine.player is self.parent:
            death_message = "You Died!"
            death_message_color = color.player_die
            
        else:
            death_message = f"{self.parent.name} is Dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191,0,0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"Remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE
        
        self.engine.message_log.add_message(death_message,death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)
    
    # This function will restore a certain amount of HP, up to the maximum and return 
    # The amount that was healed. If the entity's health is at full just return()
    def heal(self,amount:int)->int:
        if self.hp == self.max_hp:
            return 0
        
        new_hp_value = self.hp+amount

        if new_hp_value>self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value-self.hp

        self.hp = new_hp_value
        return amount_recovered
    
    def take_damage(self,amount:int)-> None:
        self.hp -= amount


