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
        self.EXIT_FLAG = False
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.COLORS = COLORS
        self.SCREEN = SCREEN
        self.GAME_BEGINNING = True
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
        self.BOOST_IS_ACTIVE = {
            'RED':False, 
            'GREEN':False, 
            'BLUE':False 
            }
        self.BOOST_TIMER_PROCESSOR = {
            'RED':ProcessPoolExecutor(max_workers = 1), 
            'GREEN':ProcessPoolExecutor(max_workers = 1), 
            'BLUE':ProcessPoolExecutor(max_workers = 1)
            }
        # self.RED_BOOST_TIMER_PROCESSOR = ProcessPoolExecutor(max_workers = 1)
        # self.GREEN_BOOST_TIMER_PROCESSOR = ProcessPoolExecutor(max_workers = 1)
        # self.BLUE_BOOST_TIMER_PROCESSOR = ProcessPoolExecutor(max_workers = 1)
        # self.RED_BOOST_TIME_STAMP = {'start': 0, 'end': 0}
        # self.GREEN_BOOST_TIME_STAMP = {'start': 0, 'end': 0}
        # self.BLUE_BOOST_TIME_STAMP = {'start': 0, 'end': 0}
        self.BOOST_TIME_PROPERTIES = {
            'RED':{'start': 0, 'end': time.time(), 'elapsed': 0, 'remaining': 7000}, 
            'GREEN':{'start': 0, 'end': time.time(), 'elapsed': 0, 'remaining': 7000}, 
            'BLUE':{'start': 0, 'end': time.time(), 'elapsed': 0, 'remaining': 7000}
            }
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
        if self.GAME_BEGINNING: 
            for i in range(self.BLOCKS_PER_LINE):
                for j in range(self.BLOCKS_PER_LINE):
                    self.CELL_CONTENT[i][j] = Tile(self.TILE_RANKS[0],random.choice(self.TILE_COLORS), LOADED = True)
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
            if not self.EXIT_FLAG:
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
        
        if not self.EXIT_FLAG:
            pygame.draw.rect(self.SCREEN, self.COLORS['screen_color'], LOADING_TILE)
            pygame.display.update(LOADING_TILE)
            REMAINING_PIXELS_PER_SIDE = 6
            RENDER_TIME = 0.13
            INITIAL_VELOCITY_RATE_OF_RENDER = REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME
            DECELERATION_RATE_OF_RENDER = -REMAINING_PIXELS_PER_SIDE * 2 / RENDER_TIME ** 2
        else:
            pass

        for PIXEL_NUMBER in range(REMAINING_PIXELS_PER_SIDE):
            if not self.EXIT_FLAG:
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
            self.render_loaded_tile(CELL_ROW, CELL_COLUMN)
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
                self.activate_boost_countdown_timer('RED')
            elif self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].COLOR == self.COLORS['green_tile']:
                self.activate_boost_countdown_timer('GREEN')
            elif self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]].COLOR == self.COLORS['blue_tile']:
                self.activate_boost_countdown_timer('BLUE')
            self.CELL_CONTENT[ACT_T2_IND[0]][ACT_T2_IND[1]] = None
            self.CELL_CONTENT[ACT_T1_IND[0]][ACT_T1_IND[1]] = None
        self.add_score()

    def boost_countdown_timer(self, MILLISECONDS):
        while MILLISECONDS > 0:
            pygame.time.delay(100)
            MILLISECONDS -= 100

    def activate_boost_countdown_timer(self, COLOR):

        self.BOOST_TIME_PROPERTIES[COLOR]['end'] = time.time()
        self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] = (self.BOOST_TIME_PROPERTIES[COLOR]['end'] - self.BOOST_TIME_PROPERTIES[COLOR]['start']) * 1000


        # test timing of this
        if self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] > self.BOOST_TIME_PROPERTIES[COLOR]['remaining']:
                if self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] - self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] > 300:
                    self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
                    self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] = 7000
                    self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 7000)
                elif self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] - self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] > 200:
                    self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
                    self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] = 7000
                    self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 6900)
                elif self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] - self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] > 100:
                    self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
                    self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] = 7000
                    self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 6800)
                else:
                    self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
                    self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] = 7000
                    self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 6700)
        #update this remaining time to be checked with elapsed time
        elif self.BOOST_TIME_PROPERTIES[COLOR]['elapsed'] < 1000:
            self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
            self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] = 7000
            self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 7000 - round(self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] / 100) * 100 - 300)
        else:
            self.BOOST_TIME_PROPERTIES[COLOR]['start'] = time.time()
            self.BOOST_TIME_PROPERTIES[COLOR]['remaining'] += 1000
            self.BOOST_TIMER_PROCESSOR[COLOR].submit(self.boost_countdown_timer, 700)


    def count_combos(self):
        COMBO_TIME = self.COMBO_TIME_END - self.COMBO_TIME_START
        if COMBO_TIME <= 1.7:
            self.COMBO_COUNT += 1
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
        BOOST_END_TIME_STAMP_REFERENCE = time.time()
        BOOST_ELAPSED_TIME_STAMP_REFERENCE = (BOOST_END_TIME_STAMP_REFERENCE - self.BOOST_TIME_PROPERTIES['RED']['start']) * 1000

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
        

        #debug double scoring upon activation of boost
        if BOOST_ELAPSED_TIME_STAMP_REFERENCE < self.BOOST_TIME_PROPERTIES['RED']['remaining'] + 200:
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

    def display_time(self):
        FONT = pygame.font.Font("BebasNeue-Regular.otf",34)
        TITLE_IMG = FONT.render("60:00", False, self.COLORS['color_white'])
        self.SCREEN.blit(TITLE_IMG, (self.BOARD_ORIGIN_X, self.BOARD_ORIGIN_Y - 45))
        pygame.display.update()