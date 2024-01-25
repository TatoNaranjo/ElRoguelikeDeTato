#Import and inherit from BaseComponent.
from __future__ import annotations
from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from render_order import RenderOrder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor
class Fighter(BaseComponent):
    entity: Actor
    """
    Hp -> Represents the entity's hit points.
    Defense -> Represents how much taken damage will be reduced.
    Power -> The Entity's Raw Attack Power.
    """
    def __init__(self, hp:int, defense:int, power:int):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

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
        if self._hp == 0 and self.entity.ai:
            self.die()
    
    def die(self)-> None:
        if self.engine.player is self.entity:
            death_message = "You Died!"
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.entity.name} is Dead!"

        self.entity.char = "%"
        self.entity.color = (191,0,0)
        self.entity.blocks_movement = False
        self.entity.ai = None
        self.entity.name = f"Remains of {self.entity.name}"
        self.entity.render_order = RenderOrder.CORPSE
        
        print(death_message)
