from settings import SANTEC_SLM, slm_size, bit_depth
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.messagebox  as tkMbox
import numpy as np
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import os
import phase_settings
import preview_window
if SANTEC_SLM: import santec_driver._slm_py as slm
else:          import publish_window
import feedbacker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")



class main_screen(object):
    """"""

    def __init__(self, parent):
        """Constructor"""
        self.main_win = parent
        self.main_win.title('SLM Phase Control')

        self.main_win.columnconfigure(0, minsize=250, weight=1)
        self.main_win.rowconfigure(2, minsize=100, weight=1)
        self.pub_win = None
        self.prev_win = None
        self.phase_map = np.zeros(slm_size)

        # creating frames
        frm_top = tk.Frame(self.main_win)
        self.frm_mid = ttk.Notebook(self.main_win)
        frm_bot = tk.Frame(self.main_win)
        frm_topb = tk.Frame(frm_top)
        self.frm_side = tk.Frame(self.main_win)

        # Creating labels
        lbl_title = tk.Label(
            self.main_win,
            text='Control Phase',
            font=tkFont.Font(family='Lucida Grande', size=20))
        if SANTEC_SLM:
            lbl_screen = tk.Label(frm_top, text='SLM display number:')
        else:
            lbl_screen = tk.Label(frm_top, text='SLM screen position:')

        # Creating buttons
        but_fbck = tk.Button(frm_bot, text='Feedbacker', command=self.open_fbck)
        but_prev = tk.Button(frm_bot, text='Preview', command=self.open_prev)
        but_pub = tk.Button(frm_bot, text='Publish', command=self.open_pub)
        but_exit = tk.Button(frm_bot, text='EXIT', command=self.exit_prog)
        but_save = tk.Button(frm_topb, text='Save Settings', command=self.save)
        but_load = tk.Button(frm_topb, text='Load Settings', command=self.load)

        # Creating entry
        if SANTEC_SLM:
            self.ent_scr = tk.Spinbox(frm_top, width=5, from_=1, to=8)
        else:
            self.ent_scr = tk.Entry(frm_top, width=15)
            self.ent_scr.insert(tk.END, '+right+down')

        # Setting up general structure
        lbl_title.grid(row=0, column=0, sticky='ew')
        frm_top.grid(row=2, column=0, sticky='ew')
        self.frm_mid.grid(row=1, column=0, sticky='nsew')
        frm_bot.grid(row=4, column=0)
        self.frm_side.grid(row=3, column=0, sticky='nsew')

        # Setting up top frame
        lbl_screen.grid(row=0, column=0, sticky='e', padx=10, pady=10)
        self.ent_scr.grid(row=0, column=1, sticky='w', padx=(0, 10))
        self.setup_box(frm_top)  # sets up the checkboxes separately
        frm_topb.grid(row=1, column=1, sticky='nsew')
        but_save.grid(row=0, padx=5, pady=5)
        but_load.grid(row=1, padx=5)

        # Setting up scan and phase figure
        self.scan_options()
        self.fig = Figure(figsize=(2, 1.5), dpi=130)
        self.ax1 = self.fig.add_subplot(111)
        self.img1 = FigureCanvasTkAgg(self.fig, frm_topb)
        self.tk_widget_fig = self.img1.get_tk_widget()
        self.tk_widget_fig.grid(row=2, sticky='ew')

        self.ax1.axes.xaxis.set_visible(False)
        self.ax1.axes.yaxis.set_visible(False)

        # Setting up bot frame
        but_fbck.grid(row=0, column=0, padx=5, ipadx=5)
        but_prev.grid(row=0, column=1, padx=5, pady=5, ipadx=5)
        but_pub.grid(row=0, column=2, pady=5, ipadx=5)
        but_exit.grid(row=0, column=3, padx=10, pady=5, ipadx=5)

        # binding keys
        def lefthandler(event): return self.left_arrow()
        self.main_win.bind('a', lefthandler)
        def righthandler(event): return self.right_arrow()
        self.main_win.bind('d', righthandler)
        def uphandler(event): return self.up_arrow()
        self.main_win.bind('w', uphandler)
        def downhandler(event): return self.down_arrow()
        self.main_win.bind('s', downhandler)
        def escapehandler(event): return self.escape_key()
        self.main_win.bind('<Escape>', escapehandler)

        # loading last settings
        self.load('./last_settings.txt')

    def open_fbck(self):
        self.fbcker = feedbacker.feedbacker(self)

    def open_prev(self):
        if self.prev_win is not None:
            self.prev_win.update_plots()
        else:
            self.prev_win = preview_window.prev_screen(self)

    def prev_win_closed(self):
        print('prev closed')
        self.prev_win = None

    def open_pub(self):
        self.ent_scr.config(state='disabled')
        self.phase_map = self.get_phase()
        if SANTEC_SLM: # Santec SLM Dispay routine
            self.pub_win = int(self.ent_scr.get())
            slm.SLM_Disp_Open(int(self.ent_scr.get()))
            slm.SLM_Disp_Data(int(self.ent_scr.get()), self.phase_map,
                              slm_size[1], slm_size[0])
        else: # Hamamatsu SLM Display routine
            if self.pub_win is not None:
                self.pub_win.update_img(self.phase_map)
            else:
                self.pub_win = publish_window.pub_screen(
                    self, self.ent_scr.get(), self.phase_map)
        self.update_phase_plot(self.phase_map)

    def do_scan(self):
        if self.strvar_delay.get() == '':
            self.strvar_delay.set('1')
        delay = float(self.strvar_delay.get())
        filelist = self.load_filelist()
        var = tk.IntVar()

        for filepath in filelist:
            if self.var_stop_scan.get():
                self.var_stop_scan.set(0)
                return
            root.after(int(delay*1000), var.set, 1)
            self.load(filepath)

            # keeps to one window and updates for each filepath
            self.open_pub()

            self.lbl_time['text'] = delay
            self.countdown()
            root.wait_variable(var)

    def countdown(self):
        self.lbl_time['text'] = int(self.lbl_time['text']) - 1
        if int(self.lbl_time['text']):
            self.lbl_time.after(1000, self.countdown)

    def pub_win_closed(self):
        self.ent_scr.config(state='normal')
        if SANTEC_SLM:
            slm.SLM_Disp_Close(int(self.ent_scr.get()))
        self.pub_win = None

    def setup_box(self, frm_):
        frm_box = tk.LabelFrame(frm_, text='Phases enabled')
        frm_box.grid(column=0)
        self.types = phase_settings.types  # reads in  different phase types
        self.vars = []  # init a list holding the variables from the boxes
        self.phase_refs = []  # init a list to hold the references to types
        self.tabs = []  # init a list to hold the tabs
        for ind, typ in enumerate(self.types):
            self.var_ = (tk.IntVar())
            self.vars.append(self.var_)
            self.tabs.append(ttk.Frame(self.frm_mid))
            self.frm_mid.add(self.tabs[ind], text=typ)
            self.phase_refs.append(phase_settings.new_type(self.tabs[ind],
                                                           typ))
            self.box_ = tk.Checkbutton(frm_box, text=typ,
                                       variable=self.vars[ind],
                                       onvalue=1, offvalue=0)
            self.box_.grid(row=ind, sticky='w')


    def get_phase(self):
        '''gets the phase from the active phase types'''
        phase = np.zeros(slm_size)
        for ind, phase_types in enumerate(self.phase_refs):
            if self.vars[ind].get() == 1:
                print(phase_types)
                phase += phase_types.phase()
        return phase

    def save(self, filepath=None):
        """Save the current settings as a new file."""
        if filepath is None:
            filepath = asksaveasfilename(
                defaultextension='txt',
                filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
            )
            if not filepath:
                return
        dict = {}
        with open(filepath, 'w') as f:
            for num, phase in enumerate(self.phase_refs):
                dict[phase.name_()] = {'Enabled': self.vars[num].get(),
                                       'Params': phase.save_()}
            dict['screen_pos'] = self.ent_scr.get()
            f.write(json.dumps(dict))

    def load(self, filepath=None):
        if filepath is None:
            filepath = askopenfilename(
                filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
            )
            if not filepath:
                return
        try:
            with open(filepath, 'r') as f:
                dics = json.loads(f.read())
            try:
                for num, phase in enumerate(self.phase_refs):  # loading
                    phase.load_(dics[phase.name_()]['Params'])
                    self.vars[num].set(dics[phase.name_()]['Enabled'])
                self.ent_scr.delete(0, tk.END)
                self.ent_scr.insert(0, dics['screen_pos'])
            except ValueError:
                print('Not able to load settings')
        except FileNotFoundError:
            print(f'No settings file found at {filepath}')

    def scan_options(self):
        self.so_frm = tk.LabelFrame(self.frm_side, text='Scan options')
        self.so_frm.grid(row=0, sticky='nsew')

        # creating frames
        frm_file = tk.Frame(self.so_frm)

        # creating labels
        lbl_scpar = tk.Label(self.so_frm, text='Scan parameter')
        lbl_val = tk.Label(self.so_frm, text='Value (strt:stop:num)')
        lbl_actf = tk.Label(frm_file, text='Active file:')
        self.lbl_file = tk.Label(frm_file, text='', wraplength=230,
                                 justify='left', foreground='gray')
        lbl_delay = tk.Label(
            self.so_frm, text='Delay between each phase [s]:')
        self.lbl_time = tk.Label(self.so_frm, text='0')

        # creating entries
        self.cbx_scpar = ttk.Combobox(
            self.so_frm, values=['Select'], postcommand=self.scan_params)
        self.cbx_scpar.current(0)
        vcmd = (self.frm_side.register(self.callback))
        self.strvar_val = tk.StringVar()
        ent_val = tk.Entry(self.so_frm,  width=10,  validate='all',
                           validatecommand=(vcmd, '%d', '%P', '%S'),
                           textvariable=self.strvar_val)
        self.strvar_delay = tk.StringVar()
        ent_delay = tk.Entry(self.so_frm, width=5, validate='all',
                             validatecommand=(vcmd, '%d', '%P', '%S'),
                             textvariable=self.strvar_delay)

        # creating buttons
        self.but_crt = tk.Button(
            self.so_frm, text='Create loading file',
            command=self.create_loadingfile)
        but_openload = tk.Button(
            self.so_frm, text='Open existing loading file',
            command=self.open_loadingfile)
        self.but_scan = tk.Button(
            self.so_frm, text='Scan', command=self.do_scan)
        but_stop_scan = tk.Button(
            self.so_frm, text='Stop scan', command=self.stop_scan)
        self.var_stop_scan = tk.IntVar(value=0)

        # setup
        frm_file.grid(row=3, sticky='w', columnspan=3)
        self.but_crt.grid(row=2, column=0, sticky='ew')
        but_openload.grid(row=2, column=1, columnspan=2, sticky='ew')


        self.but_scan.grid(row=5, column=0, padx=5, pady=5)
        but_stop_scan.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        lbl_scpar.grid(row=0, column=0, sticky='e')
        lbl_val.grid(row=1, column=0, sticky='e')
        self.cbx_scpar.grid(row=0, column=1, columnspan=2, sticky='w')
        ent_val.grid(row=1, column=1, columnspan=2, sticky='w')

        lbl_actf.grid(row=3, column=0)
        self.lbl_file.grid(row=3, column=1)

        lbl_delay.grid(row=4, column=0, sticky='e')
        ent_delay.grid(row=4, column=1, columnspan=2, sticky='w')
        self.lbl_time.grid(row=4, column=2, sticky='w')

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+:':
                return True
            else:
                return False
        else:
            return True

    def scan_params(self):
        scparams = []
        for ind, phase in enumerate(self.phase_refs):
            if self.vars[ind].get() == 1:
                phparam = phase.save_()
                for param in phparam.keys():
                    scparams.append(phase.name_() + ':' + param)
        self.cbx_scpar['values'] = scparams
        return

    def create_loadingfile(self):
        if self.strvar_val.get() != '':
            strval = self.strvar_val.get()
            listval = strval.split(':', 3)
            try:
                strt = float(listval[0])
                stop = float(listval[1])
                num = int(listval[2])
                val_range = np.around(np.linspace(strt, stop, num), decimals=3)
            except (ValueError, IndexError) as err:
                self.but_crt['text'] = f'Create loading file : {err}'
                return

        else:
            print('Empty value')
            return
        print(f'{strt}_{stop}_{num}')

        cwd = os.getcwd()
        print('cwd is {}'.format(cwd))
        dirstr = '\\SLM_phase_scan_files'
        if not os.path.exists(cwd + dirstr):
            os.mkdir(cwd + dirstr)
        # create folder
        scparam = self.cbx_scpar.get().split(':')
        folder_str = '\\{}_{}_{}_{}_{}'.format(
            scparam[0], scparam[1], strt, stop, num)
        cwd = cwd + dirstr + folder_str
        if not os.path.exists(cwd):
            os.mkdir(cwd)

        # create file for filepaths
        ind = self.types.index(scparam[0])
        param_dic = self.phase_refs[ind].save_()
        with open(cwd + '\\' + 'filepaths.txt', 'w') as logfile:
            for val in val_range:
                param_dic[scparam[1]] = val
                self.phase_refs[ind].load_(param_dic)
                filepath = f'{cwd}\\{val:.3f}.txt'
                print(filepath)
                self.save(filepath)
                logfile.write(filepath + '\n')
        self.lbl_file['text'] = cwd + '\\' + 'filepaths.txt'

        self.but_crt['text'] = 'Create loading file : OK'
        return

    def open_loadingfile(self):
        filepath = askopenfilename(
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        if not filepath:
            return
        self.lbl_file['text'] = f'{filepath}'
        return

    def load_filelist(self):
        filelistpath = self.lbl_file['text']
        with open(filelistpath, 'r') as f:
            text = f.read()
            stringlist = text.split('\n')
            return stringlist[0:-1]

    def stop_scan(self):
        self.var_stop_scan.set(1)
        return

    def left_arrow(self):
        if self.vars[2].get() == 1:
            self.phase_refs[2].left_()
            self.open_pub()
            self.main_win.after(500, self.main_win.focus_force)

    def right_arrow(self):
        if self.vars[2].get() == 1:
            self.phase_refs[2].right_()
            self.open_pub()
            self.main_win.after(500, self.main_win.focus_force)

    def up_arrow(self):
        if self.vars[2].get() == 1:
            self.phase_refs[2].up_()
            self.open_pub()
            self.main_win.after(500, self.main_win.focus_force)

    def down_arrow(self):
        print('s pressed')
        if self.vars[2].get() == 1:
            self.phase_refs[2].down_()
            self.open_pub()
            self.main_win.after(500, self.main_win.focus_force)
    
    def escape_key(self):
        print('esc pressed')
        if self.pub_win is not None:
            q_str = 'Do you want to close the SLM Publication Window?\nThe SLM screen will instead show the desktop background.'
            result = tkMbox.askquestion('Close Publication Window', q_str)
            if result == 'yes':
                if not SANTEC_SLM:
                    self.pub_win.win.destroy()
                self.pub_win_closed()
                self.ax1.clear()
                self.img1.draw()

    def update_phase_plot(self, phase):
        self.ax1.clear()
        self.ax1.imshow(phase % (bit_depth+1), cmap='twilight',
                        interpolation='None')
        self.img1.draw()

    def exit_prog(self):
        self.save('./last_settings.txt')
        self.pub_win_closed()
        self.main_win.destroy()


root = tk.Tk()

main = main_screen(root)

root.mainloop()
