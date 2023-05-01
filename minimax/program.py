# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
from referee.game.constants import *
from copy import deepcopy
import random
import time
_SWITCH_COLOR = {
    PlayerColor.RED: PlayerColor.BLUE,
    PlayerColor.BLUE: PlayerColor.RED
}
# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

COORDINATES = [
    HexPos(r, q)
    for r in range(7)
    for q in range(7)
    if abs(r - q) < 7
]

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self.game_state = Board()
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
                minimax = MiniMax(self.game_state, PlayerColor.RED, max_depth=3)
                spawns, spreads = minimax.root.get_legal_actions()
                return random.choice(spawns + spreads)
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                starttime = time.time()
                minimax = MiniMax(self.game_state, PlayerColor.BLUE, max_depth=2)
                minimax.generate_tree()
                #minimax.print_tree()
                best_action = minimax.find_next_step()
                endtime = time.time()
                print('time costs this round = ', endtime - starttime)
                return best_action
    
    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        self.game_state.apply_action(action)
        #print(self.game_state._state)
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

class Node:
    def __init__(self, state: Board, color: PlayerColor, level: int, parent = None, action = None) -> None:
        self.color = color
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.level = level

    def add_child(self, child):
        self.children.append(child)

    def is_terminal_node(self):
        return self.state.game_over
    
    def get_legal_actions(self):
        board = self.state
        color = self.color
        spawns = []
        spreads = []
        directions = [HexDir.Down, HexDir.DownLeft, HexDir.DownRight, HexDir.Up, HexDir.UpLeft, HexDir.UpRight]
        for cor in COORDINATES:
            if board._cell_occupied(cor):
                cellColor, cellPower = board[cor]
                if cellColor == color:
                    for direction in directions:
                        spreads.append(SpreadAction(cor, direction))
            else:
                spawns.append(SpawnAction(cor))
        return spawns, spreads
    
    def evaluation(self):
        red_power = 0
        blue_power = 0
        for cell in self.state._state.values():
            if cell.player == PlayerColor.BLUE:
                blue_power += cell.power
            else:
                red_power += cell.power

        return blue_power - red_power
    
class MiniMax:
    def __init__(self, root_state, curr_color, max_depth = 3):
        self.root = Node(root_state, curr_color, level=0)
        self.max_depth = max_depth
    
    def generate_tree(self):
        self._generate_tree_recursive(self.root, self.max_depth)

    def _generate_tree_recursive(self, node: Node, depth):
        if depth == 0 or node.is_terminal_node():
            return
        
        spawns, spreads = node.get_legal_actions()
        next_color = _SWITCH_COLOR[node.color]
        #print(spawns + spreads)
        for action in spawns + spreads:
            child_state = deepcopy(node.state)
            child_state.apply_action(action)
            child_node = Node(child_state, next_color, node.level + 1, parent=node, action=action)
            node.add_child(child_node)
            self._generate_tree_recursive(child_node, depth - 1)
    
    def find_next_step(self):
        maximizing_player = self.root.color == PlayerColor.BLUE
        best_value, best_action = self._minimax_alpha_beta(self.root, self.max_depth, float('-inf'), float('inf'), maximizing_player)
        return best_action

    def _minimax_alpha_beta(self, node, depth, alpha, beta, maximizing_player):
        if depth == 0 or node.is_terminal_node():
            #print(node.evaluation())
            return node.evaluation(), node.action

        if maximizing_player:
            max_value = float('-inf')
            best_action = None
            for child in node.children:
                value, action = self._minimax_alpha_beta(child, depth - 1, alpha, beta, False)
                if value > max_value:
                    max_value = value
                    best_action = child.action
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
            return max_value, best_action
        else:
            min_value = float('inf')
            best_action = None
            for child in node.children:
                value, action = self._minimax_alpha_beta(child, depth - 1, alpha, beta, True)
                if value < min_value:
                    min_value = value
                    best_action = child.action
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_value, best_action
    def print_tree(self):
        self._print_tree_recursive(self.root, 0)

    def _print_tree_recursive(self, node: Node, indent_level):
        indent = '  ' * indent_level
        if node.action:
            print(f"{indent}{node.action} (Level: {node.level}, Value: {node.evaluation()})")
        else:
            print(f"{indent}Root (Level: {node.level}, Value: {node.evaluation()})")

        for child in node.children:
            self._print_tree_recursive(child, indent_level + 1)