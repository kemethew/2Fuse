import pygame, random, math, threading, time
from concurrent.futures import ProcessPoolExecutor
pygame.init()

class Tile:
    def __init__(self, RANK, COLOR, LOADED = False, LOADING = False):
        self.RANK = RANK
        self.COLOR = COLOR
        self.LOADED = LOADED
        self.LOADING = LOADING
    
    def __eq__(self, other):
        return self.RANK == other.RANK and self.COLOR == other.COLOR
    
    def __hash__(self):
        return hash([self.RANK, self.COLOR])

class Game:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, SCREEN):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.COLORS = COLORS
        self.SCREEN = SCREEN
        self.GAME_START_TIME = 0
        self.GAME_TIME_REMAINING = 1
        self.GAME_ADDITIONAL_RUNNING_TIME = ""
        self.GAME_CURRENT_TIME_STAMP = 0
        self.GAME_PREVIOUS_TIME_STAMP = 0
        self.EXIT_FLAG = False
        self.IS_GAME_BEGINNING = True
        self.IS_GAME_OVER = False
        self.BOARD_DIMENSION = 560
        self.BOARD_ORIGIN_X = self.SCREEN_WIDTH/2 - self.BOARD_DIMENSION/2
        self.BOARD_ORIGIN_Y = self.SCREEN_HEIGHT - 30 - self.BOARD_DIMENSION
        self.BLOCKS_PER_LINE = 4
        self.GRIDLINE_WIDTH = 3
        self.GRID_GAP_DIMENSION = self.BOARD_DIMENSION/self.BLOCKS_PER_LINE
        self.GRIDLINE_BOUNDARIES = {
            'xmax':[],'xmin':[],
            'ymax':[],'ymin':[]
            }
        for i in range(self.BLOCKS_PER_LINE + 1):
            XMAX = self.BOARD_ORIGIN_X + self.GRIDLINE_WIDTH/2 + self.GRID_GAP_DIMENSION * i
            XMIN = XMAX - self.GRIDLINE_WIDTH
            YMAX = self.BOARD_ORIGIN_Y + self.GRIDLINE_WIDTH/2 + self.GRID_GAP_DIMENSION * i
            YMIN = YMAX - self.GRIDLINE_WIDTH
            self.GRIDLINE_BOUNDARIES['xmax'].append(XMAX)
            self.GRIDLINE_BOUNDARIES['xmin'].append(XMIN)
            self.GRIDLINE_BOUNDARIES['ymax'].append(YMAX)
            self.GRIDLINE_BOUNDARIES['ymin'].append(YMIN)
        self.CELL_CONTENT = [[None for _ in range(self.BLOCKS_PER_LINE)] for _ in range(self.BLOCKS_PER_LINE)]
        self.GAME_TILES = []
        self.TILE_COLORS = [
            self.COLORS['red_tile'],
            self.COLORS['green_tile'],
            self.COLORS['blue_tile']
            ]
        self.TILE_RANKS = [
            {'rank': 1,'value': 1},
            {'rank': 2, 'value': 2},
            {'rank': 'star', 'value': 4}
                     ]
        for color in self.TILE_COLORS:
            for rank in self.TILE_RANKS:
                self.GAME_TILES.append(Tile(rank,color))
        self.ACTIVE_TILE_1 = None
        self.ACTIVE_TILE_2 = None
        self.ACTIVE_TILE_1_INDEX = []
        self.ACTIVE_TILE_2_INDEX = []
        self.SCORE = 0
        self.COMBO_TIME_START = 0.0
        self.COMBO_TIME_END = 0.0
        self.COMBO_COUNT = 1
        self.HIGHEST_COMBO_COUNT = 0
        self.BOOST_IS_ACTIVE = {'RED': False, 'GREEN': False, 'BLUE': False}
        self.BOOST_START_TIME = {'RED': 0, 'GREEN': 0, 'BLUE': 0}
        self.BOOST_TIME_REMAINING = {'RED': 7, 'GREEN': 7, 'BLUE': 7}
        self.BOOST_RUNNING_TIME = {'RED': 0, 'GREEN': 0, 'BLUE': 0}
        
    def display_gameboard(self):
        BOARD_RECT = pygame.Rect(self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y, self.BOARD_DIMENSION + 1, self.BOARD_DIMENSION + 1)
        pygame.draw.rect(self.SCREEN, self.COLORS['gridline_color'], BOARD_RECT, self.GRIDLINE_WIDTH, 12)
        for i in range(3):
            pygame.draw.line(self.SCREEN, self.COLORS['gridline_color'], 
                             (self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * (1 + i)),
                             (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION, self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * (1 + i)),
                             self.GRIDLINE_WIDTH)
            pygame.draw.line(self.SCREEN, self.COLORS['gridline_color'], 
                             (self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * (1 + i), self.BOARD_ORIGIN_Y),
                             (self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * (1 + i), self.BOARD_ORIGIN_Y + self.BOARD_DIMENSION),
                             self.GRIDLINE_WIDTH)
        pygame.display.update(BOARD_RECT)

    def refresh_active_tiles(self):
        CELL_1_CENTER_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * (self.ACTIVE_TILE_1_INDEX[1] + 0.5)
        CELL_1_CENTER_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * (self.ACTIVE_TILE_1_INDEX[0] + 0.5)
        CELL_1_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_1_INDEX[1]
        CELL_1_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_1_INDEX[0]
        CELL_RECT_1 = pygame.Rect(CELL_1_ORIGIN_X, CELL_1_ORIGIN_Y, self.GRID_GAP_DIMENSION + 2, self.GRID_GAP_DIMENSION + 2)
        CELL_2_CENTER_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * (self.ACTIVE_TILE_2_INDEX[1] + 0.5)
        CELL_2_CENTER_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * (self.ACTIVE_TILE_2_INDEX[0] + 0.5)
        CELL_2_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_2_INDEX[1]
        CELL_2_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_2_INDEX[0]
        CELL_RECT_2 = pygame.Rect(CELL_2_ORIGIN_X, CELL_2_ORIGIN_Y, self.GRID_GAP_DIMENSION + 2, self.GRID_GAP_DIMENSION + 2)
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], CELL_RECT_1)
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], CELL_RECT_2)
        pygame.draw.circle(self.SCREEN, self.COLORS['screen_color'], [CELL_1_CENTER_X,CELL_1_CENTER_Y], self.GRID_GAP_DIMENSION/1.68 , 15)
        pygame.draw.circle(self.SCREEN, self.COLORS['screen_color'], [CELL_2_CENTER_X,CELL_2_CENTER_Y], self.GRID_GAP_DIMENSION/1.68 , 15)
        pygame.display.update(pygame.Rect(CELL_1_ORIGIN_X - 10, CELL_1_ORIGIN_Y - 10, self.GRID_GAP_DIMENSION + 20, self.GRID_GAP_DIMENSION + 20))
        pygame.display.update(pygame.Rect(CELL_2_ORIGIN_X - 10, CELL_2_ORIGIN_Y - 10, self.GRID_GAP_DIMENSION + 20, self.GRID_GAP_DIMENSION + 20))
        self.display_gameboard()
        self.ACTIVE_TILE_1 = None
        self.ACTIVE_TILE_2 = None
        self.ACTIVE_TILE_1_INDEX = []
        self.ACTIVE_TILE_2_INDEX = []

    def assign_tiles(self):
        if self.IS_GAME_BEGINNING or self.BOOST_IS_ACTIVE['GREEN']: 
            for i in range(self.BLOCKS_PER_LINE):
                for j in range(self.BLOCKS_PER_LINE):
                    if self.CELL_CONTENT[i][j] is None:
                        self.CELL_CONTENT[i][j] = Tile(self.TILE_RANKS[0],random.choice(self.TILE_COLORS), LOADED = True)
                    else:
                        continue
        else:
            for i in range(self.BLOCKS_PER_LINE):
                for j in range(self.BLOCKS_PER_LINE):
                    if self.CELL_CONTENT[i][j] is None:
                        self.CELL_CONTENT[i][j] = Tile(self.TILE_RANKS[0],random.choice(self.TILE_COLORS))
                    else:
                        continue

    def render_loading_tile(self, CELL_ROW, CELL_COLUMN):
        REMAINING_PIXELS_PER_SIDE = 57
        RENDER_TIME = 3.4
        INITIAL_VELOCITY_RATE_OF_RENDER = REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME
        DECELERATION_RATE_OF_RENDER = -REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME ** 2

        for PIXEL_NUMBER in range(REMAINING_PIXELS_PER_SIDE):
            if self.BOOST_IS_ACTIVE['GREEN']:
                self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADING = False
                self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADED = True
            elif not self.EXIT_FLAG:
                if PIXEL_NUMBER == 0:
                    WAIT_TIME = 0
                elif PIXEL_NUMBER == REMAINING_PIXELS_PER_SIDE:
                    WAIT_TIME = 2/(INITIAL_VELOCITY_RATE_OF_RENDER + 0)
                else:
                    LOADING_TILE_VELOCITY = math.sqrt(INITIAL_VELOCITY_RATE_OF_RENDER ** 2 + 2 * DECELERATION_RATE_OF_RENDER * 1)
                    WAIT_TIME = 2/(INITIAL_VELOCITY_RATE_OF_RENDER + LOADING_TILE_VELOCITY)
                    INITIAL_VELOCITY_RATE_OF_RENDER = LOADING_TILE_VELOCITY

                LOADING_TILE_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * CELL_COLUMN + self.GRIDLINE_WIDTH/2 + 6 + 1 + (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER)
                LOADING_TILE_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * CELL_ROW + self.GRIDLINE_WIDTH/2 + 6 + 1 + (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER)
                LOADING_TILE_DIMENSION = self.GRID_GAP_DIMENSION - self.GRIDLINE_WIDTH - 12 - (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER) * 2
                PIXEL_NUMBER += 1
                LOADING_TILE = pygame.Rect(LOADING_TILE_ORIGIN_X, LOADING_TILE_ORIGIN_Y, LOADING_TILE_DIMENSION, LOADING_TILE_DIMENSION)
                pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], LOADING_TILE, 0, 12)
                pygame.draw.rect(self.SCREEN, self.COLORS['tile_border'], LOADING_TILE, 3, 12)
                pygame.display.update(LOADING_TILE)
                pygame.time.delay(int(WAIT_TIME*1000))
            else:
                break
        
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], LOADING_TILE)
        pygame.display.update(LOADING_TILE)
        REMAINING_PIXELS_PER_SIDE = 6
        RENDER_TIME = 0.13
        INITIAL_VELOCITY_RATE_OF_RENDER = REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME
        DECELERATION_RATE_OF_RENDER = -REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME ** 2

        for PIXEL_NUMBER in range(REMAINING_PIXELS_PER_SIDE):
            if self.BOOST_IS_ACTIVE['GREEN']:
                self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADING = False
                self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADED = True
            elif not self.EXIT_FLAG:
                if PIXEL_NUMBER == 0:
                    WAIT_TIME = 0
                elif PIXEL_NUMBER == REMAINING_PIXELS_PER_SIDE:
                    WAIT_TIME = 2/(INITIAL_VELOCITY_RATE_OF_RENDER + 0)
                else:
                    LOADING_TILE_VELOCITY = math.sqrt(INITIAL_VELOCITY_RATE_OF_RENDER ** 2 + 2 *DECELERATION_RATE_OF_RENDER * 1)
                    WAIT_TIME = 2/(INITIAL_VELOCITY_RATE_OF_RENDER + LOADING_TILE_VELOCITY)
                    INITIAL_VELOCITY_RATE_OF_RENDER = LOADING_TILE_VELOCITY

                LOADING_TILE_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * CELL_COLUMN + self.GRIDLINE_WIDTH/2 + 6 + 1 + (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER)
                LOADING_TILE_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * CELL_ROW + self.GRIDLINE_WIDTH/2 + 6 + 1 + (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER)
                LOADING_TILE_DIMENSION = self.GRID_GAP_DIMENSION - self.GRIDLINE_WIDTH - 12 - (REMAINING_PIXELS_PER_SIDE - PIXEL_NUMBER) * 2
                PIXEL_NUMBER += 1
                LOADING_TILE = pygame.Rect(LOADING_TILE_ORIGIN_X, LOADING_TILE_ORIGIN_Y, LOADING_TILE_DIMENSION, LOADING_TILE_DIMENSION)
                pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], LOADING_TILE, 0, 12)
                pygame.draw.rect(self.SCREEN, self.COLORS['tile_border'], LOADING_TILE, 3, 12)
                pygame.display.update(LOADING_TILE)
                pygame.time.delay(int(WAIT_TIME*1000))
            else:
                break

        if not self.EXIT_FLAG:
            self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADING = False
            self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].LOADED = True
        else:
            pass
    
    def render_loaded_tile(self, CELL_ROW, CELL_COLUMN):
        TILE_DIMENSION = self.GRID_GAP_DIMENSION - self.GRIDLINE_WIDTH - 12
        TILE_RANK = self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].RANK
        TILE_COLOR = self.CELL_CONTENT[CELL_ROW][CELL_COLUMN].COLOR
        TILE_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * CELL_COLUMN + self.GRIDLINE_WIDTH/2 + 6 + 1
        TILE_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * CELL_ROW + self.GRIDLINE_WIDTH/2 + 6 + 1
        TILE_CENTER_X = TILE_ORIGIN_X + TILE_DIMENSION/2 + 1
        TILE_CENTER_Y = TILE_ORIGIN_Y + TILE_DIMENSION/2 + 2
        SHAPE_BORDER_COLOR = []
        if TILE_COLOR == self.COLORS['red_tile']:
            SHAPE_BORDER_COLOR.extend(self.COLORS['red_shape_border'])
        elif TILE_COLOR == self.COLORS['blue_tile']:
            SHAPE_BORDER_COLOR.extend(self.COLORS['blue_shape_border'])
        else:
            SHAPE_BORDER_COLOR.extend(self.COLORS['green_shape_border'])
        TILE = pygame.Rect(TILE_ORIGIN_X, TILE_ORIGIN_Y, TILE_DIMENSION, TILE_DIMENSION)
        SHAPE_ONE_POINTS = [[TILE_ORIGIN_X + 0.3*TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.615*TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.615*TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.39*TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.39*TILE_DIMENSION,TILE_ORIGIN_Y + 0.37*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.3*TILE_DIMENSION,TILE_ORIGIN_Y + 0.37*TILE_DIMENSION],
                            ]
        SHAPE_TWO_POINTS = [[TILE_ORIGIN_X + 0.2*TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*TILE_DIMENSION,TILE_ORIGIN_Y + 0.5875*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.375*TILE_DIMENSION,TILE_ORIGIN_Y + 0.5875*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.375*TILE_DIMENSION,TILE_ORIGIN_Y + 0.625*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*TILE_DIMENSION,TILE_ORIGIN_Y + 0.625*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*TILE_DIMENSION,TILE_ORIGIN_Y + 0.4125*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.625*TILE_DIMENSION,TILE_ORIGIN_Y + 0.4125*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.625*TILE_DIMENSION,TILE_ORIGIN_Y + 0.375*TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*TILE_DIMENSION,TILE_ORIGIN_Y + 0.375*TILE_DIMENSION],
                            ]
        SHAPE_STAR_POINTS = []
        a, b, c, n = 0.81, 0.1, 1, 5
        SCALE = TILE_DIMENSION * 0.12
        SHAPE_STAR_RADIANS = [0.3, 0.95, 1.55, 2.2, 2.8, 3.45, 4.1, 4.7, 5.35, 6]
        for phi in SHAPE_STAR_RADIANS:
            x_max = math.sqrt(-1/b**2 * math.log(2*math.e**(-a**2) - 1))
            r0 = 0.1 * x_max
            r = r0 + 1/c * math.sqrt(-math.log(2*math.e**(-a**2) - math.e**(-b**2 * x_max**2 * math.sin((phi-3*math.pi/2) * n/2)**2)))
            SHAPE_STAR_POINTS.append([TILE_CENTER_X + r*SCALE*math.cos(phi), TILE_CENTER_Y + r*SCALE*math.sin(phi)])
        pygame.draw.rect(self.SCREEN, TILE_COLOR, TILE, border_radius = 12)
        pygame.draw.rect(self.SCREEN, self.COLORS['tile_border'], TILE, 4, border_radius = 12)
        if TILE_RANK['rank'] == 1:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_number_color'], SHAPE_ONE_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_ONE_POINTS, 3)
        elif TILE_RANK['rank'] == 2:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_number_color'], SHAPE_TWO_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_TWO_POINTS, 3)
        else:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_star_color'], SHAPE_STAR_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_STAR_POINTS,3)

        pygame.display.update(TILE)

    def render_tiles(self):
        for i in range(self.BLOCKS_PER_LINE):
            for j in range(self.BLOCKS_PER_LINE):
                if self.CELL_CONTENT[i][j].LOADING or [i,j] == self.ACTIVE_TILE_1_INDEX or [i,j] == self.ACTIVE_TILE_2_INDEX:
                    continue
                elif self.CELL_CONTENT[i][j].LOADED:
                    self.render_loaded_tile(i,j)
                else:
                    self.CELL_CONTENT[i][j].LOADING = True
                    thread = threading.Thread(target = self.render_loading_tile, args = (i,j), daemon = True)
                    thread.start()

    def highlight_active_tile(self, Tile_2 = False):
        HIGHLIGHTED_TILE_DIMENSION = self.GRID_GAP_DIMENSION
        if Tile_2 == False:
            TILE_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_1_INDEX[1] - self.GRIDLINE_WIDTH/2 + 3
            TILE_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_1_INDEX[0] + self.GRIDLINE_WIDTH/2 + 1
            TILE_CENTER_X = TILE_ORIGIN_X + HIGHLIGHTED_TILE_DIMENSION/2
            TILE_CENTER_Y = TILE_ORIGIN_Y + HIGHLIGHTED_TILE_DIMENSION/2
            TILE_ROW = self.ACTIVE_TILE_1_INDEX[0]
            TILE_COLUMN = self.ACTIVE_TILE_1_INDEX[1]
            TILE_COLOR = self.CELL_CONTENT[TILE_ROW][TILE_COLUMN].COLOR
            TILE_RANK = self.CELL_CONTENT[TILE_ROW][TILE_COLUMN].RANK
            SHAPE_BORDER_COLOR = []
            if TILE_COLOR == self.COLORS['red_tile']:
                SHAPE_BORDER_COLOR.extend(self.COLORS['red_shape_border'])
            elif TILE_COLOR == self.COLORS['blue_tile']:
                SHAPE_BORDER_COLOR.extend(self.COLORS['blue_shape_border'])
            else:
                SHAPE_BORDER_COLOR.extend(self.COLORS['green_shape_border'])
        else:
            TILE_ORIGIN_X = self.BOARD_ORIGIN_X + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_2_INDEX[1] - self.GRIDLINE_WIDTH/2 + 3
            TILE_ORIGIN_Y = self.BOARD_ORIGIN_Y + self.GRID_GAP_DIMENSION * self.ACTIVE_TILE_2_INDEX[0] + self.GRIDLINE_WIDTH/2 + 1
            TILE_CENTER_X = TILE_ORIGIN_X + HIGHLIGHTED_TILE_DIMENSION/2
            TILE_CENTER_Y = TILE_ORIGIN_Y + HIGHLIGHTED_TILE_DIMENSION/2
            TILE_ROW = self.ACTIVE_TILE_2_INDEX[0]
            TILE_COLUMN = self.ACTIVE_TILE_2_INDEX[1]
            TILE_COLOR = self.CELL_CONTENT[TILE_ROW][TILE_COLUMN].COLOR
            TILE_RANK = self.CELL_CONTENT[TILE_ROW][TILE_COLUMN].RANK
            SHAPE_BORDER_COLOR = []
            if TILE_COLOR == self.COLORS['red_tile']:
                SHAPE_BORDER_COLOR.extend(self.COLORS['red_shape_border'])
            elif TILE_COLOR == self.COLORS['blue_tile']:
                SHAPE_BORDER_COLOR.extend(self.COLORS['blue_shape_border'])
            else:
                SHAPE_BORDER_COLOR.extend(self.COLORS['green_shape_border'])

        TILE = pygame.Rect(TILE_ORIGIN_X, TILE_ORIGIN_Y, HIGHLIGHTED_TILE_DIMENSION, HIGHLIGHTED_TILE_DIMENSION)
        SHAPE_ONE_POINTS = [[TILE_ORIGIN_X + 0.3*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.615*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.615*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.39*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.39*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.37*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.3*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.37*HIGHLIGHTED_TILE_DIMENSION],
                            ]
        SHAPE_TWO_POINTS = [[TILE_ORIGIN_X + 0.2*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.2*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.5875*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.375*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.5875*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.375*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.625*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.625*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.8*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.8*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.4125*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.625*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.4125*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.625*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.375*HIGHLIGHTED_TILE_DIMENSION],
                            [TILE_ORIGIN_X + 0.2*HIGHLIGHTED_TILE_DIMENSION,TILE_ORIGIN_Y + 0.375*HIGHLIGHTED_TILE_DIMENSION],
                            ]
        SHAPE_STAR_POINTS = []
        a, b, c, n = 0.81, 0.1, 1, 5
        SCALE = HIGHLIGHTED_TILE_DIMENSION * 0.12
        SHAPE_STAR_RADIANS = [0.3, 0.95, 1.55, 2.2, 2.8, 3.45, 4.1, 4.7, 5.35, 6]
        for phi in SHAPE_STAR_RADIANS:
            x_max = math.sqrt(-1/b**2 * math.log(2*math.e**(-a**2) - 1))
            r0 = 0.1 * x_max
            r = r0 + 1/c * math.sqrt(-math.log(2*math.e**(-a**2) - math.e**(-b**2 * x_max**2 * math.sin((phi-3*math.pi/2) * n/2)**2)))
            SHAPE_STAR_POINTS.append([TILE_CENTER_X + r*SCALE*math.cos(phi), TILE_CENTER_Y + r*SCALE*math.sin(phi)])
        
        pygame.draw.rect(self.SCREEN, TILE_COLOR, TILE, border_radius = 12)
        pygame.draw.rect(self.SCREEN, self.COLORS['tile_border'], TILE, 4, border_radius = 12)
        if TILE_RANK['rank'] == 1:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_number_color'], SHAPE_ONE_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_ONE_POINTS, 3)
        elif TILE_RANK['rank'] == 2:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_number_color'], SHAPE_TWO_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_TWO_POINTS, 3)
        else:
            pygame.draw.polygon(self.SCREEN, self.COLORS['shape_star_color'], SHAPE_STAR_POINTS)
            pygame.draw.polygon(self.SCREEN, SHAPE_BORDER_COLOR, SHAPE_STAR_POINTS,3)
            # pygame.draw.aalines(self.SCREEN, SHAPE_BORDER_COLOR, True, SHAPE_STAR_POINTS, 3)
        
        pygame.draw.circle(self.SCREEN, self.COLORS['active_tile_highlight'], [TILE_CENTER_X,TILE_CENTER_Y], self.GRID_GAP_DIMENSION/1.85 , 5)
        pygame.draw.circle(self.SCREEN, self.COLORS['active_tile_halo'], [TILE_CENTER_X,TILE_CENTER_Y], self.GRID_GAP_DIMENSION/2.05 , 4)
        pygame.draw.circle(self.SCREEN, self.COLORS['active_tile_halo'], [TILE_CENTER_X,TILE_CENTER_Y], self.GRID_GAP_DIMENSION/1.75 , 4)
        pygame.display.update(pygame.Rect(TILE_ORIGIN_X - 10, TILE_ORIGIN_Y - 10, HIGHLIGHTED_TILE_DIMENSION + 20, HIGHLIGHTED_TILE_DIMENSION + 20))

    def check_equal_tiles(self):
        if self.ACTIVE_TILE_2.RANK == self.ACTIVE_TILE_1.RANK and self.ACTIVE_TILE_2.COLOR == self.ACTIVE_TILE_1.COLOR:
            return True
        else:
            return False

    def combine_tiles(self):
        ACT_T1_CONT = self.ACTIVE_TILE_1
        ACT_T2_CONT = self.ACTIVE_TILE_2
        ACT_T1_IND = self.ACTIVE_TILE_1_INDEX
        ACT_T2_IND = self.ACTIVE_TILE_2_INDEX
        SUM_VALUE = ACT_T1_CONT.RANK['value'] + ACT_T2_CONT.RANK['value']
        if SUM_VALUE == 2:
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]] = Tile(self.TILE_RANKS[1], ACT_T2_CONT.COLOR)
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].LOADED = True
            self.CELL_CONTENT[ACT_T1_IND[0]][ACT_T1_IND[1]] = None
        elif SUM_VALUE == 4:
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]] = Tile(self.TILE_RANKS[2], ACT_T2_CONT.COLOR)
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].LOADED = True
            self.CELL_CONTENT[ACT_T1_IND[0]][ACT_T1_IND[1]] = None
        else:
            if self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].COLOR == self.COLORS['red_tile']:
                self.activate_boost('RED')
            elif self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].COLOR == self.COLORS['green_tile']:
                self.activate_boost('GREEN')
            elif self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].COLOR == self.COLORS['blue_tile']:
                self.activate_boost('BLUE')
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]] = None
            self.CELL_CONTENT[ACT_T1_IND[0]][ACT_T1_IND[1]] = None
        self.add_score()

    def check_expired_boost_timers(self):
        ELAPSED_TIME_THIS_LOOP = self.GAME_CURRENT_TIME_STAMP - self.GAME_PREVIOUS_TIME_STAMP
        if self.BOOST_TIME_REMAINING['RED'] <= 0 and self.BOOST_IS_ACTIVE['RED']:
            self.BOOST_IS_ACTIVE['RED'] = False
            self.BOOST_TIME_REMAINING['RED'] = 7
        elif self.BOOST_TIME_REMAINING['RED'] > 0 and self.BOOST_IS_ACTIVE['RED']:
            self.BOOST_TIME_REMAINING['RED'] -= ELAPSED_TIME_THIS_LOOP
        else:
            pass

        if self.BOOST_TIME_REMAINING['GREEN'] <= 0 and self.BOOST_IS_ACTIVE['GREEN']:
            self.BOOST_IS_ACTIVE['GREEN'] = False
            self.BOOST_TIME_REMAINING['GREEN'] = 7
        elif self.BOOST_TIME_REMAINING['GREEN'] > 0 and self.BOOST_IS_ACTIVE['GREEN']:
            self.BOOST_TIME_REMAINING['GREEN'] -= ELAPSED_TIME_THIS_LOOP
        else:
            pass

        if self.BOOST_TIME_REMAINING['BLUE'] <= 0 and self.BOOST_IS_ACTIVE['BLUE']:
            self.BOOST_IS_ACTIVE['BLUE'] = False
            self.BOOST_TIME_REMAINING['BLUE'] = 7
        elif self.BOOST_TIME_REMAINING['BLUE'] > 0 and self.BOOST_IS_ACTIVE['BLUE']:
            self.BOOST_TIME_REMAINING['BLUE'] -= ELAPSED_TIME_THIS_LOOP
        else:
            pass

    def activate_boost(self, COLOR):
        if COLOR == 'RED':
            if not self.BOOST_IS_ACTIVE['RED']:
                self.BOOST_IS_ACTIVE['RED'] = True
            else:
                if self.BOOST_TIME_REMAINING['RED'] >= 6:
                    self.BOOST_TIME_REMAINING['RED'] = 7
                else:
                    self.BOOST_TIME_REMAINING['RED'] += 1
        elif COLOR == 'GREEN':
            if not self.BOOST_IS_ACTIVE['GREEN']:
                self.BOOST_IS_ACTIVE['GREEN'] = True
            else:
                if self.BOOST_TIME_REMAINING['GREEN'] >= 6:
                    self.BOOST_TIME_REMAINING['GREEN'] = 7
                else:
                    self.BOOST_TIME_REMAINING['GREEN'] += 1
        else:
            if not self.BOOST_IS_ACTIVE['BLUE']:
                self.BOOST_IS_ACTIVE['BLUE'] = True
            else:
                if self.BOOST_TIME_REMAINING['BLUE'] >= 6:
                    self.BOOST_TIME_REMAINING['BLUE'] = 7
                else:
                    self.BOOST_TIME_REMAINING['BLUE'] += 1

    def count_combos(self):
        COMBO_TIME = self.COMBO_TIME_END - self.COMBO_TIME_START
        if COMBO_TIME <= 1.7:
            self.COMBO_COUNT += 1
            if self.SCORE > 0 and self.HIGHEST_COMBO_COUNT < self.COMBO_COUNT:
                self.HIGHEST_COMBO_COUNT = self.COMBO_COUNT
        else:
            self.COMBO_COUNT = 1

        if self.COMBO_COUNT > 4:
            self.display_combo_count()

    def display_combo_count(self):
        COMBO_TITLE_FONT_SIZE = 31
        COMBO_TITLE_FONT = pygame.font.Font("BebasNeue-Regular.otf", COMBO_TITLE_FONT_SIZE)
        COMBO_TITLE_IMG = COMBO_TITLE_FONT.render('COMBO', False, self.COLORS['score_color'])
        COMBO_COUNT_FONT_SIZE = 46
        COMBO_COUNT_FONT = pygame.font.Font("BebasNeue-Regular.otf", COMBO_COUNT_FONT_SIZE)
        COMBO_COUNT_IMG = COMBO_COUNT_FONT.render(str(self.COMBO_COUNT), False, self.COLORS['color_white'])
        COMBO_COUNT_ORIGIN_X = 0
        if self.COMBO_COUNT < 9:
            COMBO_COUNT_ORIGIN_X =  self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 11
        else:
            COMBO_COUNT_ORIGIN_X =  self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 18
        COMBO_BACKGROUND_REFILL_TILE = pygame.Rect(self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 32, self.BOARD_ORIGIN_Y - COMBO_COUNT_FONT_SIZE - 48 - COMBO_TITLE_FONT_SIZE, 64, 80)

        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], COMBO_BACKGROUND_REFILL_TILE)
        self.SCREEN.blit(COMBO_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 32, self.BOARD_ORIGIN_Y - COMBO_COUNT_FONT_SIZE - 48 - COMBO_TITLE_FONT_SIZE))
        self.SCREEN.blit(COMBO_COUNT_IMG, (COMBO_COUNT_ORIGIN_X, self.BOARD_ORIGIN_Y - COMBO_COUNT_FONT_SIZE - 58))
        pygame.display.update(COMBO_BACKGROUND_REFILL_TILE)

    def add_score(self):
        COMBINED_TILE_VALUE = 0
        ADDITIONAL_COMBO_SCORE = 0

        if self.ACTIVE_TILE_2.RANK['value'] == 1:
            COMBINED_TILE_VALUE = 50
        elif  self.ACTIVE_TILE_2.RANK['value'] == 2:
            COMBINED_TILE_VALUE = 150
        else:
            COMBINED_TILE_VALUE = 500
        
        if self.COMBO_COUNT > 60:
            ADDITIONAL_COMBO_SCORE =  (self.COMBO_COUNT - 61) // 10 * 500 + 1500
        elif self.COMBO_COUNT > 40:
            ADDITIONAL_COMBO_SCORE = 1000
        elif self.COMBO_COUNT > 30:
            ADDITIONAL_COMBO_SCORE = 500
        elif self.COMBO_COUNT > 16:
            ADDITIONAL_COMBO_SCORE = 300
        elif self.COMBO_COUNT > 12:
            ADDITIONAL_COMBO_SCORE = 100
        elif self.COMBO_COUNT > 8:
            ADDITIONAL_COMBO_SCORE = 50
        elif self.COMBO_COUNT > 4:
            ADDITIONAL_COMBO_SCORE = 20
        else:
            ADDITIONAL_COMBO_SCORE = 0
        
        if self.BOOST_IS_ACTIVE['RED']:
            self.SCORE += (COMBINED_TILE_VALUE + ADDITIONAL_COMBO_SCORE) * 2
        else:
            self.SCORE += COMBINED_TILE_VALUE + ADDITIONAL_COMBO_SCORE

    def display_score(self):
        SCORE_SURFACE = pygame.Rect(self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 97, 140, 55)
        FONT = pygame.font.Font("BebasNeue-Regular.otf",50)
        SCORE_STRING = "0" * (7 - len(str(self.SCORE))) + str(self.SCORE)
        SCORE_PREFIX_STRING = "000000"
        SCORE_IMG = FONT.render(SCORE_STRING, False, self.COLORS['score_color'])
        SCORE_PREFIX_IMG = FONT.render(SCORE_PREFIX_STRING[:len(SCORE_PREFIX_STRING) - len(str(self.SCORE)) + 1], False, self.COLORS['score_prefix_color'])
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], SCORE_SURFACE)
        self.SCREEN.blit(SCORE_IMG, (self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 97))
        self.SCREEN.blit(SCORE_PREFIX_IMG, (self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 97))
        pygame.display.update(SCORE_SURFACE)

    def is_expired_game_timer(self):
        self.GAME_PREVIOUS_TIME_STAMP = self.GAME_CURRENT_TIME_STAMP
        self.GAME_CURRENT_TIME_STAMP = time.time()
        ELAPSED_TIME_THIS_LOOP = self.GAME_CURRENT_TIME_STAMP - self.GAME_PREVIOUS_TIME_STAMP
        if self.BOOST_IS_ACTIVE['BLUE']:
            self.GAME_TIME_REMAINING -= ELAPSED_TIME_THIS_LOOP / 2
        else:
            self.GAME_TIME_REMAINING -= ELAPSED_TIME_THIS_LOOP
        if self.GAME_TIME_REMAINING <= 0:
            return True
        else:
            return False

    def display_game_timer(self):
        # ELAPSED_TIME_THIS_LOOP = self.GAME_CURRENT_TIME_STAMP - self.GAME_PREVIOUS_TIME_STAMP
        # if self.BOOST_IS_ACTIVE['BLUE']:
        #     self.GAME_TIME_REMAINING -= ELAPSED_TIME_THIS_LOOP / 2
        # else:
        #     self.GAME_TIME_REMAINING -= ELAPSED_TIME_THIS_LOOP

        SECOND = int(self.GAME_TIME_REMAINING)
        CENTISECOND = int((self.GAME_TIME_REMAINING - SECOND) * 100)
        TIME_SURFACE = pygame.Rect(self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 40, 65, 26)
        FONT = pygame.font.Font("BebasNeue-Regular.otf",34)
        TITLE_IMG = FONT.render(f"{SECOND}:{CENTISECOND}", False, self.COLORS['color_white'])
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], TIME_SURFACE)
        self.SCREEN.blit(TITLE_IMG, (self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 45))
        pygame.display.update(TIME_SURFACE)

        TIMER_FILLER_BAR = pygame.Rect(self.BOARD_ORIGIN_X + 70, self.BOARD_ORIGIN_Y - 32, self.SCREEN_WIDTH - (self.BOARD_ORIGIN_X + 70) - self.BOARD_ORIGIN_X, 12)
        TIMER_BORDER = pygame.Rect(self.BOARD_ORIGIN_X + 70, self.BOARD_ORIGIN_Y - 32, self.SCREEN_WIDTH - (self.BOARD_ORIGIN_X + 70) - self.BOARD_ORIGIN_X, 12)
        RUNNING_TIMER_BAR = pygame.Rect(self.BOARD_ORIGIN_X + 71, self.BOARD_ORIGIN_Y - 29, (self.SCREEN_WIDTH - (self.BOARD_ORIGIN_X + 72) - self.BOARD_ORIGIN_X - 1) * self.GAME_TIME_REMAINING / 60, 6)
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], TIMER_FILLER_BAR)
        pygame.draw.rect(self.SCREEN, self.COLORS['timer_border_color'], TIMER_BORDER, 1)
        if self.BOOST_IS_ACTIVE['BLUE']:
            pygame.draw.rect(self.SCREEN, self.COLORS['boosted_running_timer_color'], RUNNING_TIMER_BAR)
        else:
            pygame.draw.rect(self.SCREEN, self.COLORS['normal_running_timer_color'], RUNNING_TIMER_BAR)
        pygame.display.update(TIMER_FILLER_BAR)
        pygame.display.update(TIMER_BORDER)      
        pygame.display.update(RUNNING_TIMER_BAR)

    def display_boost_timers(self):
        BORDER_WIDTH, BORDER_HEIGHT, FILLER_WIDTH, FILLER_HEIGHT = 35, 45, 33, 44
        RED_TIMER_ORIGIN_X, RED_TIMER_ORIGIN_Y = self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 131, self.BOARD_ORIGIN_Y - 90
        GREEN_TIMER_ORIGIN_X, GREEN_TIMER_ORIGIN_Y = self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 83, self.BOARD_ORIGIN_Y - 90
        BLUE_TIMER_ORIGIN_X, BLUE_TIMER_ORIGIN_Y = self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 35, self.BOARD_ORIGIN_Y - 90

        RED_BOOST_BACKGROUND_REFILL = pygame.Rect(RED_TIMER_ORIGIN_X, RED_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)
        GREEN_BOOST_BACKGROUND_REFILL = pygame.Rect(GREEN_TIMER_ORIGIN_X, GREEN_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)
        BLUE_BOOST_BACKGROUND_REFILL = pygame.Rect(BLUE_TIMER_ORIGIN_X, BLUE_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)

        RED_BOOST_TIMER_BORDER = pygame.Rect(RED_TIMER_ORIGIN_X, RED_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)
        GREEN_BOOST_TIMER_BORDER = pygame.Rect(GREEN_TIMER_ORIGIN_X, GREEN_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)
        BLUE_BOOST_TIMER_BORDER = pygame.Rect(BLUE_TIMER_ORIGIN_X, BLUE_TIMER_ORIGIN_Y, BORDER_WIDTH, BORDER_HEIGHT)

        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], RED_BOOST_BACKGROUND_REFILL)
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], GREEN_BOOST_BACKGROUND_REFILL)
        pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], BLUE_BOOST_BACKGROUND_REFILL)
        pygame.draw.rect(self.SCREEN, self.COLORS['red_shape_border'], RED_BOOST_TIMER_BORDER, 1)
        pygame.draw.rect(self.SCREEN, self.COLORS['green_shape_border'], GREEN_BOOST_TIMER_BORDER, 1)
        pygame.draw.rect(self.SCREEN, self.COLORS['blue_shape_border'], BLUE_BOOST_TIMER_BORDER, 1)
        pygame.display.update(RED_BOOST_BACKGROUND_REFILL)
        pygame.display.update(GREEN_BOOST_BACKGROUND_REFILL)
        pygame.display.update(BLUE_BOOST_BACKGROUND_REFILL)
        pygame.display.update(RED_BOOST_TIMER_BORDER)
        pygame.display.update(GREEN_BOOST_TIMER_BORDER)
        pygame.display.update(BLUE_BOOST_TIMER_BORDER)
        
        if self.BOOST_IS_ACTIVE['RED']:
            RED_BOOST_TIMER_FILLER = pygame.Rect(self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 131 + 1, self.BOARD_ORIGIN_Y - 90 + 1 + FILLER_HEIGHT * (1 - self.BOOST_TIME_REMAINING['RED'] / 7), FILLER_WIDTH, FILLER_HEIGHT * (self.BOOST_TIME_REMAINING['RED'] / 7))
            pygame.draw.rect(self.SCREEN, self.COLORS['red_tile'], RED_BOOST_TIMER_FILLER)
            pygame.display.update(RED_BOOST_TIMER_FILLER)
        if self.BOOST_IS_ACTIVE['GREEN']:
            GREEN_BOOST_TIMER_FILLER = pygame.Rect(self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 83 + 1, self.BOARD_ORIGIN_Y - 90 + 1 + FILLER_HEIGHT * (1 - self.BOOST_TIME_REMAINING['GREEN'] / 7), FILLER_WIDTH, FILLER_HEIGHT * (self.BOOST_TIME_REMAINING['GREEN'] / 7))
            pygame.draw.rect(self.SCREEN, self.COLORS['green_tile'], GREEN_BOOST_TIMER_FILLER)
            pygame.display.update(GREEN_BOOST_TIMER_FILLER)            
        if self.BOOST_IS_ACTIVE['BLUE']:
            BLUE_BOOST_TIMER_FILLER = pygame.Rect(self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 10 - 35 + 1, self.BOARD_ORIGIN_Y - 90 + 1 + FILLER_HEIGHT * (1 - self.BOOST_TIME_REMAINING['BLUE'] / 7), FILLER_WIDTH, FILLER_HEIGHT * (self.BOOST_TIME_REMAINING['BLUE'] / 7))
            pygame.draw.rect(self.SCREEN, self.COLORS['blue_tile'], BLUE_BOOST_TIMER_FILLER)
            pygame.display.update(BLUE_BOOST_TIMER_FILLER)            

    def evaluate_additional_running_time(self):
        ADDITIONAL_RUNNING_TIME = int(time.time() - self.GAME_START_TIME - 60)
        if len(str(ADDITIONAL_RUNNING_TIME)) == 1:
            self.GAME_ADDITIONAL_RUNNING_TIME = f"0{ADDITIONAL_RUNNING_TIME}"
        else:
            self.GAME_ADDITIONAL_RUNNING_TIME = str(ADDITIONAL_RUNNING_TIME)

    def display_game_over_screen(self):
        self.IS_GAME_OVER = True
        self.SCREEN.fill(self.COLORS['screen_color'])

        TITLE_FONT = pygame.font.Font("BebasNeue-Regular.otf", 85)
        MINI_SUBTITLE_FONT = pygame.font.Font("BebasNeue-Regular.otf", 29)
        SUBTITLE_FONT = pygame.font.Font("BebasNeue-Regular.otf", 30)
        CONTENT_VALUE_FONT = pygame.font.Font("BebasNeue-Regular.otf", 30)
        DECISION_FONT = pygame.font.Font("BebasNeue-Regular.otf", 65)
        SUBDECISION_FONT = pygame.font.Font("BebasNeue-Regular.otf", 60)
        SCORE_VALUE_COORDINATE = (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 15 - 17 * (len(str(self.SCORE)) - 1), self.BOARD_ORIGIN_Y + 95)
        PLAY_AGAIN_BUTTON_POINTS = ((self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 115, self.BOARD_ORIGIN_Y + 367), 
                                    (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 115, self.BOARD_ORIGIN_Y + 386), 
                                    (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 135, self.BOARD_ORIGIN_Y + 386), 
                                    (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 115, self.BOARD_ORIGIN_Y + 386), 
                                    (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 135, self.BOARD_ORIGIN_Y + 386), 
                                    (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 115, self.BOARD_ORIGIN_Y + 405)
                                    )
        EXIT_BUTTON_POINTS = ((self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 45, self.BOARD_ORIGIN_Y + 430), 
                              (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 45, self.BOARD_ORIGIN_Y + 448), 
                              (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 65, self.BOARD_ORIGIN_Y + 448), 
                              (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 45, self.BOARD_ORIGIN_Y + 448), 
                              (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 65, self.BOARD_ORIGIN_Y + 448), 
                              (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 45, self.BOARD_ORIGIN_Y + 466)
                              )

        RESULTS_TITLE_IMG = TITLE_FONT.render('RESULTS', False, self.COLORS['game_over_remark_color'])
        SCORE_TITLE_IMG = MINI_SUBTITLE_FONT.render('SCORE', False, self.COLORS['game_over_remark_color'])
        SCORE_VALUE_IMG = TITLE_FONT.render(str(self.SCORE), False, self.COLORS['color_white'])
        HIGHEST_COMBO_TITLE_IMG = SUBTITLE_FONT.render('HIGHEST COMBO -', False, self.COLORS['game_over_remark_color'])
        HIGHEST_COMBO_VALUE_IMG = CONTENT_VALUE_FONT.render(str(self.HIGHEST_COMBO_COUNT), False, self.COLORS['score_color'])
        TIME_PLAYED_TITLE_IMG = SUBTITLE_FONT.render('TIME PLAYED -', False, self.COLORS['game_over_remark_color'])
        TIME_PLAYED_VALUE_IMG = CONTENT_VALUE_FONT.render(f"1:{self.GAME_ADDITIONAL_RUNNING_TIME}", False, self.COLORS['score_color'])
        PLAY_AGAIN_TITLE_IMG = DECISION_FONT.render('PLAY AGAIN', False, self.COLORS['color_white'])
        EXIT_TITLE_IMG = SUBDECISION_FONT.render('EXIT', False, self.COLORS['color_white'])

        self.SCREEN.blit(RESULTS_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 108, self.BOARD_ORIGIN_Y - 60))
        pygame.draw.line(self.SCREEN, self.COLORS['color_white'], (self.BOARD_ORIGIN_X + 80, self.BOARD_ORIGIN_Y + 36), (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 80, self.BOARD_ORIGIN_Y + 36), 2)
        self.SCREEN.blit(SCORE_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 26, self.BOARD_ORIGIN_Y + 63))
        self.SCREEN.blit(SCORE_VALUE_IMG, SCORE_VALUE_COORDINATE)
        self.SCREEN.blit(HIGHEST_COMBO_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 100, self.BOARD_ORIGIN_Y + 225))
        self.SCREEN.blit(HIGHEST_COMBO_VALUE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 63, self.BOARD_ORIGIN_Y + 225))
        self.SCREEN.blit(TIME_PLAYED_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 87, self.BOARD_ORIGIN_Y + 265))
        self.SCREEN.blit(TIME_PLAYED_VALUE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 + 47, self.BOARD_ORIGIN_Y + 265))
        pygame.draw.line(self.SCREEN, self.COLORS['color_white'], (self.BOARD_ORIGIN_X + 80, self.BOARD_ORIGIN_Y + 335), (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION - 80, self.BOARD_ORIGIN_Y + 335), 2)
        self.SCREEN.blit(PLAY_AGAIN_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 115, self.BOARD_ORIGIN_Y + 350))
        pygame.draw.polygon(self.SCREEN, self.COLORS['green_tile'], PLAY_AGAIN_BUTTON_POINTS[0:3])
        pygame.draw.polygon(self.SCREEN, self.COLORS['green_shape_border'], PLAY_AGAIN_BUTTON_POINTS[3:])
        self.SCREEN.blit(EXIT_TITLE_IMG, (self.BOARD_ORIGIN_X + self.BOARD_DIMENSION/2 - 42, self.BOARD_ORIGIN_Y + 414))
        pygame.draw.polygon(self.SCREEN, self.COLORS['red_tile'], EXIT_BUTTON_POINTS[0:3])
        pygame.draw.polygon(self.SCREEN, self.COLORS['red_shape_border'], EXIT_BUTTON_POINTS[3:])

