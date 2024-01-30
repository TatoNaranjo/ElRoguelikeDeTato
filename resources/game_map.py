from __future__ import annotations

from typing import Iterable,Iterator, Optional, TYPE_CHECKING
import numpy as np #type: ignore
from tcod.console import Console


from resources.entity import Actor, Item
from resources import tile_types


if TYPE_CHECKING:
    from resources.engine import Engine
    from resources.entity import Entity

class GameMap:
    
    # The initializer takes width and height integers and assigns them in one line.
    def __init__(
            self,engine:Engine,width:int,height:int,entities:Iterable[Entity]=()
    ):
        # We create a 2D array filled with the same values, which in this case is the
        # tile_types.floor that we created. This will fill self.tiles with floor tiles.
        self.engine = engine
        self.width,self.height = width,height
        self.entities = set(entities)
        self.tiles = np.full((width,height),fill_value=tile_types.wall,order="F")
        self.visible = np.full(
            (width,height),fill_value=False, order="F"
            ) # Tiles the player can currently see.
        self.explored = np.full(
            (width,height),fill_value=False,order="F"
            ) # Tiles the player has seen before

        #Initial location of the next level downstairs.
        self.down_stairs_location=(0,0)

    @property
    def gamemap(self) -> GameMap:
        return self
    
    @property
    def actors(self)-> Iterator[Actor]:
        """Iterate over this maps living actos."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity,Actor) and entity.is_alive
        )
    
    @property
    def items(self)->Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity,Item))

        # Iterates through all the entities, if one is found that blocks movement and occupies the given
        # Location_x and location_y coordinates, returns that Entity, otherwise return None instead.
    def get_blocking_entity_at_location(
            self,location_x:int,location_y:int,
            )->Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement 
                and entity.x == location_x 
                and entity.y== location_y
                ):
                return entity
        
        return None

    def get_actor_at_location(self,x:int,y:int)->Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None
    
    # This method returns true if the given x and y values are within the map's boundaries.
    # Used to ensure the player doesn't move beyond the map into the void.
    def in_bounds(self,x:int,y:int) ->bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0<=x<self.width and 0<=y<self.height
    
    # Using the console class's tiles_rgb method, now we render the entire map.
    # Much faster than console.print.
    def render(self,console:Console)->None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "Explored" array, then draw it with the "dark" colors.
        Otherwise the default is "SHROUD".
        
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist = [self.visible,self.explored],
            choicelist = [self.tiles["light"],self.tiles["dark"]],
            default = tile_types.SHROUD,
        )

        # Using a function lambda to define a order from 1 (Corpse, lowest) to 3
        # (Actor, Highest)
        entities_sorted_for_rendering = sorted(
            self.entities, key = lambda x:x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x,entity.y]:
                console.print(
                    x=entity.x,y=entity.y,string = entity.char,fg = entity.color
                )
    
#Creates a new game map each time we go down a floor, using the variables that 
#Gameworld stores.
class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.

    """

    def __init__(
            self,
            *,
            engine:Engine,
            map_width:int,
            map_height:int,
            max_rooms:int,
            room_min_size:int,
            room_max_size:int,
            current_floor:int=0
    ):
            self.engine = engine

            self.map_width = map_width
            self.map_height = map_height

            self.max_rooms = max_rooms

            self.room_min_size = room_min_size
            self.room_max_size = room_max_size

            self.current_floor = current_floor
    
    def generate_floor(self)->None:
        from resources.procgen import generate_dungeon

        self.current_floor+=1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,

            engine = self.engine
        )
        