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
        self.node_explore = []
        self.time_taken = []
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
                #random.seed(88)
                #starttime = time.time()
                minimax = MiniMax(self.game_state, PlayerColor.RED, max_depth=2)
                #minimax.generate_tree()
                best_action = minimax.find_next_step()
                #endtime = time.time()
                #print('time costs this round = ', endtime - starttime)
                #actions = minimax.root.get_legal_actions()
                #return random.choice(actions)
                return best_action
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                #starttime = time.time()
                minimax = MiniMax(self.game_state, PlayerColor.BLUE, max_depth=2)
                #minimax.generate_tree()
                #total_nodes = minimax.print_tree()
                best_action = minimax.find_next_step()
                #endtime = time.time()
                #self.node_explore.append(total_nodes)
                #self.time_taken.append(endtime - starttime)
                #print(endtime - starttime)
                #print('total time costs = ', sum(self.time_taken))
                #print(self.node_explore)
                #print(self.time_taken)

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
    def __init__(self, state: Board, color: PlayerColor, level: int, action = None) -> None:
        self.color = color
        self.state = state
        self.action = action
        self.level = level
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def is_terminal_node(self):
        return self.state.game_over
    
    def get_legal_actions(self):
        spawns = []
        spreads = []
        directions = [HexDir.Down, HexDir.DownLeft, HexDir.DownRight, HexDir.Up, HexDir.UpLeft, HexDir.UpRight]
        for cor in COORDINATES:
            if self.state._cell_occupied(cor):
                cellColor, cellPower = self.state[cor]
                if cellColor == self.color:
                    for direction in directions:
                        spreads.append(SpreadAction(cor, direction))
            else:
                spawns.append(SpawnAction(cor))

        random.shuffle(spawns)
        if self.state._total_power >= 49:
            
            return spreads
        else:
            return spreads + spawns
    
    def evaluation(self, root_color):

        opp_power = 0
        self_power = 0
        opp_cells = 0
        self_cells = 0

        for cell in self.state._state.values():
            if cell.player == root_color:
                self_power += cell.power
                self_cells += 1
            elif cell.player == _SWITCH_COLOR[root_color]:
                opp_power += cell.power
                opp_cells += 2

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
    
    def evaluation_state(self, root_color, test_state):

        opp_power = 0
        self_power = 0
        opp_cells = 0
        self_cells = 0

        for cell in test_state._state.values():
            if cell.player == root_color:
                self_power += cell.power
                self_cells += 1
            elif cell.player == _SWITCH_COLOR[root_color]:
                opp_power += cell.power
                opp_cells += 2

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

    
class MiniMax:
    def __init__(self, root_state, curr_color, max_depth = 3):
        self.root = Node(root_state, curr_color, level=0)
        self.max_depth = max_depth
    
    def find_next_step(self):
        maximizing_player = True
        best_action = None
        start_time = time.time()
        time_limit = 0.8

        for depth in range(1, self.max_depth + 1):
            
            current_value, current_action = self._minimax_alpha_beta(self.root, depth, float('-inf'), float('inf'), maximizing_player, time_limit)
            best_action = current_action
                

            # Check if the elapsed time exceeds the time limit
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time >= time_limit:
                break
        
        return best_action



    def _minimax_alpha_beta(self, node, depth, alpha, beta, maximizing_player, start_time=None, time_limit=1):

        if depth == 0 :
            return node.evaluation(self.root.color), node.action
        if node.is_terminal_node():
            if node.state.winner_color == self.root.color:
                return float('inf'), node.action
            else:
                return float('-inf'), node.action

        if not node.children:
            legal_actions = node.get_legal_actions()
        best_action = None
        if maximizing_player:
            max_value = float('-inf')
            if node.children:
                for child in node.children:
                    value, _ = self._minimax_alpha_beta(child, depth - 1, alpha, beta, False, start_time, time_limit)

                    if value > max_value:
                        max_value = value
                        best_action = child.action
                    alpha = max(alpha, max_value)
                    if beta <= alpha:
                        break
                return max_value, best_action
            
            else:
                for action in legal_actions:
                    child_state = deepcopy(node.state)
                    child_state.apply_action(action)
                    child_node = Node(child_state, _SWITCH_COLOR[node.color], node.level + 1,action=action)
                    node.add_child(child_node)
                    child_node.action = action
                    value, _ = self._minimax_alpha_beta(child_node, depth - 1, alpha, beta, False, start_time, time_limit)

                    if value > max_value:
                        max_value = value
                        best_action = action
                    alpha = max(alpha, max_value)
                    if beta <= alpha:
                        break
                return max_value, best_action
        else:
            min_value = float('inf')
            for action in legal_actions:
                child_state = deepcopy(node.state)
                child_state.apply_action(action)

                value = self.root.evaluation_state(self.root.color, child_state)

                if value < min_value:
                    min_value = value
                    best_action = action
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_value, best_action


    def print_tree(self):
        total_nodes = self._print_tree_recursive(self.root, 0)
        print(f"Total nodes: {total_nodes}")
        return total_nodes

    def _print_tree_recursive(self, node: Node, indent_level):
        indent = '  ' * indent_level
        if node.action:
            print(f"{indent}{node.action} (Level: {node.level}, Value: {node.evaluation()})")
        else:
            print(f"{indent}Root (Level: {node.level}, Value: {node.evaluation()})")

        node_count = 1  # Count the current node
        for child in node.children:
            node_count += self._print_tree_recursive(child, indent_level + 1)

        return node_count
