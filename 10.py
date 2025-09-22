import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Крестики-нолики")
        self.board = [' ' for i in range(9)]
        self.current_player = 'X'
        self.buttons = []
        
        for i in range(3):
            for j in range(3):
                button = tk.Button(self.window, text='', font=('Arial', 20), width=5, height=2,
                                 command=lambda row=i, col=j: self.make_move(row, col))
                button.grid(row=i, column=j)
                self.buttons.append(button)
    
    def make_move(self, row, col):
        index = 3 * row + col
        if self.board[index] == ' ' and self.current_player == 'X':
            self.board[index] = 'X'
            self.buttons[index].config(text='X', state='disabled')
            
            if not self.check_winner():
                self.current_player = 'O'
                self.bot_move()
    
    def bot_move(self):
        best_score = float('-inf')
        best_move = None
        
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O'
                score = self.minimax(self.board, 0, False)
                self.board[i] = ' '
                
                if score > best_score:
                    best_score = score
                    best_move = i
        
        if best_move is not None:
            self.board[best_move] = 'O'
            self.buttons[best_move].config(text='O', state='disabled')
            self.check_winner()
            self.current_player = 'X'
    
    def minimax(self, board, depth, is_maximizing):
        scores = {'X': -1, 'O': 1, 'tie': 0}
        
        winner = self.check_winner_minimax(board)
        if winner:
            return scores[winner]
        
        if is_maximizing:
            best_score = float('-inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'O'
                    score = self.minimax(board, depth + 1, False)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'X'
                    score = self.minimax(board, depth + 1, True)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score
    
    def check_winner_minimax(self, board):
        # Проверка строк
        for i in range(0, 9, 3):
            if board[i] == board[i+1] == board[i+2] != ' ':
                return board[i]
        
        # Проверка столбцов
        for i in range(3):
            if board[i] == board[i+3] == board[i+6] != ' ':
                return board[i]
        
        # Проверка диагоналей
        if board[0] == board[4] == board[8] != ' ':
            return board[0]
        if board[2] == board[4] == board[6] != ' ':
            return board[2]
        
        # Проверка на ничью
        if ' ' not in board:
            return 'tie'
        
        return None
    
    def check_winner(self):
        winner = self.check_winner_minimax(self.board)
        
        if winner == 'X':
            messagebox.showinfo("Победа!", "Вы победили!")
            self.reset_game()
            return True
        elif winner == 'O':
            messagebox.showinfo("Поражение", "Бот победил!")
            self.reset_game()
            return True
        elif winner == 'tie':
            messagebox.showinfo("Ничья", "Игра закончилась вничью!")
            self.reset_game()
            return True
        
        return False
    
    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        for button in self.buttons:
            button.config(text='', state='normal')
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = TicTacToe()
    game.run()
