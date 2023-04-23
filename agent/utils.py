from referee.game import Board, HexPos, HexDir, SpawnAction, SpreadAction, Action
from referee.game.constants import *
from typing import Generator
from copy import deepcopy

class HexVec:
    r: int
    q: int

    def __add__(self, other: 'HexVec') -> 'HexVec':
        return self.__class__(self.r + other.r, self.q + other.q)

    def __sub__(self, other: 'HexVec') -> 'HexVec':
        return self.__class__(self.r - other.r, self.q - other.q)

    def __neg__(self) -> 'HexVec':
        return self.__class__(self.r * -1, self.q * -1)

    def __mul__(self, n: int) -> 'HexVec':
        return self.__class__(self.r * n, self.q * n)

    def __iter__(self) -> Generator[int, None, None]:
        yield self.r
        yield self.q

def correctCoordinates(coordinates: tuple):
    """
    this function is being used to correct the corrdinates
    for example: (7, 7) -> (0, 0)
    """
    r = coordinates[0]
    q = coordinates[1]
    if r < 0:
        r = 7 - abs(r) % 7
    else:
        r = r % 7
    if q < 0:
        q = 7 - abs(q) % 7
    else:
        q = q % 7
    return (r, q)

def spawn(board: dict[tuple, tuple], token, color):
    board[token] = (color, 1)
    
def spread(board: dict[tuple, tuple], token: tuple, direction: tuple):
    """
    spread function. The input is the board status, tokens coordinates
    that about to move, and move direction
    """
    color = board[token][0]
    power = board[token][1]
    curr_tok = token
    
    while power > 0 :
        curr_tok = correctCoordinates((curr_tok[0] + direction[0], curr_tok[1] + direction[1]))
        addToken(board,curr_tok,color)
        power -= 1

    # delete the token being spreaded
    del board[token]

def addToken(board: dict[tuple, tuple], token: tuple, color: str):
    """
    Add a token to the board, increment its power if it's already present,
    and remove it if its power reaches 7.
    """
    if token in board:
        current_power = board[token][1] + 1
        if current_power < 7:
            board[token] = (color, current_power)
        else:
            del board[token]
    else:
        board[token] = (color, 1)

def convert_board(board: Board):
    dim = BOARD_N
    converted_board = {}
    for row in range(dim * 2 - 1):
        for col in range(dim - abs(row - (dim - 1))):
            # Map row, col to r, q
            r = max((dim - 1) - row, 0) + col
            q = max(row - (dim - 1), 0) + col
            if board._cell_occupied(HexPos(r, q)):
                color, power = board._state[HexPos(r, q)]
                converted_board[(r, q)] = (color, power)
    return converted_board

def isTerminal(board: dict[tuple, tuple]):
    colors = set()
    for token in board.keys():
        colors.add(board[token][0])
        if len(colors) > 1:
            return False
    return True

def move(board: dict[tuple, tuple], action):
    cor = action[1]
    #use copy of state, otherwise ruined the original state
    child_state = deepcopy(board)
    if action[0] == 'Spawn':
        color = action[2]
        spawn(child_state, cor, color)
    else:
        direction = action[2]
        spread(child_state, cor, direction)

def convert_action(action):
    cor = action[1]
    r = cor[0]
    q = cor[1]
    if action[0] == 'Spawn':
        return SpawnAction(HexPos(r, q))
    else:
        direction_r = action[2][0]
        direction_q = action[2][1]
        direction = HexVec(direction_r, direction_q)
        return SpreadAction(HexPos(r, q), direction)
