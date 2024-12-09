import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
import time
import os
from tkinter import Canvas

colors = {
    0:"white",
    1:"#2e34e5",
    2:"#12b32d",
    3:"#c42121",
    4:"#0905fc",
    5:"#c5e016",
    6:"#7111f0",
    7:"#f011cb",
    8:"#11e1f0",
}

class MyButton(tk.Button):
    
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font=("Arial", 12, "bold"), *args, **kwargs)
        self.x=x
        self.y=y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False
    
    def __repr__(self):
        return f'MyButton{self.x} {self.y} {self.number} {self.is_mine}'
    
    
class MineSweeper:
    
    window = tk.Tk()
    ROW = 10
    COLUMNS = 10
    MINES = 7
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    IS_PAUSED = False
    
    def __init__(self):
        MineSweeper.window.title("Minesweeper")
        self.window.config(bg="lightblue")
        self.scores = []
        self.buttons = []
        for i in range(MineSweeper.ROW+2):
            temp = []
            for j in range(MineSweeper.COLUMNS+2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
        self.timer_label = tk.Label(MineSweeper.window, text="Уақыт: 0")
        self.timer_label.grid(row=0, column=0, columnspan=MineSweeper.COLUMNS // 2)
        self.flags_label = tk.Label(MineSweeper.window, text=f"Белгілер: {MineSweeper.MINES}")
        self.flags_label.grid(row=0, column=MineSweeper.COLUMNS // 2, columnspan=MineSweeper.COLUMNS // 2)
        self.start_time = None
        self.flags_left = MineSweeper.MINES
        self.update_timer()

    def record_time(self):
        if MineSweeper.IS_GAME_OVER and self.start_time is not None:
            elapsed_time = int(time.time() - self.start_time)
            self.save_score(elapsed_time)

    def save_score(self, score):
        if not os.path.exists("scores.txt"):
            with open("scores.txt", "w") as file:
                file.write(f"{score}\n")
        else:
            with open("scores.txt", "a") as file:
                file.write(f"{score}\n")
        self.load_scores()

    def load_scores(self):
        if os.path.exists("scores.txt"):
            with open("scores.txt", "r") as file:
                self.scores = sorted([int(line.strip()) for line in file.readlines() if line.strip().isdigit()])
        else:
            self.scores = []

    def show_scores(self):
        scores_window = tk.Toplevel(self.window)
        scores_window.wm_title("Үздік нәтижелер")
        tk.Label(scores_window, text="Үздік нәтижелер").grid(row=0, column=0, padx=10, pady=10)
        for i, score in enumerate(self.scores):
            tk.Label(scores_window, text=f"{i+1}. {score} секунд").grid(row=i+1, column=0, padx=10, pady=5)

    def update_timer(self):
        if not MineSweeper.IS_GAME_OVER and not MineSweeper.IS_PAUSED and self.start_time is not None:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Уақыт: {elapsed_time}")
            MineSweeper.window.after(1000, self.update_timer)
    
    def right_click(self, event):
        if MineSweeper.IS_GAME_OVER:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground'] = 'red'
            self.flags_left -= 1
        elif cur_btn['text'] == '🚩':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'
            self.flags_left += 1
        self.flags_label.config(text=f"Белгілер: {self.flags_left}")
     
    def check_win(self):
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if not btn.is_mine and not btn.is_open:
                    return
        MineSweeper.IS_GAME_OVER = True
        self.open_all_buttons()
        showinfo("Win!", "Сіз жеңдіңіз!")             
                   
    def click(self, clicked_button: MyButton):
        if MineSweeper.IS_GAME_OVER or MineSweeper.IS_PAUSED:
            return None 
   
        if MineSweeper.IS_FIRST_CLICK:
            self.start_time = time.time()
            self.update_timer()  
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            MineSweeper.IS_FIRST_CLICK = False
        
        if clicked_button.is_mine:
            clicked_button.config(text='💣', background='red', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over', 'Сіз жеңілдіңіз!')
            for i in range(1, MineSweeper.ROW+1):
                for j in range(1, MineSweeper.COLUMNS+1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '💣'
        else:
            color = colors.get(clicked_button.count_bomb, "black")
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)
        self.check_win()
        
    def toggle_pause(self):
        if MineSweeper.IS_PAUSED:
            MineSweeper.IS_PAUSED = False
            self.update_timer() 
            showinfo("Кідірту", "Ойын басталды!")
        else:
            MineSweeper.IS_PAUSED = True
            showinfo("Кідірту", "Ойын тоқтатылды!")
    
    def give_hint(self):
        if MineSweeper.IS_GAME_OVER or MineSweeper.IS_PAUSED:
            return
        safe_buttons = []
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if not btn.is_mine and not btn.is_open:
                    safe_buttons.append(btn)
        if safe_buttons:
            hint_button = safe_buttons[0] 
            self.click(hint_button)  
            self.hint_button.config(state="disabled")  
            showinfo("Көмек", "Бос ұяшық ашылды.")
        else:
            showinfo("Көмек", "Бос ұяшықтар жоқ.")
    
    def open_button_with_effect(btn):
        btn.config(state="disabled", relief=tk.SUNKEN)
        btn.config(text=btn.count_bomb)
        btn.update_idletasks() 
        for i in range(10):
            color = f"#{hex(255 - i * 25)[2:].zfill(2)}{hex(i * 25)[2:].zfill(2)}00"
            btn.config(bg=color)
            time.sleep(0.05)
            btn.update_idletasks()

    def breadth_first_search(self, btn:MyButton):
        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground= color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state='disabled')
            cur_btn.config(relief=tk.SUNKEN)
            if cur_btn.count_bomb == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[x+dx][y+dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.ROW and \
                                1 <= next_btn.y <= MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)
                            
    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False
    
    def create_settings_window(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Параметрлер')
        tk.Label(win_settings, text='Жолдардың саны').grid(row = 0, column = 0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Бағандардың саны').grid(row = 1, column = 0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Миналардың саны').grid(row = 2, column = 0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        save_btn = tk.Button(win_settings, text='Қабылдау', command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
    def change_settings(self, row:tk.Entry, column:tk.Entry, mines:tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Қателік', 'Сан енгізіңіз!')
            return
        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        self.reload()        
    
    def create_widgets(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Кідірту', command=self.toggle_pause)
        settings_menu.add_command(label='Қайта ойнау', command = self.reload)
        settings_menu.add_command(label='Параметрлер', command = self.create_settings_window)
        settings_menu.add_command(label="Ең үздік нәтижелер", command=self.show_scores)
        settings_menu.add_command(label='Шығу', command = self.window.destroy)
        menubar.add_cascade(label='Мәзір', menu=settings_menu)    
        self.hint_button = tk.Button(self.window, text="Көмек", command=self.give_hint)
        self.hint_button.grid(row=0, column=MineSweeper.COLUMNS + 1, padx=10, pady=10)    
        count = 1
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick = 'NWES')
                count += 1
        for i in range(1, MineSweeper.ROW+1):
            tk.Grid.rowconfigure(self.window, i, weight = 1)
        for i in range(1, MineSweeper.COLUMNS+1):
            tk.Grid.columnconfigure(self.window, i, weight = 1)
    
    def open_all_buttons(self):
        for i in range(MineSweeper.ROW+2):
            for j in range(MineSweeper.COLUMNS+2):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text='*', background='red', disabledforeground='black')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, "black")
                    btn.config(text=btn.count_bomb, fg = color)
                   
    def start(self):
        self.create_widgets()
        MineSweeper.window.mainloop()
                    
    def insert_mines(self, number:int):
        index_mines = self.get_mines_places(number)
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
         for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neigbour = self.buttons[i + row_dx][j + col_dx]
                            if neigbour.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb    
            
    @staticmethod
    def get_mines_places(exclude_number:int):
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSweeper.MINES]
       
game = MineSweeper()
game.start()
