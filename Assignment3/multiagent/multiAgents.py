# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        """
         Pseudocode from the book:
         function MINIMAX-DECISION(state) returns an action
          return the max of the available action taking into account recursive min-max calls
         
         function MAX-VALUE(state) returns a utility value
          if TERMINAL-TEST(state) then return UTILITY(state)
          v = -100000000000000000000000000000 (negative infinity)
          for each a in ACTIONS(state) do
          MAX(v, MIN-VALUE(RESULT(s, a)))
          return v
       
         function MIN-VALUE(state) returns a utility value
          if TERMINAL-TEST(state) then return UTILITY(state)
          v = 100000000000000000000000000000 (infinity)
          for each a in ACTIONS(state) do
          v = MIN(v, MAX-VALUE(RESULT(s, a)))
          return v
        """

        def minValue(gameState, depth, agent):
            """
            Calculates the action that leads to the lowest score in our zero sum game.
            The score is calculated unbiased and a negative score means our ghost agent is "leading"
            ghost agents therefore aim to get the lowest possible score, even in a losing position. (optimal play)

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, will be >0 (ghost-agent).
            :return:
                minimum: the lowest possible score given the depth we are allowed to search.
                action: the corresponding action that achieves this score.
            """
            # represents positive infinity, we are searching to make minimum as low as possible
            minimum = 1000000
            # we will set this variable as the best action (corresponds to minimum value)
            bestAction = None
            ghostActions = gameState.getLegalActions(agent)

            # if there are no legal actions we are in a terminal state
            if not ghostActions:
                return self.evaluationFunction(gameState), None

            for action in ghostActions:
                # emulates the state we want to check
                stateAfterAction = gameState.generateSuccessor(agent, action)
                # we are only interested the value
                evalValue, evalAction = minOrMax(stateAfterAction, depth, agent + 1)
                #
                if evalValue < minimum:
                    minimum, bestAction = evalValue, action
            return minimum, action

        def maxValue(gameState, depth, agent):
            """
            Calculates the action that leads to the highest score in our zero sum game.
            The score is calculated unbiased and a negative score means our ghost agent is "leading"
            ghost agents therefore aim to get the lowest possible score, even in a losing position. (optimal play)

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, will be 0 (pacman-agent).
            :return:
                maximum: the highest possible score given the depth we are allowed to search.
                action: the corresponding action that achieves this score.
            """
            # represents negative infinity, we are searching to make minimum as high as possible
            maximum = -1000000
            # we will set this variable as the best action (corresponds to maximum value)
            bestAction = None
            pacmanActions = gameState.getLegalActions(agent)

            # if there are no legal actions we are in a terminal state
            if not pacmanActions:
                return self.evaluationFunction(gameState), None

            for action in pacmanActions:
                # emulates the state we want to check
                stateAfterAction = gameState.generateSuccessor(agent, action)
                # we are only interested the value
                evalValue, evalAction = minOrMax(stateAfterAction, depth, agent + 1)
                if evalValue > maximum:
                    maximum, bestAction = evalValue, action
            return maximum, bestAction

        def minOrMax(gameState, depth, agent):
            """
            used to count the depths and determine if our next call should be maxValue or minValue

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, can be either pacman-agent (0) or ghost-agent (>0)
            :return:
                value: the best possible score given the depth we are allowed to search, relative to the agent we
                call it on.
                action: the corresponding action that achieves this score.
            """
            # this is true if we have checked all ghost agents. Start again at 0-agent with increased depth
            if agent >= gameState.getNumAgents():
                depth += 1
                agent = 0

            # initial condition
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState), None
            # agent 0 is pacman, we need to call maxValue
            elif agent == 0:
                return maxValue(gameState, depth, agent)
            # agent >0 is a ghost, we need to call minValue
            else:
                return minValue(gameState, depth, agent)

        # we start our search at depth 0, for agent 0 (pacman)
        value, action = minOrMax(gameState, 0, 0)
        return action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        """
         Algorithms from the book:
        
         function ALPHA-BETA-SEARCH(state) returns an action
          v = MAX-VALUE(state, -inf, inf)
          return the action in ACTIONS(state) with value v
         
         function MAX-VALUE(state, al, be) returns a utility value
          if TERMINAL-TEST(state) then return UTILITY(state)
          v = -100000000000000000000000000000 (negative infinity)
          for each a in ACTIONS(state) do
           v = MAX(v, MIN-VALUE(RESULT(s, a), al, be))
           if v >= be then return v
            al = MAX(al, v)
          return v
          
          
         function MIN-VALUE(state, al, be) returns a utility value
          if TERMINAL-TEST(state) then return UTILITY(state)
          v = 100000000000000000000000000000 (positive infinity)
          for each a in ACTIONS(state) do
           v = MIN(v, MAX-VALUE(RESULT(s, a), al, be))
           if v <= al then return v
            be = MIN(al, v)
          return v
        """

        def alfaBetaMinValue(gameState, depth, agent, a, b):
            """
            Calculates the action that leads to the lowest score in our zero sum game.
            The score is calculated unbiased and a negative score means our ghost agent is "leading"
            ghost agents therefore aim to get the lowest possible score, even in a losing position. (optimal play)

            In alpha-beta pruning we cut our computation short if we know our best min() evaluation is lower than
            anything the parent alfaBetaMaxValue function would choose. threshold value is a.

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, will be >0 (ghost-agent)
            :param a: alpha, the highest value we can find in our scope (depends on gameState)
            :param b: beta, the lowest value we can find in our scope (depends on gameState)
            :return:
            """
            # represents positive infinity, we are searching to make minimum as low as possible
            minimum = 1000000
            # we will set this variable as the best action (corresponds to minimum value)
            bestAction = None
            ghostActions = gameState.getLegalActions(agent)

            # if there are no legal actions we are in a terminal state
            if not ghostActions:
                return self.evaluationFunction(gameState), None

            for action in ghostActions:
                # emulates the state we want to check
                stateAfterAction = gameState.generateSuccessor(agent, action)
                # we are only interested the value
                evalValue, evalAction = alfaBetaMinOrMax(stateAfterAction, depth, agent + 1, a, b)
                if evalValue < minimum:
                    minimum, bestAction = evalValue, action
                # important: returns evalValue and action immediately if this is true, all computations will
                # result in giving parent alfaBetaMaxValue a worse choice than it already has
                if evalValue < a:
                    return evalValue, action
                b = min(b, evalValue)
            return minimum, bestAction

        def alfaBetaMaxValue(gameState, depth, agent, a, b):
            """
            Calculates the action that leads to the highest score in our zero sum game.
            The score is calculated unbiased and a negative score means our ghost agent is "leading"
            ghost agents therefore aim to get the lowest possible score, even in a losing position. (optimal play)

            In alpha-beta pruning we cut our computation short if we know our best max() evaluation is higher than
            anything the parent alfaBetaMinValue function would choose. threshold value is b.

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, will be 0 (pacman-agent).
            :param a: alpha, the highest value we can find in our scope (depends on gameState)
            :param b: beta, the lowest value we can find in our scope (depends on gameState)
            :return:
            """
            # represents negative infinity, we are searching to make minimum as high as possible
            maximum = -1000000
            # we will set this variable as the best action (corresponds to maximum value)
            bestAction = None
            pacmanActions = gameState.getLegalActions(agent)

            # if there are no legal actions we are in a terminal state
            if not pacmanActions:
                return self.evaluationFunction(gameState), None

            for action in pacmanActions:
                # emulates the state we want to check
                stateAfterAction = gameState.generateSuccessor(agent, action)
                # we are only interested the value
                evalValue, evalAction = alfaBetaMinOrMax(stateAfterAction, depth, agent + 1, a, b)
                if evalValue > maximum:
                    maximum, bestAction = evalValue, action
                # important: returns evalValue and action immediately if this is true, all computations will
                # result in giving parent alfaBetaMinValue a worse choice than it already has
                if evalValue > b:
                    return evalValue, action
                a = max(a, evalValue)
            return maximum, bestAction

        def alfaBetaMinOrMax(gameState, depth, agent, a, b):
            """
            used to count the depths and determine if our next call should be maxValue or minValue
            doesn't really change much from minOrMax, as the logic for choosing what functions to call are still
            the same, just some inner computations in alfaBetaMaxValue and alfaBetaMinValue are "pruned" (cut)

            :param gameState:
            :param depth: the dept we currently are at.
            :param agent: agent, can be either pacman-agent (0) or ghost-agent (>0)
            :param a: alpha, the highest value we can find in our scope (depends on gameState)
            :param b: beta, the lowest value we can find in our scope (depends on gameState)
            :return:
            """
            # this is true if we have checked all ghost agents. Start again at 0-agent with increased depth
            if agent >= gameState.getNumAgents():
                depth += 1
                agent = 0

            # initial condition
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState), None
            # agent 0 is pacman, we need to call maxValue
            elif agent == 0:
                return alfaBetaMaxValue(gameState, depth, agent, a, b)
            # agent >0 is a ghost, we need to call alfaBetaMinValue
            else:
                return alfaBetaMinValue(gameState, depth, agent, a, b)

        # we start our search at depth 0, for agent 0 (pacman). a = "- inf" & b = "inf"
        value, action = alfaBetaMinOrMax(gameState, 0, 0, -1000000,1000000)
        return action


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

