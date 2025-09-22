import tkinter as tk
from tkinter import messagebox
okno = tk.Tk()
board = [' ' for i in range(9)]
current_player = 'X'
buttons = []

def create_board():
    """Создание игрового поля"""
    okno.title("Крестики-нолики")
    
    for i in range(3):
        for j in range(3):
            index = 3 * i + j
            button = tk.Button(okno, text='', font=('Arial', 20), width=5, height=2,
                             command=lambda idx=index: make_move(idx))
            button.grid(row=i, column=j)
            buttons.append(button)

def make_move(index):
    """Ход игрока"""
    global current_player
    
    if board[index] == ' ' and current_player == 'X':
        board[index] = 'X'
        buttons[index].config(text='X', state='disabled')
        
        if not check_winner():
            current_player = 'O'
            bot_move()

def bot_move():
    """Ход бота"""
    global current_player
    
    best_score = float('-inf')
    best_move = None
    
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            score = minimax(board, 0, False)
            board[i] = ' '
            
            if score > best_score:
                best_score = score
                best_move = i
    
    if best_move is not None:
        board[best_move] = 'O'
        buttons[best_move].config(text='O', state='disabled')
        check_winner()
        current_player = 'X'

def minimax(board, depth, is_maximizing):
    """Алгоритм минимакс для поиска лучшего хода"""
    scores = {'X': -1, 'O': 1, 'tie': 0}
    
    winner = check_winner_minimax(board)
    if winner:
        return scores[winner]
    
    if is_maximizing:
        best_score = float('-inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                score = minimax(board, depth + 1, False)
                board[i] = ' '
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                score = minimax(board, depth + 1, True)
                board[i] = ' '
                best_score = min(score, best_score)
        return best_score

def check_winner_minimax(board):
    """Проверка победителя для алгоритма минимакс"""
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

def check_winner():
    """Проверка победителя в основной игре"""
    winner = check_winner_minimax(board)
    
    if winner == 'X':
        messagebox.showinfo("Победа!", "Вы победили!")
        reset_game()
        return True
    elif winner == 'O':
        messagebox.showinfo("Поражение", "Бот победил!")
        reset_game()
        return True
    elif winner == 'tie':
        messagebox.showinfo("Ничья", "Игра закончилась вничью!")
        reset_game()
        return True
    
    return False

def reset_game():
    """Сброс игры"""
    global board, current_player
    
    board = [' ' for i in range(9)]
    current_player = 'X'
    
    for button in buttons:
        button.config(text='', state='normal')

def main():
    """Основная функция"""
    create_board()
    okno.mainloop()

if __name__ == "__main__":
    main()


