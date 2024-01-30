#!/usr/bin/env python3
import tcod
import copy
import color
import traceback

import exceptions
import input_handlers

import setup_game


def save_game(handler:input_handlers.BaseEventHandler,filename:str) ->None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler,input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game Saved.")


def main() ->None:
    #Defining Variables for the Screen Size. 
    #Todo: load this values from a JSON File.
    screen_width = 80
    screen_height = 50

    #tcod will use our font from dejavu10x10_gs_tc.png
    tileset = tcod.tileset.load_tilesheet(
        'src/dejavu10x10_gs_tc.png',32,8,tcod.tileset.CHARMAP_TCOD
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()
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

        try:
            
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception: #Handle Exceptions in game
                    traceback.print_exc() # Print error to stderr
                    # Then print the error to the message log.
                    if isinstance(handler,input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(),color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit: #Save and quit
            save_game(handler,"savegame.sav")
            raise
        except BaseException: # Save on any other unexpected exceptions
            save_game(handler,"savegame.sav")
            raise

            

if __name__ == "__main__":
    main()