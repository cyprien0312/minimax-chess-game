# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

import math
import random
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
from referee.game.constants import *
from referee.game.exceptions import *
from copy import deepcopy

# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!
_SWITCH_COLOR = {
    PlayerColor.RED: PlayerColor.BLUE,
    PlayerColor.BLUE: PlayerColor.RED
}

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
                mcts = MCTS(self.game_state, PlayerColor.RED, num_iterations=10)
                actions = mcts.root.get_legal_actions()
                while True:
                    try:
                        best_action = random.choice(actions)
                        copy_state = deepcopy(self.game_state)
                        copy_state.apply_action(best_action)
                        break
                    except IllegalActionException:
                        actions.remove(best_action)
                        
                return best_action
            case PlayerColor.BLUE:
                mcts = MCTS(self.game_state, PlayerColor.BLUE, num_iterations=10)
                best_action = mcts.search()
                return best_action

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        self.game_state.apply_action(action)
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

class Node:
    def __init__(self, state: Board, color: PlayerColor, parent=None, action=None):
        self.color = color
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.wins = 0
        self.visits = 0
        self.unexpanded_children = self.get_legal_actions()

    def add_child(self, child):
        self.children.append(child)

    def is_terminal_node(self):
        return self.state.game_over
    
        
    def get_legal_actions(self):
        # return a list of leagl actions
        board = self.state
        color = self.color
        dim = BOARD_N
        actions = []
        directions = [HexDir.Down, HexDir.DownLeft, HexDir.DownRight, HexDir.Up, HexDir.UpLeft]
        for row in range(dim * 2 - 1):
            for col in range(dim - abs(row - (dim - 1))):
                # Map row, col to r, q
                r = max((dim - 1) - row, 0) + col
                q = max(row - (dim - 1), 0) + col
                if board._cell_occupied(HexPos(r, q)):
                    cellColor, cellPower = board[HexPos(r, q)]
                    if cellColor == color:
                        for direction in directions:
                            actions.append(SpreadAction(HexPos(r, q), direction))
                else:
                    actions.append(SpawnAction(HexPos(r, q)))
        return actions



class MCTS:
    def __init__(self, root_state, curr_color, num_iterations=10, exploration_parameter=math.sqrt(2)):
        self.root = Node(root_state, curr_color)
        self.num_iterations = num_iterations
        self.exploration_parameter = exploration_parameter

    # search for the best child
    def search(self):
        # loop for iterations, later on changed to time
        for i in range(self.num_iterations):
            print(i)
            # selection, needs check
            selected_node = self.select_node(self.root)
            if not selected_node.is_terminal_node():
                child_node = self.expand(selected_node)
            #simulation for selected node
            winner_color = self.rollout(child_node)
            #back propagation
            self.backpropagate(child_node, (winner_color == self.root.color))

        #after iteration, choose the best child
        best_child = self.best_child(self.root, self.exploration_parameter)
        return best_child.action

    #need check and fix!
    def select_node(self, node: Node):

        # if the selected node is not full expanded, return the node, else find the best children
        if node.unexpanded_children:
            return node
        else:
            best_child = self.best_child(node, self.exploration_parameter)
            return node.select_node(best_child)
        
    #expand the node, and add all available child
    def expand(self, node):
        if not node.unexpanded_children:
            return
        while True:
            try:
                action = random.choice(node.unexpanded_children)
                copy_state = deepcopy(node.state)
                copy_state.apply_action(action)
                break
            except IllegalActionException:
                node.unexpanded_children.remove(action)
                
        child_state = deepcopy(node.state)
        child_state.apply_action(action)
        child_color = _SWITCH_COLOR[node.color]
        child_node = Node(child_state, child_color, node, action)
        node.add_child(child_node)
        return child_node
    #simulations
    def rollout(self, node):
        #create copy node
        tmp_node = deepcopy(node)
        curr_color = tmp_node.color
        curr_state = tmp_node.state

        #loop until game over
        while not curr_state.game_over:
            #it needs to be expending nodes and switch side at the same time, below comment code is wrong
            #print(curr_state.turn_count)
            legal_actions = tmp_node.get_legal_actions()
            #random move
            while True:
                try:
                    random_action = random.choice(legal_actions)
                    copy_state = deepcopy(curr_state)
                    copy_state.apply_action(random_action)
                    break
                except IllegalActionException:
                    legal_actions.remove(random_action)
            
            curr_state.apply_action(random_action)
            tmp_node.state = curr_state
            # need check 
            curr_color = _SWITCH_COLOR[curr_color]
            tmp_node.color = curr_color
        return curr_state.winner_color
            

    #back propagation 
    def backpropagate(self, node, result):
        node.visits += 1
        node.wins += result
        if node.parent:
            self.backpropagate(node.parent, 1 - result)

    def best_child(self, node, exploration_parameter):
        def uct(child):
            return (child.wins / child.visits) + exploration_parameter * math.sqrt(
                math.log(node.visits) / child.visits
            )

        return max(node.children, key=uct)
    


