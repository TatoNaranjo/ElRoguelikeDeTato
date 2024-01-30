from __future__ import annotations

from typing import Optional,Tuple,TYPE_CHECKING

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item
class Action:
    def __init__(self,entity:Actor)->None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self)->Engine:
        """Return the engine this action belongs to"""
        return self.entity.gamemap.engine
        
    def perform(self)->None:

        """
        Perform this action with the objects needed to determine it's scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.        
        
        """
        raise NotImplementedError()

class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is a room for it."""
    def __init__(self,entity:Actor):
        super().__init__(entity)

    # Gets the entity's location and tries to find an item that exists in the same location,
    # Iterating through self.engine.game_map_items.
    
    # If a item is found, we try to add it to the inventory checking the capacity first, and 
    # Returning impossible if is full.
        
    # When adding an item to the inventory, we remove it from the game map and store it in the inventory
    # and print out a message. Then return ince only one item can be picked up per turn.
        
    # If no item is found, just return Impossible, informing the player that there's nothing there.
    def perform(self)->None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items)>= inventory.capacity:
                    raise exceptions.Impossible("Your Inventory Is Full.")
                
                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You Picked Up The {item.name}!")
                return
            
        raise exceptions.Impossible("There is nothing here to pick up.")



class ItemAction(Action):
    def __init__(
            self,entity:Actor, item: Item, target_xy: Optional[Tuple[int,int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    # Gets the actor at the target location.
    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)
    
    # Activates the consumable.
    def perform(self)-> None:
        """Invoke the item's hability, his action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)



    

# Used to describe when the user wants to drop some Item in the game. 
class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.inventory.toggle_equip(self.item)
        
        self.entity.inventory.drop(self.item)

class EquipAction(Action):
    def __init__(self,entity:Actor,item:Item):
        super().__init__(entity)

        self.item = item
    
    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)

# Represents an actor saying "I'll do nothing this turn."
class WaitAction(Action):
    def perform(self)->None:
        pass

class TakeStairsAction(Action):
    def perform(self) ->None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if(self.entity.x,self.entity.y) == self.engine.game_map.down_stairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.",color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")
class ActionWithDirection(Action):
    def __init__(self,entity:Actor,dx:int,dy:int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self)->Tuple[int,int]:
        """Returns this action destination."""
        return self.entity.x+self.dx,self.entity.y + self.dy
    
    @property
    def blocking_entity(self)-> Optional[Entity]:
        """Return the blocking entity at this actions destination"""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    
    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor if this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self)->None:
        raise NotImplementedError()

# This function describes the action used to perform a melee action.
class MeleeAction(ActionWithDirection):
    def perform(self)-> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to Attack.")
        
        damage = self.entity.fighter.power - target.fighter.defense

        #Updated MeleeAction to perform an Attack instead of just printing a message
        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.",attack_color
            )
            target.fighter.hp-=damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.",attack_color
            )



#Used to describe when our player moves around.
class MovementAction(ActionWithDirection):
    #This passes the direction where the player is trying to move.
    def perform(self)-> None:
        dest_x,dest_y = self.dest_xy
        
        # Passing in the engine and the entity performing the action to each Action sublass.

        # We check if we're out of bounds, if it is right, just return without doing nothing.
        if not self.engine.game_map.in_bounds(dest_x,dest_y):
            #Destination is out of Bounds.
            raise exceptions.Impossible("That Way is Blocked.")
        
        # We check if the destination is blocked by a entity, if it is right just return 
        # without doing anything.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x,dest_y):
            #Destination is blocked by an entity.
            raise exceptions.Impossible("That Way is Blocked.")
        
        # We check if we're in a non walkable place, 
        # if it is right, just return without doing nothing.
        if not self.engine.game_map.tiles["walkable"][dest_x,dest_y]:
            #Destination is blocked by a tile.
            raise exceptions.Impossible("That Way is Blocked.")

        self.entity.move(self.dx,self.dy)

# This function decides which class between MeleeAction and MovementAction to return.
class BumpAction(ActionWithDirection):
    def perform(self)-> None:
        if self.target_actor:
            return MeleeAction(self.entity,self.dx,self.dy).perform()
        
        else:
            return MovementAction(self.entity,self.dx,self.dy).perform()