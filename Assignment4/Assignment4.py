import copy
import itertools

class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

        # used to keep count of number of times we have to backtrack
        self.backtrack_count = 0
        # used to keep count of number of times a branch search fails
        self.fail_count = 0

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self):
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [(i, j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var):
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j])

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def backtrack(self, assignment):
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.

        CODE FROM THE BOOK:

        function BACKTRACKING-SEARCH(csp) returns a solution, or failure
            return BACKTRACK({},csp)

        note: BACKTRACKING-SEARCH is defined above


        function BACKTRACK(assignment, csp) return a solution, or failure
            if assignment is complete then return assignment
            var <- SELECT-UNASSIGNED-VARIABLE(csp)
            for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
                add {var = value} to assignment
                inferences <- INFERENCE(csp, var, value)
                if inferences != failure then
                    add inferences to assignment
                    result <- BACKTRACK(assignment, csp)
                    if result != failure then
                        return result
                remove {var = value} and inferences from assignment
            return failure
        """

        # backtrack has been called, increase global counter by 1
        self.backtrack_count += 1

        # if assignment is complete then return assignment
        values = list(filter(lambda node: len(node[1]) > 1, assignment.items()))
        if len(values) == 0:
            return assignment

        # define the next values we are going to check (var is actually the key pointing to desired value)
        var = self.select_unassigned_variable(assignment)

        # loop over domain of var.
        for value in assignment[var]:
            # we must make a copy here before we do anything
            copy_assignment = copy.deepcopy(assignment)

            copy_assignment[var] = [value]

            # if changed value inference over all neighbours removing values from domain
            # returns false if an inconsistency is found and true otherwise
            inference = self.inference(copy_assignment, self.get_all_neighboring_arcs(var))

            if inference is True:
                # we found no inconsistencies, we can call backtrack with the updated domain
                # backtrack returns true
                result = self.backtrack(copy_assignment)

                # Return true if assignment complete
                if result:
                    return result
            else:
                # we tried a path that resulted in an inconsistency, fail
                self.fail_count += 1

        # No solution found
        return False




    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """

        # filter out every key, value mapping where length of value is only 1
        # (only 1 legal value in domain mapped by key)
        assignable_pairs = dict(filter(lambda pair: len(pair[1]) > 1, assignment.items()))
        # map the lists in values to the length of the lists
        length_of_values = list(map(lambda values: len(values), assignable_pairs.values()))
        # the lowest length, the key who's value has this length is the most suitable to check next (should be returned)
        lowest_length = min(length_of_values)

        # check all unassigned variables, the case length = 1 is already filtered out
        for key, value in assignable_pairs.items():
            if len(value) == lowest_length:
                return key

        """
        # alternative assignment of variable, just returns any valid unassigned variable:
        for key, value in assignment.items():
            if len(value) > 1:
                return key
        """



    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.

        CODE FROM THE BOOK:

        function AC-3(csp) returns false if an inconsistency is found and true otherwise
            inputs: csp, a binary CSP with components (X, D, C)
            local variables: queue, a queue of arcs, initially all the arcs in csp

            while queue is not empty do
                (Xi, Xj) <- REMOVE-FIRST(queue)
                if REVISE(csp, Xi, Xj) then
                    if size of Di = 0 then return false
                    for each Xk in Xi.NEIGHBOURS - {Xj} do
                        add (Xk, Xj) to queue
            return true


        function REVISE(csp, Xi, Xj) returns true if we revise the domain of Xi
            revise <- false
            for each x in Di do
                if no value y in Dj allows (x, y) to satisfy the constraint between Xi and Xj then
                    delete x from Di
                    revised <- true
            return revised
        """
    # def inference(self, assignment, queue):
        # while queue is not empty
        while len(queue) > 0:
            #  queue is a pair of the form ('INT1-INT2','INT3-INT4) i.e. ('0-0','0-1')
            # '0-0' is a key in our domain which maps to the values '0-0' can contain (list)
            pair = queue.pop()
            # revise returns true if we have eliminated something from pair[0]s domain (possible values reduced)
            if self.revise(assignment, pair[0], pair[1]):

                # if size of Di = 0 then return false, basically we revised pair[0] so that it cannot have a value
                # the revision is based purely on the rules of the game
                if len(assignment[pair[0]]) == 0:
                    return False
                # Add all neighbours to queue, so we have the possibility to revise them
                for neighbour in self.get_all_neighboring_arcs(pair[0]):
                    # these will be checked first as we use the pop() function
                    queue.append(neighbour)
        return True

    def revise(self, assignment, i, j):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.

        function REVISE(csp, Xi, Xj) returns true if we revise the domain of Xi
            revise <- false
            for each x in Di do
                if no value y in Dj allows (x, y) to satisfy the constraint between Xi and Xj then
                    delete x from Di
                    revised <- true
            return revised
        """
    # def revise(self, assignment, i, j):
        # i & j are keys in the form 'INT-INT' which can be used to access their domains

        revised = False
        # retrieve the constraints relevant for the values we want to check in the domain for Xi and Xj
        constraints = self.constraints[i][j]
        # iterates through the legal values in the domain
        for value in assignment[i]:
            filtered = list(filter(lambda pair: pair[0] == value, constraints))
            found_move = False
            for v in assignment[j]:
                for c in filtered:
                    if c[1] == v:
                        found_move = True

            # the essence of the function, shrink domain for "block" so we don't
            # use resources to traverse possibilities springing from the value currently being checked
            if not found_move:
                assignment[i].remove(value)
                revised = True

        # either true or false
        return revised



def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'NT': ['WA', 'Q'], 'NSW': ['Q', 'V']}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors)
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)

    for constraint in csp.constraints:
        for entry in csp.constraints[constraint]:
            csp.constraints[constraint][entry] = list(csp.constraints[constraint][entry])
    return csp


def create_sudoku_csp(filename):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    for constraint in csp.constraints:
        for entry in csp.constraints[constraint]:
            csp.constraints[constraint][entry] = list(csp.constraints[constraint][entry])
    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            print(solution['%d-%d' % (row, col)][0], end=" "),
            if col == 2 or col == 5:
                print('|', end=" "),
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')

if __name__ == "__main__":
    # initializing different sudoku objects
    csp_easy = create_sudoku_csp('easy.txt')
    csp_medium = create_sudoku_csp('medium.txt')
    csp_hard = create_sudoku_csp('hard.txt')
    csp_very_hard = create_sudoku_csp('veryhard.txt')

    # easy puzzle:
    solved_easy = csp_easy.backtracking_search()
    print("the solution for the easy puzzle is: ")
    print_sudoku_solution(solved_easy)
    print('\nbacktrack function was called {} times and "failure" was returned {} times\n\n'.format(
        csp_easy.backtrack_count, csp_easy.fail_count))

    # medium puzzle:
    solved_medium = csp_medium.backtracking_search()
    print("the solution for the medium puzzle is: ")
    print_sudoku_solution(solved_medium)
    print('\nbacktrack function was called {} times and "failure" was returned {} times\n\n'.format(
        csp_medium.backtrack_count, csp_medium.fail_count))

    # hard puzzle:
    solved_hard = csp_hard.backtracking_search()
    print("the solution for the hard puzzle is: ")
    print_sudoku_solution(solved_hard)
    print('\nbacktrack function was called {} times and "failure" was returned {} times\n\n'.format(
        csp_hard.backtrack_count, csp_hard.fail_count))

    # very hard puzzle:
    solved_very_hard = csp_very_hard.backtracking_search()
    print("the solution for the very hard puzzle is: ")
    print_sudoku_solution(solved_very_hard)
    print('\nbacktrack function was called {} times and "failure" was returned {} times\n\n'.format(
        csp_very_hard.backtrack_count, csp_very_hard.fail_count))