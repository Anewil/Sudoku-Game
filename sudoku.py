from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM
import argparse

BOARDS_NAMES = ['test']  # Names of sudoku boards
MARGIN = 20  # Margin around the board
CELL = 50  # Edge of cell
WIDTH = HEIGHT = MARGIN * 2 + CELL * 9  # Width and height of the whole board

class SudokuError(Exception):
    pass


class SudokuBoard:
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        board = []
        for line in board_file:
            line = line.strip()

            if len(line) != 9:
                board = []
                raise SudokuError("Each line in the sudoku puzzle must be 9 chars long")

            board.append([])

            for c in line:
                if not c.isdigit():
                    raise SudokuError("The char must be a digit")

                board[-1].append(int(c))

        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")

        return board

class SudokuGame:
    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def check_win(self):
        for i in range(9):
            if not self.__check_row(i):
                return False
            if not self.__check_column(i):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_box(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block([self.puzzle[row][column] for row in range(9)])

    def __check_box(self, row, column):
        return self.__check_block([self.puzzle[r][c]
                                   for r in range(row * 3, (row + 1) * 3)
                                   for c in range(column * 3, (column + 1) * 3)])



class SudokuUI(Frame):
    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.row = 0
        self.col = 0

        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             heigh=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self,
                              text="Clear answers",
                              command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        for i in range(10):
            if i % 3 == 0:
                color = "blue"
            else:
                color = "gray"

            x0 = MARGIN + i * CELL
            y0 = MARGIN
            x1 = MARGIN + i * CELL
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * CELL
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * CELL
            self.canvas.create_line(x0, y0, x1, y1, fill=color)


    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * CELL + CELL / 2
                    y = MARGIN + i * CELL + CELL / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            row, col = int((y - MARGIN) / CELL), int((x - MARGIN) / CELL)

            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col

        self.__draw_cursor()

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * CELL + 1
            y0 = MARGIN + self.row * CELL + 1
            x1 = MARGIN + (self.col + 1) * CELL - 1
            y1 = MARGIN + (self.row + 1) * CELL - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __draw_victory(self):
        x0 = y0 = MARGIN + CELL * 2
        x1 = y1 = MARGIN + CELL * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="blue"
        )

        x = y = MARGIN + 4 * CELL + CELL / 2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="winner",
            fill="white", font=("Arial", 32)
        )


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS_NAMES,
                            required=True)

    args = vars(arg_parser.parse_args())
    return args['board']


if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()