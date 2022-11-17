import tkinter as tk
from tkinter import ttk



class popup_question():
    '''
    Simple popup box to ask a question with two possible answers.
    Two possible answers can be specified.
    Once the popup is closed, callback is called with the answer as paramteter.

    Parameters
    ----------
    callback: function with one input parameter
        Called if any answer is chosen.
        True if left button is pressed, False if right button is pressed.
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

    '''
    
        
    def __init__(self, callback, title, question, answer_true, answer_false):
        self.popup = tk.Toplevel()
        self.popup.title(title)
        self.popup.protocol("WM_DELETE_WINDOW", self.true_pressed)
        self.callback = callback
        self.answer = None
        label = ttk.Label(self.popup, text=question, width=60, wraplength=340)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(self.popup, text=answer_true, command=self.true_pressed)
        B1.pack(side="left", padx=10, pady=10)
        B2 = ttk.Button(self.popup, text=answer_false, command=self.false_pressed)
        B2.pack(side="right", padx=10, pady=10)
        self.popup.mainloop()    
    
    def true_pressed(self):
        self.popup.destroy()
        self.callback(True)
        
    def false_pressed(self):
        self.popup.destroy()
        self.callback(False)
    
    def cancelled(self):
        self.popup.destroy()
