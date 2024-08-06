__author__ = "<your name>"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "<your e-mail>"

import numpy as np

agentName = "Limited-depth-minimax"

class Node:
    def __init__(self, state):
        self.state = state
        self.value = None
        self.best_child = None

class State:
    def __init__(self, bidding_on, items_left, my_cards, my_bank, opponents_bank, opponents_cards):
        self.bidding_on = bidding_on
        self.items_left = items_left
        self.my_cards = my_cards
        self.my_bank = my_bank
        self.opponents_bank = opponents_bank
        self.opponents_cards = opponents_cards

        self.my_action = None
        self.opponent_action = None
    
    def get_evaluation_value(self):
        return self.my_bank - self.opponents_bank
    
    def is_terminal_state(self):
        return len(self.items_left) <= 1
    
    def get_my_possible_next_states(self):
        next_states = []
        for i in range(len(self.my_cards)):
            my_action = self.my_cards[i]
            next_my_cards = tuple([card for card in self.my_cards if card != my_action]) # Get a new tuple of my cards after using a card
            # Generate a new state
            next_state = State(self.bidding_on, self.items_left[:], next_my_cards, self.my_bank, self.opponents_bank, self.opponents_cards)
            next_state.my_action = my_action
            next_states.append(next_state)
        return next_states
    
    def get_opponents_possible_next_states(self):
        next_states = []
        for i in range(len(self.opponents_cards)):
            opponent_action = self.opponents_cards[i]
            next_my_bank = self.my_bank
            next_opponents_bank = self.opponents_bank
            next_bidding_on = self.items_left[0] # Note: In real cases, next item should be random
            next_items_left = self.items_left[1:]
            next_opponents_cards = tuple([card for card in self.opponents_cards if card != opponent_action]) # Get a new tuple of opponent's cards
            if self.my_action > opponent_action:
                next_my_bank += self.bidding_on
            elif self.my_action == opponent_action:
                next_bidding_on += self.bidding_on
            else:
                next_opponents_bank += self.bidding_on
            
            # Generate a new state
            new_state = State(next_bidding_on, next_items_left, self.my_cards[:], next_my_bank, next_opponents_bank, next_opponents_cards)

            next_states.append(new_state)
        return next_states


class RajAgent():
    """
    A class that encapsulates the code dictating the
    behaviour of the agent playing the game of Raj.

    ...

    Attributes
    ----------
    item_values : list of ints
        values of items to bid on
    card_values: list of ints
        cards agent bids with

    Methods
    -------
    AgentFunction(percepts)
        Returns the card value from hand to bid with
    """
    
    DEPTH_LIMIT = 4

    def __init__(self, item_values, card_values):
        """
        :param item_values: list of ints, values of items to bid on
        :card_values: list of ints, cards agent bids with
        """

        self.card_values = card_values
        self.item_values = item_values

    def get_best_child(self, node, depth):
        state = node.state
        next_states = []
        is_max = depth % 2 == 0
        alpha = -999999
        beta = 999999
        if is_max:
            next_states = state.get_my_possible_next_states()
        else:
            next_states = state.get_opponents_possible_next_states()

        next_depth = depth + 1
        for next_state in next_states:
            child_node = Node(next_state)
            # If already reaches the depth limit, or this child is already a terminal state, calculate the value of the child with evaluation function
            if next_depth == self.DEPTH_LIMIT or next_state.is_terminal_state():
                child_node.value = next_state.get_evaluation_value()
                # Alpha-beta pruning: if this child's value is not better, ignore all the subsequent siblings
                if (is_max and child_node.value < alpha) or ((not is_max) and child_node.value > beta):
                    continue
            else: # If not reaches the depth limit or terminal state, keep going deep
                self.get_best_child(child_node, next_depth)

            # Back up the value to parent
            if node.value == None or (is_max and child_node.value > node.value) or ((not is_max) and child_node.value < node.value):
                node.value = child_node.value
                node.best_child = child_node
                if is_max:
                    alpha = max(alpha, node.value)
                else:
                    beta = min(beta, node.value)

        return node.best_child


    def AgentFunction(self, percepts):
        """Returns the bid value of the next bid

            :param percepts: a tuple of four items: bidding_on, items_left, my_cards, opponents_cards

                        , where

                        bidding_on - is an integer value of the item to bid on;

                        items_left - the items still to bid on after this bid (the length of the list is the number of
                                    bids left in the game)

                        my_cards - the list of cards in the agent's hand

                        bank - total value of items in this game
                        
                        opponents_cards - a list of lists of cards in the opponents' hands, so in two player game, this is
                                        a list of one list of cards, in three player game, this is a list of two lists, etc.


            :return: value - card value to bid with, must be a number from my_cards
        """

        # Extract different parts of percepts.
        bidding_on = percepts[0] # e.g. 4
        items_left = percepts[1] # e.g. (-1, 1, 2, 3)
        my_cards = percepts[2] # e.g. (1, 2, 3, 4)
        bank = percepts[3] # e.g. 2
        opponents_cards = percepts[4:] # e.g. ((3, 4, 5, 6),)

         # Note: Only consider that there's only one opponent
        root_state = State(bidding_on, items_left, my_cards, bank, 0, opponents_cards[0])
        root_node = Node(root_state)

        best_child = self.get_best_child(root_node, 0)
        best_next_state = best_child.state
        action = best_next_state.my_action

        # Currently this agent just bids the first card in its hand - you need to make it smarter!
        # action = my_cards[0]

        # Return the bid
        return action