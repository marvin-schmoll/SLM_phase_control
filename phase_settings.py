import tkinter as tk
from tkinter import ttk
import numpy as np
from tkinter.filedialog import askopenfilename
import matplotlib.image as mpimg
import time


slm_size = (600, 792)
chip_width = 15.84e-3
chip_height = 12e-3
wavelength = 800e-9
bit_depth = 256


print('types in')


types = ['Background', 'Flat', 'Tilt', 'Binary', 'Lens',
             'Multibeam', 'Vortex', 'Zernike']



def new_type(frm_mid, typ):
    if typ == 'Flat':
        return type_flat(frm_mid)
    elif typ == 'Tilt':
        return type_tilt(frm_mid)
    elif typ == 'Binary':
        return type_binary(frm_mid)
    elif typ == 'Background':
        return type_bg(frm_mid)
    elif typ == 'Lens':
        return type_lens(frm_mid)
    elif typ == 'Multibeam':
        return type_multibeams_cb(frm_mid)
    elif typ == 'Vortex':
        return type_vortex(frm_mid)
    elif typ == 'Zernike':
        return type_zernike(frm_mid)


class type_bg(object):
    """shows background settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=0, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Background')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        btn_open = tk.Button(lbl_frm, text='Open Background file',
                             command=self.open_file)
        self.lbl_file = tk.Label(lbl_frm, text='', wraplength=300, justify='left')
        btn_open.grid(row=0)
        self.lbl_file.grid(row=1)

    def open_file(self):
        filepath = askopenfilename(
            filetypes=[('Image Files', '*.bmp'), ('All Files', '*.*')]
        )
        if not filepath:
            return
        self.img = mpimg.imread(filepath)
        self.lbl_file['text'] = f'{filepath}'

    def phase(self):
        if self.lbl_file['text'] != '':
            phase = self.img
        else:
            phase = np.zeros(slm_size)
        return phase

    def save_(self):
        dict = {'filepath': self.lbl_file['text']}
        return dict

    def load_(self, dict):
        self.lbl_file['text'] = dict['filepath']
        try:
            self.img = mpimg.imread(dict['filepath'])
        except:
            print('Bg File missing')

    def name_(self):
        return 'Background'

    def close_(self):
        self.frm_.destroy()


class type_flat(object):
    """shows flat settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=1, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Flat')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        lbl_phi = tk.Label(lbl_frm, text='Phase shift (255=2pi):')
        vcmd = (parent.register(self.callback))
        self.strvar_flat = tk.StringVar()
        self.ent_flat = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_flat)
        lbl_phi.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        self.ent_flat.grid(row=0, column=1, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        if self.ent_flat.get() != '':
            phi = float(self.ent_flat.get())
        else:
            phi = 0
        phase = np.ones(slm_size)*phi
        return phase

    def save_(self):
        dict = {'flat_phase': self.ent_flat.get()}
        return dict

    def load_(self, dict):
        self.strvar_flat.set(dict['flat_phase'])

    def name_(self):
        return 'Flat'

    def close_(self):
        self.frm_.destroy()


class type_tilt(object):
    """shows the settings for redirection"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=2, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Tilt')
        lbl_frm.grid(row=0, column=0, sticky='ew', padx=5, pady=10)

        # Creating objects
        lbl_xdir = tk.Label(lbl_frm, text='Steepness along x-direction:')
        lbl_ydir = tk.Label(lbl_frm, text='Steepness along y-direction:')
        lbl_255 = tk.Label(lbl_frm, text='(255 corresponds to 2pi Rad)')
        lbl_step = tk.Label(lbl_frm, text='(wasd) Step per click:')
        vcmd = (parent.register(self.callback))
        self.strvar_xdir = tk.StringVar()
        self.strvar_ydir = tk.StringVar()
        self.ent_xdir = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_xdir)
        self.ent_ydir = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_ydir)
        self.strvar_tstep = tk.StringVar()
        self.ent_tstep = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_tstep)

        # Setting up
        lbl_xdir.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_ydir.grid(row=1, column=0, sticky='e', padx=(10, 0), pady=(0, 5))
        lbl_255.grid(row=2, sticky='ew', padx=(10, 10), pady=(0, 5))
        self.ent_xdir.grid(row=0, column=1, sticky='w', padx=(0, 10))
        self.ent_ydir.grid(row=1, column=1, sticky='w', padx=(0, 10))
        lbl_step.grid(row=3, column=0, sticky='e', padx=(10, 0), pady=(0, 5))
        self.ent_tstep.grid(row=3, column=1, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        xdir = self.ent_xdir.get()
        ydir = self.ent_ydir.get()

        if ydir != '' and float(ydir) != 0:
            lim = np.ones(slm_size[1]) * float(ydir)*(slm_size[1]-1)/2
            phy = np.linspace(-lim, +lim, slm_size[0], axis=0)
        else:
            phy = np.zeros(slm_size)

        if xdir != '' and float(xdir) != 0:
            lim = np.ones(slm_size[0]) * float(xdir)*(slm_size[0]-1)/2
            phx = np.linspace(-lim, +lim, slm_size[1], axis=1)
        else:
            phx = np.zeros(slm_size)

        return phx + phy

    def left_(self):
        tmp = float(self.strvar_xdir.get()) + float(self.strvar_tstep.get())
        self.strvar_xdir.set(tmp)

    def right_(self):
        tmp = float(self.strvar_xdir.get()) - float(self.strvar_tstep.get())
        self.strvar_xdir.set(tmp)

    def up_(self):
        tmp = float(self.strvar_ydir.get()) + float(self.strvar_tstep.get())
        self.strvar_ydir.set(tmp)

    def down_(self):
        tmp = float(self.strvar_ydir.get()) - float(self.strvar_tstep.get())
        self.strvar_ydir.set(tmp)

    def save_(self):
        dict = {'ent_xdir': self.ent_xdir.get(),
                'ent_ydir': self.ent_ydir.get()}
        return dict

    def load_(self, dict):
        self.strvar_xdir.set(dict['ent_xdir'])
        self.strvar_ydir.set(dict['ent_ydir'])

    def name_(self):
        return 'Tilt'

    def close_(self):
        self.frm_.destroy()


class type_binary(object):
    """shows binary settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=3, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Binary')
        lbl_frm.grid(row=0, column=0, sticky='ew', padx=5, pady=10)

        # Creating entities
        lbl_dir = tk.Label(lbl_frm, text='Direction for split:')
        lbl_rat = tk.Label(lbl_frm, text='Area amount (in %):')
        lbl_phi = tk.Label(lbl_frm, text='Phase change (in pi):')
        self.cbx_dir = ttk.Combobox(
            lbl_frm,
            values=['Horizontal', 'Vertical'],
            state='readonly',
            width=10)
        self.ent_area = tk.Spinbox(lbl_frm, width=12, from_=0, to=100)
        vcmd = (parent.register(self.callback))
        self.strvar_phi = tk.StringVar()
        self.ent_phi = tk.Entry(lbl_frm, width=12,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_phi)

        # Setting up
        lbl_dir.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_rat.grid(row=1, column=0, sticky='e', padx=(10, 0))
        lbl_phi.grid(row=2, column=0, sticky='e', padx=(10, 0), pady=5)
        self.cbx_dir.grid(row=0, column=1, sticky='w', padx=(0, 10))
        self.ent_area.grid(row=1, column=1, sticky='w', padx=(0, 10))
        self.ent_phi.grid(row=2, column=1, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        direc = self.cbx_dir.get()
        if self.ent_area.get() != '':
            area = float(self.ent_area.get())
        else:
            area = 0
        if self.ent_phi.get() != '':
            tmp = float(self.ent_phi.get())
            phi = tmp*bit_depth/2  # Converting to 0-2pi
        else:
            phi = 0

        phase_mat = np.zeros(slm_size)

        if direc == 'Horizontal':
            cutpixel = int(round(slm_size[0]*area/100))
            tmp = np.ones([cutpixel, slm_size[1]])*phi
            phase_mat[0:cutpixel, :] = tmp
        elif direc == 'Vertical':
            cutpixel = int(round(slm_size[1]*area/100))
            tmp = np.ones([slm_size[0], cutpixel])*phi
            phase_mat[:, 0:cutpixel] = tmp
        del tmp
        return phase_mat

    def save_(self):
        dict = {'direc': self.cbx_dir.get(),
                'area': self.ent_area.get(),
                'phi': self.ent_phi.get()}
        return dict

    def load_(self, dict):
        if dict['direc'] != 'Vertical' and dict['direc'] != 'Horizontal':
            dict['direc'] = 'Vertical'
        tmpind = self.cbx_dir['values'].index(dict['direc'])
        self.cbx_dir.current(tmpind)
        self.ent_area.delete(0, tk.END)
        self.ent_area.insert(0, dict['area'])
        self.strvar_phi.set(dict['phi'])

    def name_(self):
        return 'Binary'

    def close_(self):
        self.frm_.destroy()


class type_lens(object):
    """shows lens settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=4, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Lens')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        # creating labels
        lbl_ben = tk.Label(lbl_frm, text='Bending strength (1/f) [1/m]:')

        # creating entries
        vcmd = (parent.register(self.callback))
        self.strvar_ben = tk.StringVar()
        self.ent_ben = tk.Entry(lbl_frm, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_ben)

        # setup
        lbl_ben.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        self.ent_ben.grid(row=0, column=1, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        # getting the hyperbolical curve on the phases
        if self.ent_ben.get() != '':
            ben = float(self.ent_ben.get())
        else:
            ben = 0

        radsign = np.sign(ben)
        rad = 2/np.abs(ben)  # R=2*f
        x = np.linspace(-chip_width/2, chip_width/2, slm_size[1])
        y = np.linspace(-chip_height/2, chip_height/2, slm_size[0])
        [X, Y] = np.meshgrid(x, y)
        R = np.sqrt(X**2+Y**2)  # radius on a 2d array
        Z = radsign*(np.sqrt(rad**2+R**2)-rad)
        #print(Z[:, 396])
        Z_phi = Z/(wavelength)*bit_depth  # translating meters to wavelengths and phase
        del X, Y, R, Z
        return Z_phi

    def save_(self):
        dict = {'ben': self.ent_ben.get()}
        return dict

    def load_(self, dict):
        self.strvar_ben.set(dict['ben'])

    def name_(self):
        return 'Lens'

    def close_(self):
        self.frm_.destroy()


class type_multibeams_cb(object):
    """shows multibeam checkerboard settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=5, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Multibeam')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        # creating frames
        frm_n = tk.Frame(lbl_frm)
        frm_sprrad = tk.Frame(lbl_frm)
        frm_spr = tk.Frame(frm_sprrad)
        frm_rad = tk.Frame(frm_sprrad)
        frm_int = tk.Frame(lbl_frm)
        frm_pxsiz = tk.Frame(lbl_frm)

        # creating labels
        lbl_n = tk.Label(frm_n, text='n^2; n=:')
        lbl_hor = tk.Label(frm_int, text='Hor:')
        lbl_vert = tk.Label(frm_int, text='Vert:')
        lbl_intil = tk.Label(frm_int, text='Intensity tilt')
        lbl_insqr = tk.Label(frm_int, text='Intensity curve')
        lbl_horspr = tk.Label(frm_spr, text='Horizontal spread:')
        lbl_verspr = tk.Label(frm_spr, text='Vertical spread:')
        lbl_cph = tk.Label(frm_sprrad, text='Hyp.phase diff')
        lbl_rad = tk.Label(frm_rad, text='Phase[255]:')
        lbl_amp = tk.Label(frm_rad, text='Choose beam:')
        lbl_pxsiz = tk.Label(frm_pxsiz, text='pixel size:')

        # creating entries
        vcmd = (parent.register(self.callback))
        self.strvar_n = tk.StringVar()
        self.ent_n = tk.Entry(frm_n, width=5,  validate='all',
                              validatecommand=(vcmd, '%d', '%P', '%S'),
                              textvariable=self.strvar_n)
        self.strvar_hpt = tk.StringVar()
        self.ent_hpt = tk.Entry(frm_spr, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_hpt)
        self.strvar_vpt = tk.StringVar()
        self.ent_vpt = tk.Entry(frm_spr, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_vpt)
        self.strvar_rad = tk.StringVar()
        self.ent_rad = tk.Entry(frm_rad, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_rad)
        self.strvar_amp = tk.StringVar()
        self.ent_amp = tk.Entry(frm_rad, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_amp)
        self.strvar_hit = tk.StringVar()
        self.ent_hit = tk.Entry(frm_int, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_hit)
        self.strvar_vit = tk.StringVar()
        self.ent_vit = tk.Entry(frm_int, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_vit)
        self.strvar_his = tk.StringVar()
        self.ent_his = tk.Entry(frm_int, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_his)
        self.strvar_vis = tk.StringVar()
        self.ent_vis = tk.Entry(frm_int, width=5,  validate='all',
                                validatecommand=(vcmd, '%d', '%P', '%S'),
                                textvariable=self.strvar_vis)
        self.strvar_pxsiz = tk.StringVar()
        self.ent_pxsiz = tk.Entry(frm_pxsiz, width=5,  validate='all',
                                  validatecommand=(vcmd, '%d', '%P', '%S'),
                                  textvariable=self.strvar_pxsiz)

        # setup
        frm_n.grid(row=0, sticky='nsew')
        frm_sprrad.grid(row=1, sticky='nsew')
        frm_int.grid(row=2, sticky='nsew')
        frm_pxsiz.grid(row=3, sticky='nsew')

        frm_spr.grid(row=1, column=0, sticky='nsew')
        frm_rad.grid(row=1, column=1, sticky='ew')

        lbl_n.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=(5, 10))
        self.ent_n.grid(row=0, column=1, sticky='w',
                        padx=(0, 10), pady=(5, 10))

        lbl_horspr.grid(row=0, column=0, sticky='e', padx=(10, 0))
        lbl_verspr.grid(row=1, column=0, sticky='e', padx=(10, 0))
        self.ent_hpt.grid(row=0, column=1, sticky='w')
        self.ent_vpt.grid(row=1, column=1, sticky='w')

        lbl_cph.grid(row=0, column=1, sticky='ew')

        lbl_rad.grid(row=0, column=0, sticky='e', padx=(15, 0))
        lbl_amp.grid(row=1, column=0, sticky='e', padx=(15, 0))
        self.ent_rad.grid(row=0, column=1, sticky='w', padx=(0, 5))
        self.ent_amp.grid(row=1, column=1, sticky='w', padx=(0, 5))

        lbl_hor.grid(row=1, column=0, sticky='e', padx=(10, 0))
        lbl_vert.grid(row=2, column=0, sticky='e', padx=(10, 0))
        lbl_intil.grid(row=0, column=1, padx=5, pady=(10, 0))
        lbl_insqr.grid(row=0, column=2, padx=(0, 5), pady=(10, 0))
        self.ent_hit.grid(row=1, column=1)
        self.ent_his.grid(row=1, column=2, padx=(0, 5))
        self.ent_vit.grid(row=2, column=1, pady=(0, 5))
        self.ent_vis.grid(row=2, column=2, padx=(0, 5), pady=(0, 5))

        lbl_pxsiz.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        self.ent_pxsiz.grid(row=0, column=1, sticky='w')

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        # tic = time.perf_counter()
        if self.ent_n.get() != '':
            n = int(self.ent_n.get())
        else:
            n = 1

        # getting the different phases for the beams
        if self.ent_hpt.get() != '':
            xtilt = float(self.ent_hpt.get())
        else:
            xtilt = 0
        if self.ent_vpt.get() != '':
            ytilt = float(self.ent_vpt.get())
        else:
            ytilt = 0
        tilts = np.arange(-n+1, n+1, 2)  # excluding the last
        xtilts = tilts*xtilt/2
        ytilts = tilts*ytilt/2
        phases = np.zeros([slm_size[0], slm_size[1], n*n])
        ind = 0
        for xdir in xtilts:
            for ydir in ytilts:
                phases[:, :, ind] = self.phase_tilt(xdir, ydir)
                ind += 1

        # tic2 = time.perf_counter()
        # getting the hyperbolical curve on the phases
        if self.ent_rad.get() != '':
            tmprad = float(self.ent_rad.get())
        else:
            tmprad = 0
        if self.ent_amp.get() != '':
            amp = int(self.ent_amp.get())
        else:
            amp = 0
        if tmprad != 0:
            phases[:, :, amp] = tmprad + phases[:, :, amp]
            phases[:, :, amp+1] = tmprad + phases[:, :, amp+1]
            # radsign = np.sign(tmprad)
            # rad = np.abs(tmprad)
            # x = tilts
            # y = tilts
            # [X, Y] = np.meshgrid(x, y)
            # R = np.sqrt(X**2+Y**2)
            # Z = amp*radsign*(np.sqrt(rad**2+R**2)-rad)
            # ind = 0
            # for row in Z:
            #     for elem in row:
            #         phases[:, :, ind] = elem + phases[:, :, ind]
            #         ind += 1

        # tic3 = time.perf_counter()
        # setting up for intensity control
        if self.ent_hit.get() != '':
            xit = float(self.ent_hit.get())
        else:
            xit = 0
        if self.ent_vit.get() != '':
            yit = float(self.ent_vit.get())
        else:
            yit = 0
        if self.ent_his.get() != '':
            xis = float(self.ent_his.get())
        else:
            xis = 0
        if self.ent_vis.get() != '':
            yis = float(self.ent_vis.get())
        else:
            yis = 0
        intensities = np.ones(n**2)
        totnum = np.ceil((slm_size[0]*(slm_size[1]+n)/(n**2)))  # nbr of pixels for each phase
        #          plus n in second dimension to account for noneven placement
        phase_nbr = np.outer(np.arange(n**2), np.ones([int(totnum)]))

        # modifying linear intensities
        if xit != 0:
            xits = np.linspace(-((n-1)/2*xit), ((n-1)/2*xit), num=n)
        else:
            xits = np.zeros(n)
        if yit != 0:
            yits = np.linspace(-((n-1)/2*yit), ((n-1)/2*yit), num=n)
        else:
            yits = np.zeros(n)
        ii = 0
        for tmpx in xits:
            intensities[n*ii:n*(ii+1)] = (tmpx + yits + 1)
            ii += 1

        # tic4 = time.perf_counter()
        # modifying square intensities
        spread = tilts
        xiss = -xis * (spread**2 - spread[0]**2)
        yiss = -yis * (spread**2 - spread[0]**2)
        ii = 0
        for tmpx in xiss:
            intensities[n*ii:n*(ii+1)] += (tmpx + yiss + 1)
            ii += 1

        # tic5 = time.perf_counter()
        # creating the intensity arrays (which phase to have at which pixel)
        intensities[intensities < 0] = 0
        intensities = intensities/np.sum(intensities)*n**2  # normalize
        tmpint = intensities-1
        beam = 0
        strong_beams = []
        strong_beams_int = []
        weak_beams = []
        weak_beams_int = []
        for intens in tmpint:
            if intens > 0:
                strong_beams.append(beam)
                strong_beams_int.append(intens)
            elif intens < 0:
                weak_beams.append(beam)
                weak_beams_int.append(intens)
            beam += 1
        # normalize to one
        strong_beams_int = strong_beams_int/np.sum(strong_beams_int)
        for wbeam, wbeam_int in zip(weak_beams, weak_beams_int):
            nbr_pixels = np.ceil(np.abs(wbeam_int)*totnum)  # nbrpxls to change
            nbr_each = np.ceil(nbr_pixels*strong_beams_int)
            strt = 0
            for nbr, sbeam in zip(nbr_each, strong_beams):
                phase_nbr[int(wbeam), strt:(strt+int(nbr))] = sbeam
                strt += int(nbr)
        rng = np.random.default_rng()
        rng.shuffle(phase_nbr, axis=1)  # mixing so the changed are not tgether
        col = np.zeros(n**2)  # keeping track of which column in phase_nbr
        # tic6 = time.perf_counter()
        if self.ent_pxsiz.get() != '':
            pxsiz = int(self.ent_pxsiz.get())
        else:
            pxsiz = 1
        # creating the total phase by adding the different ones
        xrange = np.arange(0, slm_size[1], 1)
        yrange = np.arange(0, slm_size[0], 1)
        tot_phase = np.zeros(slm_size)
        [X, Y] = np.meshgrid(xrange, yrange)
        ind_phase_tmp = (np.floor(X/pxsiz) % n)*n + (np.floor(Y/pxsiz) % n)
        ind_phase = ind_phase_tmp.astype(int)

        # tic7 = time.perf_counter()
        iii = np.arange(0, n**2, 1)
        ind_phase2 = ind_phase.copy()
        for ii in iii:
            max_nbr = np.count_nonzero(ind_phase == ii)
            if max_nbr <= phase_nbr[0, :].size:
                ind_phase2[ind_phase == ii] = phase_nbr[ii, 0:max_nbr]
            else:
                extra = ii*np.ones([max_nbr-phase_nbr[0, :].size])
                ind_phase2[ind_phase == ii] = np.append(phase_nbr[ii, :], extra)

        for ii in iii:
            ii_phase = phases[:, :, ii]
            tot_phase[ind_phase2 == ii] = ii_phase[ind_phase2 == ii]
        # toc = time.perf_counter()
        # print(toc-tic)
        # print(tic2-tic)
        # print(tic3-tic2)
        # print(tic4-tic3)
        # print(tic5-tic4)
        # print(tic6-tic5)
        # print(tic7-tic6)
        # print(toc-tic7)

        return tot_phase

    def phase_tilt(self, xdir, ydir):
        if xdir != '' and float(xdir) != 0:
            lim = np.ones(slm_size[0]) * float(xdir)*(slm_size[0]-1)/2
            phx = np.linspace(-lim, +lim, slm_size[1], axis=1)
        else:
            phx = np.zeros(slm_size)

        if ydir != '' and float(ydir) != 0:
            lim = np.ones(slm_size[1]) * float(ydir)*(slm_size[1]-1)/2
            phy = np.linspace(-lim, +lim, slm_size[0], axis=0)
        else:
            phy = np.zeros(slm_size)

        return phx + phy

    def save_(self):
        dict = {'n': self.ent_n.get(),
                'hpt': self.ent_hpt.get(),
                'rad': self.ent_rad.get(),
                'hit': self.ent_hit.get(),
                'his': self.ent_his.get(),
                'vpt': self.ent_vpt.get(),
                'amp': self.ent_amp.get(),
                'vit': self.ent_vit.get(),
                'vis': self.ent_vis.get(),
                'pxsiz': self.ent_pxsiz.get()}
        return dict

    def load_(self, dict):
        self.strvar_n.set(dict['n'])
        self.strvar_hpt.set(dict['hpt'])
        self.strvar_rad.set(dict['rad'])
        self.strvar_hit.set(dict['hit'])
        self.strvar_his.set(dict['his'])
        self.strvar_vpt.set(dict['vpt'])
        self.strvar_amp.set(dict['amp'])
        self.strvar_vit.set(dict['vit'])
        self.strvar_vis.set(dict['vis'])
        self.strvar_pxsiz.set(dict['pxsiz'])

    def name_(self):
        return 'Multibeam'

    def close_(self):
        self.frm_.destroy()


class type_vortex(object):
    """shows vortex settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=6, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Vortex')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        lbl_vor = tk.Label(lbl_frm, text='Vortex order:')
        lbl_vordx = tk.Label(lbl_frm, text='dx [mm]:')
        lbl_vordy = tk.Label(lbl_frm, text='dy [mm]:')
        vcmd = (parent.register(self.callback))
        self.strvar_vor = tk.StringVar()
        self.strvar_vordx = tk.StringVar()
        self.strvar_vordy = tk.StringVar()
        self.ent_vor = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_vor)
        self.ent_vordx = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_vordx)
        self.ent_vordy = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_vordy)
        lbl_vor.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_vordx.grid(row=1, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_vordy.grid(row=2, column=0, sticky='e', padx=(10, 0), pady=5)
        self.ent_vor.grid(row=0, column=1, sticky='w', padx=(0, 10))
        self.ent_vordx.grid(row=1, column=1, sticky='w', padx=(0, 10))
        self.ent_vordy.grid(row=2, column=1, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        if self.ent_vor.get() != '':
            vor = float(self.ent_vor.get())
        else:
            vor = 0
        if self.ent_vordx.get() != '':
            dx = float(self.ent_vordx.get())
        else:
            dx = 0
        if self.ent_vordy.get() != '':
            dy = float(self.ent_vordy.get())
        else:
            dy = 0
        x = np.linspace(-chip_width*500+dx, chip_width*500+dx, slm_size[1])
        y = np.linspace(-chip_height*500+dy, chip_height*500+dy, slm_size[0])
        [X, Y] = np.meshgrid(x, y)
        theta = np.arctan(Y/X)
        theta[X < 0] += np.pi
        phase = theta*bit_depth/(2*np.pi)*vor
        return phase

    def save_(self):
        dict = {'vort_ord': self.ent_vor.get()}
        return dict

    def load_(self, dict):
        self.strvar_vor.set(dict['vort_ord'])

    def name_(self):
        return 'Vortex'

    def close_(self):
        self.frm_.destroy()


class type_zernike(object):
    """shows zernike settings for phase"""

    def __init__(self, parent):
        self.frm_ = tk.Frame(parent)
        self.frm_.grid(row=7, column=0, sticky='nsew')
        lbl_frm = tk.LabelFrame(self.frm_, text='Zernike')
        lbl_frm.grid(row=0, column=0, sticky='ew')

        lbl_z1 = tk.Label(lbl_frm, text='Z_00 koeff:')
        lbl_z2 = tk.Label(lbl_frm, text='Z_11 koeff:')
        lbl_z3 = tk.Label(lbl_frm, text='Z_1-1 koeff:')
        lbl_z4 = tk.Label(lbl_frm, text='Z_20 koeff:')
        lbl_z5 = tk.Label(lbl_frm, text='Z_22 koeff:')
        lbl_z6 = tk.Label(lbl_frm, text='Z_2-2 koeff:')
        lbl_z7 = tk.Label(lbl_frm, text='Z_31 koeff:')
        lbl_z8 = tk.Label(lbl_frm, text='Z_3-1 koeff:')
        lbl_z9 = tk.Label(lbl_frm, text='Z_33 koeff:')
        lbl_z10 = tk.Label(lbl_frm, text='Z_3-3 koeff:')
        lbl_zsize = tk.Label(lbl_frm, text='Z size:')
        lbl_zdx = tk.Label(lbl_frm, text='dx [mm]:')
        lbl_zdy = tk.Label(lbl_frm, text='dy [mm]:')
        vcmd = (parent.register(self.callback))
        self.strvar_z1 = tk.StringVar()
        self.strvar_z2 = tk.StringVar()
        self.strvar_z3 = tk.StringVar()
        self.strvar_z4 = tk.StringVar()
        self.strvar_z5 = tk.StringVar()
        self.strvar_z6 = tk.StringVar()
        self.strvar_z7 = tk.StringVar()
        self.strvar_z8 = tk.StringVar()
        self.strvar_z9 = tk.StringVar()
        self.strvar_z10 = tk.StringVar()
        self.strvar_zsize = tk.StringVar()
        self.strvar_zdx = tk.StringVar()
        self.strvar_zdy = tk.StringVar()
        self.ent_z1 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z1)
        self.ent_z2 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z2)
        self.ent_z3 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z3)
        self.ent_z4 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z4)
        self.ent_z5 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z5)
        self.ent_z6 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z6)
        self.ent_z7 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z7)
        self.ent_z8 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z8)
        self.ent_z9 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z9)
        self.ent_z10 = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_z10)
        self.ent_zsize = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_zsize)
        self.ent_zdx = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_zdx)
        self.ent_zdy = tk.Entry(
            lbl_frm, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_zdy)
        lbl_z1.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z2.grid(row=1, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z3.grid(row=2, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z4.grid(row=3, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z5.grid(row=4, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z6.grid(row=5, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z7.grid(row=6, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z8.grid(row=7, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z9.grid(row=8, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_z10.grid(row=9, column=0, sticky='e', padx=(10, 0), pady=5)
        lbl_zsize.grid(row=0, column=2, sticky='e', padx=(10, 0), pady=5)
        lbl_zdx.grid(row=1, column=2, sticky='e', padx=(10, 0), pady=5)
        lbl_zdy.grid(row=2, column=2, sticky='e', padx=(10, 0), pady=5)
        self.ent_z1.grid(row=0, column=1, sticky='w', padx=(0, 10))
        self.ent_z2.grid(row=1, column=1, sticky='w', padx=(0, 10))
        self.ent_z3.grid(row=2, column=1, sticky='w', padx=(0, 10))
        self.ent_z4.grid(row=3, column=1, sticky='w', padx=(0, 10))
        self.ent_z5.grid(row=4, column=1, sticky='w', padx=(0, 10))
        self.ent_z6.grid(row=5, column=1, sticky='w', padx=(0, 10))
        self.ent_z7.grid(row=6, column=1, sticky='w', padx=(0, 10))
        self.ent_z8.grid(row=7, column=1, sticky='w', padx=(0, 10))
        self.ent_z9.grid(row=8, column=1, sticky='w', padx=(0, 10))
        self.ent_z10.grid(row=9, column=1, sticky='w', padx=(0, 10))
        self.ent_zsize.grid(row=0, column=3, sticky='w', padx=(0, 10))
        self.ent_zdx.grid(row=1, column=3, sticky='w', padx=(0, 10))
        self.ent_zdy.grid(row=2, column=3, sticky='w', padx=(0, 10))

    def callback(self, action, P, text):
        # action=1 -> insert
        if(action == '1'):
            if text in '0123456789.-+':
                try:
                    float(P)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def phase(self):
        # tic1 = time.perf_counter()
        if self.ent_z1.get() != '':
            z1coef = float(self.ent_z1.get())
        else:
            z1coef = 0
        if self.ent_z2.get() != '':
            z2coef = float(self.ent_z2.get())
        else:
            z2coef = 0
        if self.ent_z3.get() != '':
            z3coef = float(self.ent_z3.get())
        else:
            z3coef = 0
        if self.ent_z4.get() != '':
            z4coef = float(self.ent_z4.get())
        else:
            z4coef = 0
        if self.ent_z5.get() != '':
            z5coef = float(self.ent_z5.get())
        else:
            z5coef = 0
        if self.ent_z6.get() != '':
            z6coef = float(self.ent_z6.get())
        else:
            z6coef = 0
        if self.ent_z7.get() != '':
            z7coef = float(self.ent_z7.get())
        else:
            z7coef = 0
        if self.ent_z8.get() != '':
            z8coef = float(self.ent_z8.get())
        else:
            z8coef = 0
        if self.ent_z9.get() != '':
            z9coef = float(self.ent_z9.get())
        else:
            z9coef = 0
        if self.ent_z10.get() != '':
            z10coef = float(self.ent_z10.get())
        else:
            z10coef = 0
        if self.ent_zsize.get() != '':
            zsize = float(self.ent_zsize.get())
        else:
            zsize = 1
        if self.ent_zdx.get() != '':
            zdx = float(self.ent_zdx.get())
        else:
            zdx = 0
        if self.ent_zdy.get() != '':
            zdy = float(self.ent_zdy.get())
        else:
            zdy = 1
        x = np.linspace(-chip_width*500+zdx, chip_width*500+zdx, slm_size[1])
        y = np.linspace(-chip_height*500+zdy, chip_height*500+zdy, slm_size[0])
        [X, Y] = np.meshgrid(x, y)
        theta = np.arctan(Y/X)
        theta[X < 0] += np.pi
        rho = np.sqrt(X**2+Y**2)/zsize
        tic2 = time.perf_counter()
        R = [1, rho, (2*rho**2-1), rho**2, (3*rho**3-2*rho), rho**3]
        Rnum = [1, 2, 2, 3, 4, 4, 5, 5, 6, 6]
        mnum = [0, 1, -1, 0, 2, -2, 1, -1, 3, -3]

        if z1coef == 0:
            p1 = 0
        else:
            p1 = z1coef*1*np.cos(0*theta)
        if z2coef == 0:
            p2 = 0
        else:
            p2 = z2coef*rho*np.cos(1*theta)
        if z3coef == 0:
            p3 = 0
        else:
            p3 = z3coef*rho*np.sin(1*theta)
        p4 = z4coef*(2*rho**2-1)*np.cos(0*theta)
        p5 = z5coef*rho**2*np.cos(2*theta)
        p6 = z6coef*rho**2*np.sin(2*theta)
        p7 = z7coef*(3*rho**3-2*rho)*np.cos(1*theta)
        p8 = z8coef*(3*rho**3-2*rho)*np.sin(1*theta)
        p9 = z9coef*rho**3*np.cos(3*theta)
        p10 = z10coef*rho**3*np.sin(3*theta)
        # tic4 = time.perf_counter()
        phase = p1+p2+p3+p4+p5+p6+p7+p8+p9+p10
        tic5 = time.perf_counter()
        print(tic5-tic2)
        return phase

    def save_(self):
        dict = {'z1coef': self.ent_z1.get(),
                'z2coef': self.ent_z2.get(),
                'z3coef': self.ent_z3.get(),
                'z4coef': self.ent_z4.get(),
                'z5coef': self.ent_z5.get(),
                'z6coef': self.ent_z6.get(),
                'z7coef': self.ent_z7.get(),
                'z8coef': self.ent_z8.get(),
                'z9coef': self.ent_z9.get(),
                'z10coef': self.ent_z10.get(),
                'zsize': self.ent_zsize.get(),
                'zdx': self.ent_zdx.get(),
                'zdy': self.ent_zdy.get()}
        return dict

    def load_(self, dict):
        self.strvar_z1.set(dict['z1coef'])
        self.strvar_z2.set(dict['z2coef'])
        self.strvar_z3.set(dict['z3coef'])
        self.strvar_z4.set(dict['z4coef'])
        self.strvar_z5.set(dict['z5coef'])
        self.strvar_z6.set(dict['z6coef'])
        self.strvar_z7.set(dict['z7coef'])
        self.strvar_z8.set(dict['z8coef'])
        self.strvar_z9.set(dict['z9coef'])
        self.strvar_z10.set(dict['z10coef'])
        self.strvar_zsize.set(dict['zsize'])
        self.strvar_zdx.set(dict['zdx'])
        self.strvar_zdy.set(dict['zdy'])

    def name_(self):
        return 'Zernike'

    def close_(self):
        self.frm_.destroy()
