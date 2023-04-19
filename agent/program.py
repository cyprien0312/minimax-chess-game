# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

import math
import random
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
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
                return SpawnAction(HexPos(3, 3))
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                return SpreadAction(HexPos(3, 3), HexDir.Up)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.wins = 0
        self.visits = 0

    def add_child(self, child):
        self.children.append(child)

class MCTS:
    def __init__(self, root_state, num_iterations=1000, exploration_parameter=math.sqrt(2)):
        self.root = Node(root_state)
        self.num_iterations = num_iterations
        self.exploration_parameter = exploration_parameter

    def search(self):
        for _ in range(self.num_iterations):
            selected_node = self.select_node(self.root)
            result = self.rollout(selected_node.state)
            self.backpropagate(selected_node, result)

        best_child = self.best_child(self.root, 0)
        return best_child.action

    def select_node(self, node):
        if not node.children:
            return node
        else:
            return self.select_node(self.best_child(node, self.exploration_parameter))

    def expand(self, node):
        legal_actions = node.state.get_legal_actions()
        for action in legal_actions:
            child_state = node.state.copy().apply_action(action)
            child_node = Node(child_state, node, action)
            node.add_child(child_node)

    def rollout(self, state):
        while not state.is_terminal():
            legal_actions = state.get_legal_actions()
            random_action = random.choice(legal_actions)
            state = state.copy().apply_action(random_action)

        return state.get_result()

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