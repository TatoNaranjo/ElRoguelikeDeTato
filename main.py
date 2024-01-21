#!/usr/bin/env python3
import tcod

#Importing the EscapeAction and MovementAction from actions and EventHandler from input_handlers
from actions import EscapeAction, MovementAction
from input_handlers import EventHandler

#Importing the Entity class into main.py
from entity import Entity



def main() ->None:
    #Defining Variables for the Screen Size. 
    #Todo: load this values from a JSON File.
    screen_width = 80
    screen_height = 50


    #tcod will use our font from dejavu10x10_gs_tc.png
    tileset = tcod.tileset.load_tilesheet(
        'src/dejavu10x10_gs_tc.png',32,8,tcod.tileset.CHARMAP_TCOD
    )

    #An instance of our EventHandler Class
    event_handler = EventHandler()

    #Initializing new entities
    player = Entity(int(screen_width/2),int(screen_height/2),"@",(255,255,255))
    npc = Entity(int(screen_width/2-5),int(screen_height/2),"@",(255,255,0))
    entities = {npc,player}

    #This creates the Screen
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "El Roguelike de Tato",
        vsync=True,
    ) as context:
        #Creates the console to display the elements

        #By default numpy acceses 2D arrays in [y,x] so this line reverses it to [x,y]
        root_console = tcod.console.Console(screen_width,screen_height,order = "F")

        #Game loop core init.
        while True:
            #Printing our @ character.
            root_console.print(x=player.x,y=player.y, string =player.char, fg=player.color)

            #This line is the core of the screen updating.
            #context.present updates the screen whit what we've told to display so far.
            context.present(root_console)

            root_console.clear();
            
            #If we hit the X button in the console's window, the game will exit.
            #That's our secure exit logic.
            for event in tcod.event.wait():
                
                #Sending the event to our event_handler's dispatch method, to send the
                #Event to its proper place.
                action = event_handler.dispatch(event)

                #If no valid key was pressed just skip the loop
                if action is None:
                    continue
                
                """
                if the action is an instance of the class MovementAction, we move our "@" character.
                We grab the dx and dy values to gave to MovementAction earlier,
                which will move our '@' character in which direction we want it to move.

                Regardless of what the value is, we add dx and dy to player_x and player_y respectively.
                Because the console is using player_x and player_y to draw where our '@' character is,
                modify these two values will cause the symbol to move.
                """
                if(isinstance(action,MovementAction)):
                    player.move(dx=action.dx,dy = action.dy)
    
                #Else we quit the program if the player hits 'Esc' key.
                elif isinstance(action,EscapeAction):
                    raise SystemExit()

if __name__ == "__main__":
    main()