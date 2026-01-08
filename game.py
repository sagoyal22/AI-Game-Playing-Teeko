import copy
import random

class TeekoPlayer:
    """ An object representation for an AI game player for the game Teeko.
    """
    pieces = ['b', 'r']
    max_depth = 3

    def __init__(self):
        """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.board = [[' ' for j in range(5)] for i in range(5)]
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def make_move(self, state):
        """ 
        TODO: Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """
        best_val = float('-inf')
        best_moves = []

        successors = self.succ(state, self.my_piece)

        for succ_state, move in successors:
            val = self.min_value(succ_state, 1)

            if val > best_val:
                best_val = val
                best_moves = [move]
            elif val == best_val:
                best_moves.append(move)

        move = random.choice(best_moves) if best_moves else None
        return move



    def succ(self, state, my_piece): 
        """
        TODO: Generate a list of valid successors for the current game state 
        on placing your piece. (defined by self.my_piece)
        """
        successors = []

        piece_count = sum(cell != ' ' for row in state for cell in row)
        drop_phase = piece_count < 8

        if drop_phase:
            for r in range(5):
                for c in range(5):
                    if state[r][c] == ' ':
                        new_state = copy.deepcopy(state)
                        new_state[r][c] = my_piece
                        move = [(r, c)]
                        successors.append((new_state, move))
        else:
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                ( 0, -1),          ( 0, 1),
                ( 1, -1), ( 1, 0), ( 1, 1)
            ]

            for r in range(5):
                for c in range(5):
                    if state[r][c] == my_piece:
                        for dr, dc in directions:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 5 and 0 <= nc < 5:
                                if state[nr][nc] == ' ':
                                    new_state = copy.deepcopy(state)
                                    new_state[r][c] = ' '
                                    new_state[nr][nc] = my_piece
                                    move = [(nr, nc), (r, c)]
                                    successors.append((new_state, move))

        return successors

    
    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    
    def heuristic_game_value(self, state):
        """ 
        TODO: Define the heuristic game value of the current board state taking into account players
        and opponents

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            float heuristic_val (heuristic computed for the game state)
        """

        gv = self.game_value(state)
        if gv != 0:
            return float(gv)

        def best_pattern_score(piece):
            best = 0

            def score_line(cells):
                nonlocal best
                if any(c == (self.opp if piece == self.my_piece else self.my_piece) for c in cells):
                    return
                count = sum(1 for c in cells if c == piece)
                best = max(best, count)

            # 4-cell lines horizontal
            for r in range(5):
                for c in range(5 - 3):
                    score_line([state[r][c + k] for k in range(4)])

            # vertical
            for c in range(5):
                for r in range(5 - 3):
                    score_line([state[r + k][c] for k in range(4)])

            # diag down-right
            for r in range(5 - 3):
                for c in range(5 - 3):
                    score_line([state[r + k][c + k] for k in range(4)])

            # diag up-right
            for r in range(3, 5):
                for c in range(5 - 3):
                    score_line([state[r - k][c + k] for k in range(4)])

            # 2x2 boxes 
            for r in range(5 - 1):
                for c in range(5 - 1):
                    cells = [
                        state[r][c], state[r][c + 1],
                        state[r + 1][c], state[r + 1][c + 1]
                    ]
                    score_line(cells)

            return best

        my_best = best_pattern_score(self.my_piece)
        opp_best = best_pattern_score(self.opp)

        heuristic_val = (my_best - opp_best) / 4.0
        return heuristic_val
 
    def game_value(self, state):
        """ 
        TODO: Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner
        """
        
        def has_win(piece):
            for r in range(5):
                for c in range(5 - 3): 
                    if all(state[r][c + k] == piece for k in range(4)):
                        return True

            for c in range(5):
                for r in range(5 - 3):  
                    if all(state[r + k][c] == piece for k in range(4)):
                        return True

            for r in range(5 - 3):      
                for c in range(5 - 3):  
                    if all(state[r + k][c + k] == piece for k in range(4)):
                        return True

            for r in range(3, 5):      
                for c in range(5 - 3):  
                    if all(state[r - k][c + k] == piece for k in range(4)):
                        return True

            for r in range(5 - 1):    
                for c in range(5 - 1):  
                    if (state[r][c] == piece and state[r][c + 1] == piece and
                        state[r + 1][c] == piece and state[r + 1][c + 1] == piece):
                        return True

            return False

        if has_win(self.my_piece):
            return 1
        if has_win(self.opp):
            return -1
        return 0  

    
    def max_value(self, state, depth):
        """
        TODO: Complete the helper function to implement min-max as described in the writeup
        """
        gv = self.game_value(state)
        if gv != 0 or depth == self.max_depth:
            return float(gv) if gv != 0 else self.heuristic_game_value(state)

        v = float('-inf')
        successors = self.succ(state, self.my_piece)

        if not successors:
            return self.heuristic_game_value(state)

        for succ_state, _ in successors:
            v = max(v, self.min_value(succ_state, depth + 1))
        return v
    
    def min_value(self, state, depth):
        """
        MIN player (the opponent) in minimax.
        """
        gv = self.game_value(state)
        if gv != 0 or depth == self.max_depth:
            return float(gv) if gv != 0 else self.heuristic_game_value(state)

        v = float('inf')
        successors = self.succ(state, self.opp)

        if not successors:
            return self.heuristic_game_value(state)

        for succ_state, _ in successors:
            v = min(v, self.max_value(succ_state, depth + 1))
        return v



############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()
