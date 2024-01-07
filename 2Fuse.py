import pygame, sys, time
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
            'best_score_color':(255,235,50)}
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    SCREEN.fill(COLORS['screen_color'])

    game = Game(SCREEN_WIDTH,SCREEN_HEIGHT,COLORS,SCREEN)
    game.display_gameboard()
    RUNNING = True
    while RUNNING:
        game.display_score()
        game.display_time()
        game.assign_tiles()
        game.GAME_BEGINNING = False
        game.render_tiles()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.EXIT_FLAG = True
                RUNNING = False
            if event.type == pygame.MOUSEBUTTONDOWN:
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
# 3. Loading tile must be in front of highlighted till refill
# 4. Color gradient background