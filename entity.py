from __future__ import annotations

import copy
from typing import Optional,Tuple,Type, TypeVar, TYPE_CHECKING
from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import GameMap

T = TypeVar("T",bound="Entity")
class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    gamemap:GameMap
    # Initializer takes four arguments: x,y,char,color
    """
    x and y: Entity's coordinates on the map.
    char: character used to represent the entity.
    color: color we'll use when drawing the entity, represented on a RGB Tuple of three integers.
    name: What's the entity is called.
    blocks_movement: describes if this entity can be moved over or not. 
                    (There are items and comsumables ideas to make this set to False)
     """
    def __init__(
        self,
        gamemap:Optional[GameMap]=None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int,int,int] = (255,255,255),
        name: str = "<unnamed>",
        blocks_movement:bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if gamemap:
            #If gamemap isn't provided now then it will be set later.
            self.gamemap=gamemap
            gamemap.add(self)


    # Takes the GameMap instance, along with x and y for locations. It then creates a clone of the
    # Instance of Entity and assigns the x and y variables to it. It then adds the entity to the gamemap's
    # entities and returns the clone.
    def spawn(self:T,gamemap:GameMap,x:int, y:int)->T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone    

    def place(self, x:int, y:int, gamemap:Optional[GameMap]=None)->None:
        """Place this entity at a new location. Handles moving across GameMaps"""
        self.x = x
        self.y = y

        if gamemap:
            if hasattr(self,"gamemap"): #Possibly undefined
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)
            
    #This method takes dx and dy as arguments, and uses them to modify the entity's position.
    def move(self,dx:int,dy:int)->None:
        # Move the entity by a given amount
        self.x +=dx
        self.y +=dy


class Actor(Entity):
    def __init__(
            self,
            *,
            x: int = 0,
            y:int = 0,
            char: str = "?",
            color: Tuple[int,int,int] = (255,255,255),
            name: str = "<Unnamed>",
            ai_cls: Type[BaseAI],
            fighter:Fighter
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            # We're passing block_movements as true every time, because we can assume
            # That all the "actors" will block movement
            blocks_movement=True,
            render_order = RenderOrder.ACTOR,
        )
        # Setting up the two components, class AI and Fighter
        # The idea is that each actor will need two things to function: 
        # 1. The ability to move around and make decisions, and the ability to take
        # (and receive) damage.

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter=fighter
        self.fighter.entity = self

    @property
    def is_alive(self)->bool:
        """Returns true as long as this actor can perform actions."""
        return bool(self.ai)
        



