from __future__ import annotations

from typing import List,Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction


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