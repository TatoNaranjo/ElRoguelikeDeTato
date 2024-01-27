from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
from components.base_component import BaseComponent
import components.inventory
from exceptions import Impossible
from input_handlers import SingleRangedAttackHandler, AreaRangedAttackHandler

if TYPE_CHECKING:
    from entity import Actor,Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self,consumer:Actor)-> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer,self.parent)
    
    def activate(self,action: actions.ItemAction) ->None:
        """Invoke the item's hability
        
        `action` is the context for this activation.
        """
        raise NotImplementedError()
    
    def consume(self) -> None:
        """Remove the consumed item from its containign inventory."""
        entity = self.parent
        inventory = entity.parent

        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)

class ConfusionConsumable(Consumable):
    def __init__(self,number_of_turns:int):
        self.number_of_turns = number_of_turns


    # Will ask to the player to select a target location, and switch the game's event handler to
    # SingleRangedAttackHandler.The callback is a lambda function (an anonymous, inline function), 
    # which takes “xy” as a parameter. “xy” will be the coordinates of the target. The lambda function 
    # executes ItemAction, which receives the consumer, the parent (the item), and the “xy” coordinates.
    def get_action(self,consumer:Actor)->Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location.",color.needs_target
        )
        self.engine.event_handler = SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy:actions.ItemAction(consumer, self.parent,xy),
        )
        return None
    
    # What happens when select a target.
    
    def activate(self,action:actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        # In Sight
        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area you cannot see.")
        # A valid Actor
        if not target:
            raise Impossible("You must select an enemy to target!")
        # Not the player.
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")
        
        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",color.status_effect_applied
        )
        target.ai = components.ai.ConfusedEnemy(
            entity = target,previous_ai=target.ai,turns_remaining=self.number_of_turns,
        )
        self.consume()

class HealingConsumable(Consumable):
    def __init__(self,amount:int):
        self.amount = amount

    # Used when the subclasses are trying to cause the efect that they've defined for
    # Themselves.
    def activate (self,action:actions.ItemAction)->None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered>0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")
        

class FireballDamageConsumable(Consumable):
    def __init__(self,damage:int,radius:int):
        self.damage = damage
        self.radius = radius

    def get_action(self,consumer:Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location.",color.needs_target
        )
        self.engine.event_handler = AreaRangedAttackHandler(
            self.engine, 
            radius = self.radius,
            callback=lambda xy:actions.ItemAction(consumer,self.parent,xy),
        )
        return None
    
    def activate(self,action:actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area you cannot see.")
        
        targets_hit = False

        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy)<=self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True
        

        #If no enemies were hit at all, the Impossible exception is raised, and the scroll isn’t consumed.
        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()





"""

Damage: How much powerful will be the Lightning.
Maximum_range: How far it can reach.


"""        
class LightningDamageConsumable(Consumable):
    def __init__(self, damage:int, maximum_range:int):
        self.damage = damage
        self.maximum_range = maximum_range
    
    # Describes what to do when the player tries using it.
    def activate(self,action:actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x,actor.y]:
                distance = consumer.distance(actor.x,actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        
        # If the Lightning Consumable Strikes
        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strickes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        
        #If it not strikes, just give an error and don't consume the scroll.
        else:
            raise Impossible("No enemy is close enough to strike.")
