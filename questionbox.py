import tkinter as tk
from tkinter import ttk

def popup_question(title, question, answer_true='Yes', answer_false='No'):
    '''
    Simple popup box to ask a question and return back the answer.
    Two possible answers can be specified.

    Parameters
    ----------
    title : str
        Title of the popup window.
    question : str
        Main text of the popup window.
    answer_true : str
        Caption of the left button.
        The method returns True if this button is pressed.
    answer_false : str
        Caption of the left button.
        The method returns True if this button is pressed.

    Returns
    -------
    answer : bool or NoneType
        True if left button is pressed, False if right button is pressed.
        None if the window is exited otherwise.

    '''
    
    window = _popup_window(title, question, answer_true, answer_false)
    answer = window.answer
    return answer
    
    

class _popup_window():
    
        
    def __init__(self, title, question, answer_true, answer_false):
        self.popup = tk.Tk()
        self.popup.wm_title(title)
        self.answer = None
        label = ttk.Label(self.popup, text=question)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(self.popup, text=answer_true, command = self.true_pressed)
        B1.pack(side="left", padx=10, pady=10)
        B2 = ttk.Button(self.popup, text=answer_false, command = self.false_pressed)
        B2.pack(side="right", padx=10, pady=10)
        self.popup.mainloop()    
    
    def true_pressed(self):
        self.popup.destroy()
        self.answer = True
        
    def false_pressed(self):
        self.popup.destroy()
        self.answer = False
    
print(popup_question('aaaaaaaaaaaaaaaaaaaaaaa', 'b', 'c', 'd'))
