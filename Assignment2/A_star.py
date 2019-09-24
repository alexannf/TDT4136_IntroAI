from assignment2.Map import Map_Obj
from math import sqrt


class Node:

    def __init__(self, pos, parent_node, ncost=1):
        # position of the node, fixed
        self.pos = pos
        if parent_node is not None:
            # cost of traversing to this node (often through other nodes), called g(s) in the lecture
            self.gcost = parent_node.get_gcost() + ncost
        else:
            # only important for initiating the starting node (it has no parent)
            self.gcost = 0
        # a given, or deducted, score on this node compared to our goal node, called h(s) in the lecture
        self.hcost = 0
        # the total cost of a solution path that is including this node
        self.fcost = 0
        # "Entry fee" for traversing through this node, fixed
        self.ncost = ncost
        # we need to know about the nodes parent so we can backtrack after we find the goal node
        self.parent = parent_node


   # --- Getters ---

    def get_position(self):
        return self.pos

    def get_gcost(self):
        return self.gcost

    def get_fcost(self):
        return self.fcost

    def get_parent(self):
        return self.parent

    # --- Methods for calculating hcost and fcost

    def calculate_hcost(self, goalpos):
        """
        calculates the distance from this node to the goalnode, gives a weight called hcost (heuristic cost)
        using euclidean distance, as it gives the best result for different edge costs
        :param goalpos: position on the grid of our goal node
        :return: nothing
        """
        self.hcost = sqrt((self.pos[0] - goalpos[0]) ** 2 + (self.pos[1] - goalpos[1]) ** 2)

    def calculate_fcost(self):
        self.fcost = self.gcost + self.hcost

    # for nice printing
    def __str__(self):
        return str(self.pos)

    # allows us to compare nodes in a easy way
    def __eq__(self, other):
        return self.get_position() == other.get_position()


class A_Star:

    def __init__(self, map_object, start_node=None):
        # the map_object (grid) we are searching in
        self.map_object = map_object
        # a stack of nodes we have discovered that have children that are not visited
        self.open = []
        # a stack of nodes we have discovered where all children have been visited
        self.closed = []
        # initiate start node at the start position given to us by the map_object object, or manually (for testing)
        if start_node is None:
            self.start_node = Node(map_object.get_start_pos(), None, 0)
        else:
            self.start_node = start_node
        # calculate the "distance" from our starting node to our goal node
        self.start_node.calculate_hcost(self.map_object.get_end_goal_pos())
        # calculate the total cost, will be the same as hcost since we are already at the startnode
        self.start_node.calculate_fcost()
        # add start node to open list
        self.open.append(self.start_node)


    # checks if our open list does not contain node
    def node_not_in_open(self, node):
        for open_node in self.open:
            if open_node.__eq__(node):
                return False
        return True

    # checks if our closed list does not contain node
    def node_not_in_closed(self, node):
        for closed_node in self.closed:
            if closed_node.__eq__(node):
                return False
        return True

    def discover_children(self, parent_node):
        """
        discovers children that are not in the closed list, and replaces Nodes in the open list if a children of the
        parent node has a better path
        :param parent_node:
        :return: nothing
        """
        pos = parent_node.get_position()
        for i in range(-1, 2, 2):
            horiz_node_pos = [pos[0] + i, pos[1]]
            vertic_node_pos = [pos[0], pos[1] + i]
            # hcost & vcost can be -1 (illegal) or 1,2 or 3 (entry cost)
            hcost = self.map_object.get_cell_value(horiz_node_pos)
            vcost = self.map_object.get_cell_value(vertic_node_pos)
            horiz_node = Node(horiz_node_pos, parent_node, hcost)
            vertic_node = Node(vertic_node_pos, parent_node, vcost)
            self.evaluate_child(horiz_node, hcost)
            self.evaluate_child(vertic_node, vcost)
        # we have found all children, we can close the node
        self.closed.append(parent_node)

    def evaluate_child(self, evaluating_node, node_cost):
        """
        3 step process:
        (1): checks if evaluating node is possible to visit, if so go to step 2
        (2): calculate h-value, go to step 3
        if evaluating node not in open list:
            (3 a): add to open list
        else: (we know a equivalent node exists in open list)
            (3 b): evaluate if evaluating node through this path is better than existing node and replace if so

        :param evaluating_node: children node of parent in discover_children method
        :param node_cost: can be -1 (illegal) or 1, 2, 3 or 4 (entry cost)
        :return: nothing
        """
        if node_cost != -1 and self.node_not_in_closed(evaluating_node):
            # we know that we are going to use this node so we calculate
            evaluating_node.calculate_hcost(self.map_object.get_goal_pos())
            evaluating_node.calculate_fcost()
            if self.node_not_in_open(evaluating_node):
                self.open.append(evaluating_node)
            # here we know our child node already is represented in open list, checking for improvements
            else:
                # retrieve node in open to check if evaluating node path is a better choice
                open_node = self.get_matching_node(evaluating_node)
                if self.has_better_path(evaluating_node, open_node):
                    # update node cost in open list
                    self.open.remove(open_node)
                    self.open.append(evaluating_node)

    # used to fetch the equivalent node in our open list so we can evaluate
    def get_matching_node(self, evaluating_node):
        for open_node in self.open:
            if open_node.__eq__(evaluating_node):
                return open_node

    # always make sure you have calculated f-values before you call this method
    def has_better_path(self, evaluating_node, open_node):
        if evaluating_node.get_fcost() < open_node.get_fcost():
            return True
        else:
            return False

    # returns a list of the positions in our shortest path, we use recursion to fetch parents until there is none
    def retrieve_shortest_path(self, node):
        if node.get_parent() is None:
            return [node.get_position()]
        else:
            return [node.get_position()] + self.retrieve_shortest_path(node.get_parent())

    # alternative method, will save a picture for every recursive call showing us the complete path in the end
    def retrieve_and_save_shortest_path(self, node, folder):
        if node.get_parent() is None:
            self.map_object.set_cell_value(node.get_position(), ' F ')
            self.map_object.save_map(folder)
            return [node.get_position()]
        else:
            self.map_object.set_cell_value(node.get_position(), ' F ')
            self.map_object.save_map(folder)
            return [node.get_position()] + self.retrieve_and_save_shortest_path(node.get_parent(), folder)


    def search(self, folder=None):
        """
        main function:

        iterates through the list of open nodes (only legal nodes)
        the list is sorted by the lowest f-score which makes open[0] the best candidate for our next node to expand

        adding nodes to closed [] is handled in the discover_children method


        :param folder (optional): you can save images in each iteration, this makes a folder where they are placed
                you might need to change path in Map.py (the path is relative to the dictionary)
        :return: the list of each position you must walk to get to the goal position, empty list if we can't find
                the goal position
        """
        while len(self.open) > 0:
            lowest_cost_node = self.open.pop(0)
            print("best choice in open list was %s" % lowest_cost_node)
            self.map_object.set_cell_value(lowest_cost_node.get_position(), ' P ')
            if folder is not None:
                self.map_object.save_map(folder)
            if lowest_cost_node.get_position() == self.map_object.get_goal_pos():
                if folder is not None:
                    shortest_path = self.retrieve_and_save_shortest_path(lowest_cost_node, folder)
                else:
                    shortest_path = self.retrieve_shortest_path(lowest_cost_node)
                print("you've reached the goal!\nhere is the shortest path: %s" % shortest_path)
                return shortest_path
            self.discover_children(lowest_cost_node)
            self.open = sorted(self.open, key=lambda n: n.get_fcost())
        return []


if __name__ == "__main__":
    map1 = Map_Obj(1)
    map2 = Map_Obj(2)
    map3 = Map_Obj(3)
    map4 = Map_Obj(4)

    AstarM1 = A_Star(map1)
    AstarM2 = A_Star(map2)
    AstarM3 = A_Star(map3)
    AstarM4 = A_Star(map4)

    path1 = AstarM1.search()
    path2 = AstarM2.search()
    path3 = AstarM3.search()
    path4 = AstarM4.search()
    """
    Use these methods instead if you want to generate pictures of the process into the pictures folder
    
    path1 = AstarM1.search("map1")
    path2 = AstarM2.search("map2")
    path3 = AstarM3.search("map3")
    path4 = AstarM4.search("map4")
    """
