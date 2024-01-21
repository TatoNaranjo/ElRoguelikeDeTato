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

#Used to describe when our player moves around.
class MovementAction(Action):
    #This passes the direction where the player is trying to move.
    def __init__(self,dx:int,dy:int):
        super().__init__()

        self.dx = dx
        self.dy = dy
    
    def perform(self,engine:Engine,entity:Entity)-> None:
        dest_x = entity.x+self.dx
        dest_y = entity.y+self.dy
        
        # Passing in the engine and the entity performing the action to each Action sublass.

        # We check if we're out of bounds, if it is right, just return without doing nothing.
        if not engine.game_map.in_bounds(dest_x,dest_y):
            return #Destination is out of Bounds.
        
        # We check if we're in a non walkable place, 
        # if it is right, just return without doing nothing.
        if not engine.game_map.tiles["walkable"][dest_x,dest_y]:
            return #Destination is blocked by a tile.

        entity.move(self.dx,self.dy)