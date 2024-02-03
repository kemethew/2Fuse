import pygame, sys, time, threading
from TileAndGame_Classes import Game


if __name__ == '__main__':
    pygame.init()
    SCREEN_WIDTH = 680
    SCREEN_HEIGHT = 760
    COLORS = {'screen_color':(0,0,100),'red_tile':(255,0,0),
            'green_tile':(70,255,30),'blue_tile':(30,120,255),
            'red_shape_border':(150,50,20),'green_shape_border':(50,150,20),
            'blue_shape_border':(0,90,150),'gridline_color':(0,255,220),
            'shape_number_color':(255,255,255),'shape_star_color':(255,235,50),
            'color_white':(255,255,255),'active_tile_halo':(70,200,200),
            'active_tile_highlight':(240,240,240),'tile_border':(230,230,230),
            'score_color':(255,210,0),'score_prefix_color':(105,105,105),
            'best_score_color':(255,180,30), 'timer_border_color':(192,192,220), 
            'normal_running_timer_color':(0,255,0), 'boosted_running_timer_color':(153,255,255), 
            'game_over_remark_color':(51,153,255), 'semi_grey':(192,192,192), 
            'darker_semi_grey':(153,153,153)}
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    SCREEN.fill(COLORS['screen_color'])

    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, SCREEN)
    RUNNING = True
    while RUNNING:
        if game.IS_GETTING_READY:
            CURRENT_TIME = time.time()
            TIME_ELAPSED = CURRENT_TIME - game.GETTING_READY_START
            if game.GETTING_READY_START == 0:
                game.GETTING_READY_START = CURRENT_TIME
                game.display_game_screen_components()
                game.display_get_ready_surface()

                game.reset_cell_contents()
            elif TIME_ELAPSED > 0 and TIME_ELAPSED < 0.25:
                pass
            elif TIME_ELAPSED > 0.25 and TIME_ELAPSED < 1.5:
                game.display_get_ready_text()
            elif TIME_ELAPSED > 1.5 and TIME_ELAPSED < 3.58:
                if game.CELL_CONTENT[0][0] is None:
                    game.SCREEN.fill(game.COLORS['screen_color'])
                    game.display_game_screen_components()
                    game.assign_tiles()
                else:
                    CELL_ROW = int((TIME_ELAPSED - 1.5) // 0.52)
                    CELL_COLUMN = int((TIME_ELAPSED - 1.5 - CELL_ROW * 0.52) // 0.13)
                    game.render_get_ready_tile(CELL_ROW, CELL_COLUMN)
            else:
                game.IS_GETTING_READY = False
                game.reset_game_variables()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    RUNNING = False
        elif game.IS_GAME_OVER:
            game.display_game_over_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    RUNNING = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    MOUSE_POS_X = pygame.mouse.get_pos()[0]
                    MOUSE_POS_Y = pygame.mouse.get_pos()[1]
                    if MOUSE_POS_X >= 298 and MOUSE_POS_X <= 407 and MOUSE_POS_Y >= 594 and MOUSE_POS_Y <= 639:
                        RUNNING = False
                    elif MOUSE_POS_X >= 226 and MOUSE_POS_X <= 477 and MOUSE_POS_Y >= 532 and MOUSE_POS_Y <= 580:
                        SCREEN.fill(COLORS['screen_color'])
                        game.IS_GETTING_READY = True
                        game.GETTING_READY_START = 0
        elif game.is_expired_game_timer():
            game.EXIT_FLAG = True
            game.update_high_score()
            game.evaluate_additional_running_time()
            game.display_game_over_screen()
        else:
            game.display_pause_option()
            game.display_game_timer()
            game.check_expired_boost_timers()
            game.evaluate_expired_combo_time()
            game.display_boost_timers()
            game.assign_tiles()
            game.IS_GAME_BEGINNING = False
            game.render_playing_tiles
            ()
            game.display_score()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.EXIT_FLAG = True
                    RUNNING = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    MOUSE_POS_X = pygame.mouse.get_pos()[0]
                    MOUSE_POS_Y = pygame.mouse.get_pos()[1]
                    MOUSE_ROW = int((MOUSE_POS_Y - game.BOARD_ORIGIN_Y) // game.GRID_GAP_DIMENSION)
                    MOUSE_COLUMN = int((MOUSE_POS_X - game.BOARD_ORIGIN_X) // game.GRID_GAP_DIMENSION)
                    try:
                        if game.GRIDLINE_BOUNDARIES['xmax'][MOUSE_COLUMN + 1] > MOUSE_POS_X > game.GRIDLINE_BOUNDARIES['xmax'][MOUSE_COLUMN] and game.GRIDLINE_BOUNDARIES['xmin'][MOUSE_COLUMN + 1] > MOUSE_POS_X > game.GRIDLINE_BOUNDARIES['xmin'][MOUSE_COLUMN] and game.GRIDLINE_BOUNDARIES['ymax'][MOUSE_ROW + 1] > MOUSE_POS_Y > game.GRIDLINE_BOUNDARIES['ymax'][MOUSE_ROW] and game.GRIDLINE_BOUNDARIES['ymin'][MOUSE_ROW + 1] > MOUSE_POS_Y > game.GRIDLINE_BOUNDARIES['ymin'][MOUSE_ROW]:
                            if game.ACTIVE_TILE_1 is None and game.CELL_CONTENT[MOUSE_ROW][MOUSE_COLUMN].LOADED:
                                game.ACTIVE_TILE_1 = game.CELL_CONTENT[MOUSE_ROW][MOUSE_COLUMN]
                                game.ACTIVE_TILE_1_INDEX.extend([MOUSE_ROW, MOUSE_COLUMN])
                                game.highlight_active_tile()
                            elif game.ACTIVE_TILE_2 is None and game.CELL_CONTENT[MOUSE_ROW][MOUSE_COLUMN].LOADED:
                                game.ACTIVE_TILE_2 = game.CELL_CONTENT[MOUSE_ROW][MOUSE_COLUMN]
                                game.ACTIVE_TILE_2_INDEX.extend([MOUSE_ROW, MOUSE_COLUMN])
                                game.highlight_active_tile(Tile_2=True)
                                if game.check_equal_tiles() and not game.ACTIVE_TILE_1_INDEX == game.ACTIVE_TILE_2_INDEX:
                                    game.COMBO_TIME_END = time.time()
                                    game.count_combos()
                                    game.COMBO_TIME_START = time.time()
                                    pygame.time.delay(40)
                                    game.combine_tiles()
                                    game.refresh_active_tiles()
                                elif game.check_equal_tiles() and game.ACTIVE_TILE_1_INDEX == game.ACTIVE_TILE_2_INDEX:
                                    pygame.time.delay(40)
                                    game.refresh_active_tiles()
                                else:
                                    game.hide_combo_count()
                                    game.COMBO_TIME_START = 0.0
                                    pygame.time.delay(40)
                                    game.refresh_active_tiles()
                            else:
                                pass
                    except IndexError:
                        pass
        pygame.display.update()
            
    pygame.quit()
    sys.exit()

# Issues I need to look into:
# 1. Tiles are a pixel off the board gridlines. Look into drawing Rectangles and Lines
# 2. Similar to the first issue, polygons are a pixel off the Rectangular Tiles.
# 3. Loading tile must be in front of highlighted til refill
# 4. Color gradient background