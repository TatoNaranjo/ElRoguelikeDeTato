from __future__ import annotations

from typing import Optional,Tuple,TYPE_CHECKING

import color

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity
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

#Used to describe when the user hit the Esc key to Exit the Game
class EscapeAction(Action):
    def perform(self)->None:
        raise SystemExit()

#Represents an actor saying "I'll do nothing this turn."
class WaitAction(Action):
    def perform(self)->None:
        pass
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
            return #There's nothing to attack
        
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
            return #Destination is out of Bounds.
        
        # We check if the destination is blocked by a entity, if it is right just return 
        # without doing anything.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x,dest_y):
            return #Destination is blocked by an entity.
        
        # We check if we're in a non walkable place, 
        # if it is right, just return without doing nothing.
        if not self.engine.game_map.tiles["walkable"][dest_x,dest_y]:
            return #Destination is blocked by a tile.

        self.entity.move(self.dx,self.dy)

# This function decides which class between MeleeAction and MovementAction to return.
class BumpAction(ActionWithDirection):
    def perform(self)-> None:
        if self.target_actor:
            return MeleeAction(self.entity,self.dx,self.dy).perform()
        
        else:
            return MovementAction(self.entity,self.dx,self.dy).perform()