from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
class Action:
    def perform(self,engine:Engine,entity:Entity)-> None:
        """
        Perform this action with the objects needed to determine it's scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.        
        
        """
        raise NotImplementedError()

#Used to describe when the user hit the Esc key to Exit the Game
class EscapeAction(Action):
    def perform(self,engine:Engine,entity:Entity)->None:
        raise SystemExit()

class ActionWithDirection(Action):
    def __init__(self,dx:int, dy:int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self,engine:Engine,entity:Entity)->None:
        raise NotImplementedError()

# This function describes the action used to perform a melee action.
class MeleeAction(ActionWithDirection):
    def perform(self,engine:Engine,entity:Entity)-> None:
        dest_x = entity.x+self.dx
        dest_y = entity.y+self.dy
        target = engine.game_map.get_blocking_entity_at_location(dest_x,dest_y)
        if not target:
            return #There's nothing to attack
        print(f"You kick the {target.name}, much to its annoyance!")



#Used to describe when our player moves around.
class MovementAction(ActionWithDirection):
    #This passes the direction where the player is trying to move.
    def perform(self,engine:Engine,entity:Entity)-> None:
        dest_x = entity.x+self.dx
        dest_y = entity.y+self.dy
        
        # Passing in the engine and the entity performing the action to each Action sublass.

        # We check if we're out of bounds, if it is right, just return without doing nothing.
        if not engine.game_map.in_bounds(dest_x,dest_y):
            return #Destination is out of Bounds.
        
        # We check if the destination is blocked by a entity, if it is right just return 
        # without doing anything.
        if engine.game_map.get_blocking_entity_at_location(dest_x,dest_y):
            return #Destination is blocked by an entity.
        
        # We check if we're in a non walkable place, 
        # if it is right, just return without doing nothing.
        if not engine.game_map.tiles["walkable"][dest_x,dest_y]:
            return #Destination is blocked by a tile.

        entity.move(self.dx,self.dy)

# This function decides which class between MeleeAction and MovementAction to return.
class BumpAction(ActionWithDirection):
    def perform(self,engine:Engine, entity:Entity)-> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_location(dest_x,dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine,entity)
        
        else:
            return MovementAction(self.dx, self.dy).perform(engine,entity)