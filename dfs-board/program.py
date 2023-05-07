# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
import numpy as np
import random

SWITCH_COLOR = {
    PlayerColor.RED: PlayerColor.BLUE,
    PlayerColor.BLUE: PlayerColor.RED
}

DIRECTIONS = [HexDir.Down, HexDir.DownLeft, HexDir.DownRight, HexDir.Up, HexDir.UpLeft, HexDir.UpRight]

class NewBoard:
    def __init__(self, color, turn, board):
        self._color = color
        self._turn = turn
        if board is None:
            self._board = np.empty((7, 7), dtype=object)

        else:
            board_copy = board.copy()
            self._board = board_copy

    def spread(self, cell, direction, color):
        power = self._board[cell.r][cell.q][1]
        self._board[cell.r][cell.q] = None
        while power > 0:
            new_cell = HexPos(cell.r, cell.q) + direction
            if self._board[new_cell.r][new_cell.q] == None:
                self._board[new_cell.r][new_cell.q] = (color, 1)
            else:
                new_cell_power = self._board[new_cell.r][new_cell.q][1] + 1
                if new_cell_power > 6:
                    self._board[new_cell.r][new_cell.q] = None
                else:
                    self._board[new_cell.r][new_cell.q] = (color, new_cell_power)
            cell = new_cell
            power -= 1


    def get_total_power(self):
        total_sum = sum(element[1] for row in self._board for element in row if element is not None)
        return total_sum
    
    def get_legal_actions(self):
        spawns = []
        spreads = []
        for i in range(7):
            for j in range(7):
                cell = self._board[i][j]
                if cell is None and self._turn != 343:
                    spawns.append(SpawnAction(HexPos(i, j)))
                if cell is not None and cell[0] == self._color and self._turn != 343:
                    for direction in DIRECTIONS:
                        spreads.append(SpreadAction(HexPos(i, j), direction))
        random.shuffle(spawns)
        if self.get_total_power() >= 49:
            return spreads
        else:
            return spreads + spawns

    def is_terminal(self):
        self_power = 0
        oppo_power = 0
        for r in range(7):
            for q in range(7):
                cell = self._board[r][q]
                if cell is not None:
                    if cell[0] == self._color:
                        self_power += cell[1]
                    else:
                        oppo_power += cell[1]
        
        if (self_power == 0 and self._turn != 0) or (oppo_power == 0 and self._turn != 0) or \
            (self_power == 0 and oppo_power == 0 and self._turn != 0) or (self._turn >= 343):
            return True
        return False
    
    def evaluation(self, rootcolor):

        opp_power = 0
        self_power = 0
        opp_cells = 0
        self_cells = 0

        for r in range(7):
            for q in range(7):
                cell = self._board[r][q]
                if cell is not None:
                    if cell[0] == rootcolor:
                        self_power += cell[1]
                        self_cells += 1
                    else:
                        opp_power += cell[1]
                        opp_cells += 1

        power_score = self_power - opp_power
        cell_score = self_cells - opp_cells
        # Assign weights to each factor according to their importance
        power_weight = 2
        cell_weight = 1

        total_cells = self_cells + opp_cells
        endgame_threshold = int(0.5 * (7 * 7))  # 50% of the total board size

        if total_cells >= endgame_threshold:
            # Increase weights for more aggressive play when approaching the end of the game
            power_weight = 3
            cell_weight = 1

        return (power_weight * power_score) + (cell_weight * cell_score)
    
    def apply_action(self, action):

        match action:
            case SpawnAction(cell):
                self._board[cell.r][cell.q] = (self._color, 1)
            case SpreadAction(cell, direction):
                self.spread(cell, direction, self._color)
        self._turn += 1
        self._color = SWITCH_COLOR[self._color]
            

    
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        if self._color == PlayerColor.RED:
            self._turn = -1
        else:
            self._turn = 0
        self.game_state = NewBoard(self._color, self._turn, None)

        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                self._turn += 2
                #print(self._turn)
                minimax = MiniMax(self.game_state, self._turn, PlayerColor.RED, max_depth=3)
                best_action = minimax.find_next_step()
                #return random.choice(actions)
                return best_action
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                self._turn += 2
                #print(self._turn)
                minimax = MiniMax(self.game_state, self._turn, PlayerColor.BLUE, max_depth=3)
                #print(self.game_state._board)
                best_action = minimax.find_next_step()
                return best_action

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                self.game_state._board[cell.r][cell.q] = (color, 1)
                pass
            case SpreadAction(cell, direction):
                self.game_state.spread(cell, direction, color)
                #print(self.game_state._board)
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass
    
class MiniMax:
    def __init__(self, root_state, turn, curr_color, max_depth):
        self.root = NewBoard(curr_color, turn, root_state._board)
        self.max_depth = max_depth
    
    def find_next_step(self):
        best_action = None
        maximize_value = float('-inf')
        
        legal_actions = self.root.get_legal_actions()
        #print(legal_actions)
        for action in legal_actions:
            new_state = NewBoard(self.root._color, self.root._turn, self.root._board)
            new_state.apply_action(action)
            value = self._minimax_alpha_beta(new_state, 1, self.max_depth, float('-inf'), float('inf'), False)
            if value > maximize_value:
                maximize_value = value
                best_action = action
    
        return best_action

    def _minimax_alpha_beta(self, board: NewBoard, depth, max_depth, alpha, beta, maximizing_player):

        if depth == max_depth or board.is_terminal():
            return board.evaluation(self.root._color)

        legal_actions = board.get_legal_actions()

        if maximizing_player:
            max_value = float('-inf')
            for action in legal_actions:
                child_node = NewBoard(board._color, board._turn, board._board)
                child_node.apply_action(action)
                value = self._minimax_alpha_beta(child_node, depth + 1, max_depth, alpha, beta, False)
                if value > max_value:
                    max_value = value
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
            return max_value
        else:
            min_value = float('inf')
            for action in legal_actions:
                child_node = NewBoard(board._color, board._turn, board._board)
                child_node.apply_action(action)

                value = self._minimax_alpha_beta(child_node, depth + 1, max_depth, alpha, beta, True)
                if value < min_value:
                    min_value = value
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_value
