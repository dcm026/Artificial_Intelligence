'''
Author: David Milam
Date: 11/11/19
Description: Play Othello against a computer or another player or set 2 computers against each other. The
             bot uses the mini-max algorithm to determine moves. The depth of the algo can be specified when
             assigning the computer's difficulty.
TODO: Implement alpha-beta pruning to make the mini-max algorithm more efficient.
'''

# import libraries
import random
import copy

# GLOBAL variables
col_map = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'} # dictionary containing column mappings
ref_mat = [[] for j in range(11)] # matrix that holds all nodes of the tree

# the node class that will be used to build the mini-max tree
class Node():
    def __init__(self, board, position, color, move_dict, par=None, lvl=0, depth=1, move=None, root_color='B'):
        self.board = board # matrix of the positions on board
        self.position = position # a list of all the positions on the board
        self.color = color # color of this node's move white(W) or black(B)
        self.par = par # stores parent Node
        self.lvl = lvl # the depth of the node
        self.move_dict = move_dict # a dictionary of possible moves
        self.move = move # move to get to current position
        self.children = [] # an array to hold this node's children
        self.root_color = root_color
        # compute heuristic if a leaf node
        if lvl == depth:
            self.heuristic = compute_heuristic(board, position, root_color)
        else:
            self.heuristic = None
        self.best_move = None # store child that results in best move

    # class function to add children to a node
    def add_children(self, depth):
        for move in self.move_dict:
            cp_board, cp_position, cp_move_dict = copy.deepcopy(self.board), copy.deepcopy(self.position), copy.deepcopy(self.move_dict)
            board, position = get_new_board_and_position(cp_board, cp_position, self.color, move, cp_move_dict[move])
            op_color = 'B' if self.color == 'W' else 'W'
            move_dict = analyze_possible_moves(board, position, op_color)
            child = Node(board, position, op_color, move_dict, self, int(self.lvl + 1), depth, move, self.root_color)
            self.children.append(child)
            ref_mat[self.lvl+1].append(child)
            child.move_dict = move_dict

    def print_par_and_child_board(self, child):
        print('PARENT BOARD  move:', self.move, 'move_dict:', self.move_dict)
        draw_board(self.board)
        print('CHILD BOARD  move:', child.move, 'move_dict:', child.move_dict)
        draw_board(child.board)

# initialize the board, filling a matrix with the standard starting position
def board_init():
    mat = [[' ' for i in range(8)] for j in range(8)]
    mat[3][4] = 'B'
    mat[4][3] = 'B'
    mat[3][3] = 'W'
    mat[4][4] = 'W'
    piece_positions = [[3,4], [4,3], [3,3], [4,4]] # variable that keeps track of spots on board that has pieces on it
    return mat, piece_positions

# print the ASCII board
def draw_board(board):
    print('  A  B  C  D  E  F  G  H ')
    for i in range(len(board)):
        string = str(i + 1) + ''
        for j in range(len(board[0])):
            string += ' ' + str(board[i][j]) + ' '
        print(string)
    print()

# return the score of black and white respectively
def get_score(board, positions):
    qty_black = 0
    for i in range(len(positions)):
        if board[positions[i][0]][positions[i][1]] == 'B':
            qty_black += 1
    return [qty_black, len(positions) - qty_black]


def analyze_possible_moves(board, positions, color):
    op_color = 'W' if color == 'B' else 'B'
    moves_dict = {}
    # an array of vectors signifying the possible directions to move
    directions = [[-1,0], [1,0], [0,-1], [0,1], [-1,-1], [-1,1], [1,-1], [1,1]]
    marked_moves = [] # an array to store possible moves
    # determine the possible moves
    for coord in positions:
        row, col = coord[0], coord[1]
        if board[row][col] == color:
            for dir in directions:
                i = 1
                try:
                    while board[row + (i * dir[0])][col + (i * dir[1])] == op_color:
                        i += 1
                except:
                    continue
                if (row + i * dir[0]) < 0 or (col + i * dir[1]) < 0:
                    continue
                if  8 != (row + i * dir[0]) != -1 and -1 != (col + i * dir[1]) != 8 and i > 1:
                    if board[(row + i * dir[0])][(col + i * dir[1])] == ' ':
                        marked_moves.append([row + i * dir[0], col + i * dir[1]])
    # find all corresponding flips for each move
    for move in marked_moves:
        row, col = move[0], move[1]
        flipped = []
        for dir in directions:
            i = 1
            temp_flipped = []
            try:
                out_of_bounds = (row + i * dir[0]) < 0 or (col + i * dir[1]) < 0
                if out_of_bounds: continue
                while board[row + (i * dir[0])][col + (i * dir[1])] == op_color and not out_of_bounds:
                    temp_flipped.append([row + i * dir[0], col + i * dir[1]])
                    i += 1
                if  -1 < (row + i * dir[0]) < 8 and -1 < (col + i * dir[1]) < 8 and board[row + i * dir[0]][col + i * dir[1]] == color:
                    flipped.extend(temp_flipped)
            except:
                pass
        key = col_map[move[1]] + str(int(move[0] + 1))
        moves_dict[key] = flipped

    return moves_dict

# given a coordinate such as 'A5', return the vector representation
def coord_to_indices(coord):
    letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    return [int(coord[1]) - 1, letter_to_index[coord[0]]]

# return the heuristic: the difference in pieces between players +2 for each piece on the
# side of the board and +4 for corner pieces
def compute_heuristic(board, positions, root_color):
    color_count = 0
    count = 0
    for i in range(len(positions)):
        x, y = positions[i][0], positions[i][1]
        if board[positions[i][0]][positions[i][1]] == root_color:
            color_count += 1
            if x == 0 or x == 7:
                color_count += 2
            if y == 0 or y == 7:
                color_count += 2
        else:
            if x == 0 or x == 7:
                color_count -= 2
            if y == 0 or y == 7:
                color_count -= 2
        count += 1
    return color_count - (count - color_count)

# return a new board and position array given a move
def get_new_board_and_position(board, positions, color, move, flips):
    flips.append(coord_to_indices(move))
    positions.append(coord_to_indices(move))
    for flip in flips:
        board[flip[0]][flip[1]] = color
    return board, positions

# perform mini-max by building tree using BFS where object references are held in the matrix  ref_mat
def mini_max(board, position, depth, color, move_dict):
    global ref_mat
    ref_mat = [[] for j in range(11)] # matrix that holds all nodes of the tree
    ref_mat[0].append(Node(board, position, color, move_dict, par=None, lvl=0, depth=depth, move=None, root_color=color))
    # build the tree
    for i in range(depth+1):
        for j in range(len(ref_mat[i])):
            ref_mat[i][j].add_children(depth)
    # compute heuristic for leaf nodes
    for j in range(len(ref_mat[depth])):
        child = ref_mat[depth][j]
        child.heuristic = compute_heuristic(child.board, child.position, color)

    for i in range(depth,0,-1):
        for j in range(len(ref_mat[i])):
            heur = ref_mat[i][j].heuristic
            par_heur = ref_mat[i][j].par.heuristic
            if par_heur is None:
                ref_mat[i][j].par.heuristic = heur
                ref_mat[i][j].par.best_move = ref_mat[i][j].move
            else:
                if i % 2 == 1:
                    if heur > par_heur:
                        ref_mat[i][j].par.heuristic = heur
                        ref_mat[i][j].par.best_move = ref_mat[i][j].move
                else:
                    if heur < par_heur:
                        ref_mat[i][j].par.heuristic = heur
                        ref_mat[i][j].par.best_move = ref_mat[i][j].move

    '''additional debugging'''
    # for i in range(1, depth):
    #     print('lvl:', i)
    #     for j in range(len(ref_mat[i])):
    #         print('node: ', ref_mat[i][j].move, ' par move:', ref_mat[i][j].par.move, ' heur:', ref_mat[i][j].heuristic)
    #     print()

    best_move, heur_dict = None, {}
    for j in range(len(ref_mat[1])):
        cur = ref_mat[1][j]
        if best_move is None:
            best_move = cur.move
            best_heur = cur.heuristic
        if cur.heuristic > best_heur:
            best_move = cur.move
            best_heur = cur.heuristic
        heur_dict.update({cur.move: cur.heuristic})

    # print(best_move, heur_dict)

    return best_move, heur_dict

def play(players_arr, difficulty_arr):
    board, positions = board_init()
    count = 0
    no_move_counter = 0 # keep track of conesecutive times players cannot move
    debug = False
    while 1:
        move_index = count % 2
        color = 'B' if move_index == 0 else 'W'
        move_dict = analyze_possible_moves(board, positions, color)
        moves = [coord_to_indices(coord) for coord in move_dict.keys()]
        for move in moves:
            board[move[0]][move[1]] = '-'
        count += 1

        print('~' * 100)
        # determine if player has any moves
        if len(move_dict) == 0 and len(positions) != 64:
            no_move_counter += 1
            print('\nPlayer', players_arr[move_index] + ' can not move anywhere.')
        # determine if game is over (both players can't move or full board)
        if len(positions) == 64 or no_move_counter == 2:
            print('Game over!')
        else:
            print('\nIt is', players_arr[move_index] + '\'s turn to move as the color', color + '.')
        score = get_score(board, positions)
        print('\nScore:  ', players_arr[0], '(B) =', score[0], ' ', players_arr[1], '(W) =', score[1])
        draw_board(board)

        # continue if the player can't move, return if the game is over
        if len(positions) == 64 or no_move_counter == 2:
            return
        if len(move_dict) == 0:
            continue

        for move in moves:
            board[move[0]][move[1]] = ' '

        selected_move = ''
        if players_arr[move_index][:8] == 'Computer':
            # perform a random move if depth is set to 0
            if str(difficulty_arr[move_index]) == '0':
                selected_move = list(move_dict.keys())[random.randint(0, len(list(move_dict.keys())) - 1)]
            # perform mini max search if depth > 0
            else:
                try:
                    selected_move, heur_dict = mini_max(board, positions, int(difficulty_arr[move_index]), color, move_dict)
                except:
                    selected_move, heur_dict = list(move_dict.keys())[0], 'only 1 move left'
            if debug:
                print(str(players_arr[move_index]), 'selected the move:', str(selected_move) + ' of the possible moves given {move: heuristic pairs}: ' + str(heur_dict) + '.')
            else:
                print(str(players_arr[move_index]), 'selected the move:', str(selected_move) + '.')
        else:
            # prompt user to select move
            while selected_move not in list(move_dict.keys()):
                print('Enter \'D\' to toggle debug mode (to show heuristic values for all posible modes or a number from 0 to 4 '
                      'to change the difficulty of the computer (current difficulty: ' + str(difficulty_arr[0]) + ')')
                if debug and players_arr[move_index][:8] == 'Computer':
                    not_used, heur_dict = mini_max(board, positions, int(difficulty_arr[move_index]), color, move_dict)
                    selected_move = input('... or select one of the possible moves given {move: heuristic pairs}: ' + str(heur_dict) + ': ')
                else:
                    selected_move = input('... or select one of the possible moves: ' + str(list(move_dict.keys())) + ': ')
                try:
                    if type(int(selected_move)) == int:
                        if -1 < int(selected_move) < 11:
                            print('Computer difficulty set to:', str(selected_move))
                            difficulty_arr[0] = int(selected_move)
                except:
                    if str(selected_move) == 'D':
                        debug = False if debug else True
                        print('Debug mode:', debug)
                print()

        board, positions = get_new_board_and_position(board, positions, color, selected_move, flips=move_dict[selected_move])

        no_move_counter = 0

# determine game type, the difficulty of the computer(s), and who moves first, then start the game
def main():
    game_type = ''
    print('Welcome to the game of Othello!')
    while not (game_type == '1' or game_type == '2' or game_type == '3'):
        game_type = str(input('Enter 1 for a player vs player game, 2 for player vs computer, or 3 for computer vs computer '))

    if game_type == '1' or game_type == '2':
        players = [str(input('Enter name for Player 1 '))]
    if game_type == '1':
        players.append(str(input('Enter name for Player 2 ')))
    elif game_type == '2':
        players.append('Computer')
    else:
        players = ['Computer1', 'Computer2']
    difficulty_arr = [-1, -1]
    if game_type == '2' or game_type == '3':
        accepted_inputs = [str(i) for i in range(11)]
        while len(difficulty_arr) == 0 or not difficulty_arr[0] in accepted_inputs:
            dif = str(input('Enter a difficulty for the computer from 0 (easiest) to 4 (hardest): '))
            if game_type == 2: difficulty_arr[0], difficulty_arr[1] = dif, dif
            else: difficulty_arr[0] = dif
    if game_type == '3':
        while len(difficulty_arr) == 1 or not difficulty_arr[1] in accepted_inputs:
            difficulty_arr[1] = str(input('Enter a difficulty for computer #2 from 0 (easiest) to 4 (hardest): '))
    if random.randint(0, 1) < 1:
        players_arr = [players[0], players[1]]
    else:
        players_arr = [players[1], players[0]]
    if game_type == 3:
        players_arr = ['Computer1', 'Computer2']

    print('By random draw,', players_arr[0], 'moves first!')
    play(players_arr, difficulty_arr)

main()

