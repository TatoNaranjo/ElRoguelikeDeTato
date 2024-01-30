from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from resources.actions import Action, MeleeAction, MovementAction, WaitAction, BumpAction


if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):


    def perform(self)-> None:
        raise NotImplementedError()
    
    #get_path_to uses the "walkable" tiles on the pile to get the path
    #fromthe BaseAI's parent entity to whatever their target might be.
    #In this case, the target will always be the player.
    def get_path_to(self, dest_x:int, dest_y:int)->List[Tuple[int,int]]:
        """
        Compute and retunr a path to the target position.

        If there's no valid path then returns an empty list.
        """
        cost = np.array(self.entity.gamemap.tiles["walkable"],dtype = np.int8)

        for entity in self.entity.gamemap.entities:
            #Check that an entity blocks movement and the cost isn't zero (Blocking)
            for entity in self.entity.gamemap.entities:
                if entity.blocks_movement and cost[entity.x, entity.y]:
                    #Add to the cost of a blocked position.
                    #A lower number means more enemies will crowd behind each other in
                    #Hallways. A higher number means enemies will take longer paths in
                    #Order to surround the player.

                    cost[entity.x, entity.y]+=10
            
            #Create a graph from the cost array and pass that graph to a new pathfinder.
            graph = tcod.path.SimpleGraph(cost=cost,cardinal=2,diagonal=3)
            pathfinder = tcod.path.Pathfinder(graph)


            pathfinder.add_root((self.entity.x,self.entity.y)) #Start Position.

            #Compute the path to the destination and remove the starting point

            path: List[List[int]] = pathfinder.path_to((dest_x,dest_y))[1:].tolist()

            #Convert from List[List[int]] to List[Tuple[int,int]]
            return [(index[0],index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to it's previous AI
    If an actor occupies a tile it is randomly moving into, it will attack.
    
    
    Entity: The actor who is being confused.
    Previous:ai: The AI class that actor currently has. Used to get back to the previous AI's entity.
    Turns_remaining: How many turns the confussion effect will last for.
    """

    def __init__(
            self, entity:Actor,previous_ai:Optional[BaseAI],turns_remaining:int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    # It causes the entity to move in a randomly selected direction. Uses bumpAction so, it will try to move into a tile.
    # If there's an actor there, it will attack it.
    def perform(self) -> None:
        #Revert the AI Back to the original state if the effect has run its course.
        if self.turns_remaining<=0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick up a random direction.
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )
            # Every turn the remaining turns effect duration will decrease by 1.
            self.turns_remaining-=1

            # The actor will either ty to move or attack in the chosen random direction.
            # It's possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity,direction_x,direction_y).perform()
class HostileEnemy(BaseAI):
    def __init__(self,entity:Actor):
        super().__init__(entity)
        self.path: List[Tuple[int,int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx),abs(dy)) # Chebyshev Distance.

        """
        If the enemy is not in the player's vision, simply wait.
        If the player is right next to the entity, attack the player.
        If the player can see the entity, but the entity is too far away to attack, then move towards
        the player.
        """
        if self.engine.game_map.visible[self.entity.x,self.entity.y]:
            if distance <=1:
                return MeleeAction(self.entity, dx,dy).perform()
                
            self.path = self.get_path_to(target.x,target.y)
            
        if self.path:
            dest_x,dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y -self.entity.y,
            ).perform()
            
        return WaitAction(self.entity).perform()