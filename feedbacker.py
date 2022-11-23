from settings import SANTEC_SLM, slm_size, bit_depth
import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import avaspec_driver._avs_py as avs
import gxipy as gx
from PIL import Image, ImageTk
import time
import draw_polygon
from simple_pid import PID
import threading
from pynput import keyboard



class feedbacker(object):
    """works back and forth with publish_window"""

    def __init__(self, parent, slm_lib, CAMERA):
        self.CAMERA = CAMERA   # True for Camera Mode, False for Spectrometer Mode
        self.parent = parent
        self.slm_lib = slm_lib
        self.win = tk.Toplevel()
        if self.CAMERA: 
            title = 'SLM Phase Control - Feedbacker (spatial)'
        else:
            title = 'SLM Phase Control - Feedbacker (spectral)'
        self.win.title(title)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        if not SANTEC_SLM:
            self.win.geometry('500x950+300+100')
        self.rect_id = 0

        # creating frames
        if self.CAMERA:
            frm_cam = tk.Frame(self.win)
            frm_cam_but = tk.Frame(frm_cam)
            frm_cam_but_set = tk.Frame(frm_cam_but)
        else:
            frm_spc_but = tk.Frame(self.win)
            frm_spc_but_set = tk.Frame(frm_spc_but)
        frm_bot = tk.Frame(self.win)
        frm_plt = tk.Frame(self.win)
        frm_mid = tk.Frame(self.win)
        frm_ratio = tk.LabelFrame(frm_mid, text='Phase extraction')
        frm_pid = tk.LabelFrame(frm_mid, text='PID controller')
        
        vcmd = (self.win.register(self.parent.callback))

        # creating buttons n labels
        but_exit = tk.Button(frm_bot, text='EXIT', command=self.on_close)
        but_feedback = tk.Button(frm_bot, text='Feedback', command=self.feedback)
        if self.CAMERA:
            but_cam_img = tk.Button(frm_cam_but, text='Get image', command=self.cam_img)
            but_cam_line = tk.Button(frm_cam_but, text='Plot fft', command=self.plot_fft)
            but_cam_phi = tk.Button(frm_cam_but, text='Scan 2pi', command=self.fast_scan)
            lbl_cam_ind = tk.Label(frm_cam_but_set, text='Camera index:')
            self.strvar_cam_ind = tk.StringVar(self.win,'2')
            self.ent_cam_ind = tk.Entry(
                frm_cam_but_set, width=11,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_cam_ind)
            lbl_cam_exp = tk.Label(frm_cam_but_set, text='Camera exposure (µs):')
            self.strvar_cam_exp = tk.StringVar(self.win,'1000')
            self.ent_cam_exp = tk.Entry(
                frm_cam_but_set, width=11,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_cam_exp)
            lbl_cam_gain = tk.Label(frm_cam_but_set, text='Camera gain (0-24):')
            self.strvar_cam_gain = tk.StringVar(self.win,'20')
            self.ent_cam_gain = tk.Entry(
                frm_cam_but_set, width=11,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_cam_gain)
        else:
            lbl_spc_ind = tk.Label(frm_spc_but_set, text='Spectrometer index:')
            self.strvar_spc_ind = tk.StringVar(self.win,'1')
            self.ent_spc_ind = tk.Entry(
                frm_spc_but_set, width=9,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_spc_ind)
            lbl_spc_exp = tk.Label(frm_spc_but_set, text='Exposure time (ms):')
            self.strvar_spc_exp = tk.StringVar(self.win,'50')
            self.ent_spc_exp = tk.Entry(
                frm_spc_but_set, width=9,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_spc_exp)
            lbl_spc_gain = tk.Label(frm_spc_but_set, text='Nr. of averages:')
            self.strvar_spc_avg = tk.StringVar(self.win,'1')
            self.ent_spc_avg = tk.Entry(
                frm_spc_but_set, width=9,  validate='all',
                validatecommand=(vcmd, '%d', '%P', '%S'),
                textvariable=self.strvar_spc_avg)
            but_spc_activate = tk.Button(frm_spc_but_set, text='Activate',
                                    command=self.spec_activate, width=8)
            but_spc_deactivate = tk.Button(frm_spc_but_set, text='Deactivate',
                                    command=self.spec_deactivate, width=8)
            but_auto_scale = tk.Button(frm_spc_but_set, text='auto-scale',
                                    command=self.auto_scale_spec_axis, width=8)
            but_spc_start = tk.Button(frm_spc_but, text='Start\nSpectrometer',
                                      command=self.spc_img, height=2)
            but_spc_stop = tk.Button(frm_spc_but, text='Stop\nSpectrometer',
                                     command=self.stop_measure, height=2)
            but_spc_phi = tk.Button(frm_spc_but, text='Scan 2pi',
                                    command=self.fast_scan, height=2)     
        lbl_phi = tk.Label(frm_ratio, text='Phase shift:')
        lbl_phi_2 = tk.Label(frm_ratio, text='pi')
        self.strvar_flat = tk.StringVar()
        self.ent_flat = tk.Entry(
            frm_ratio, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_flat)
        if SANTEC_SLM: text='4'
        else: text='8'
        self.strvar_indexfft = tk.StringVar(self.win,text)
        lbl_indexfft = tk.Label(frm_ratio, text='Index fft:')
        lbl_angle = tk.Label(frm_ratio, text='Phase:')
        self.ent_indexfft = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_indexfft)
        self.lbl_angle = tk.Label(frm_ratio, text='angle')
        if SANTEC_SLM: text='400, 1050'
        else: text='255, 420'
        if not CAMERA: text = '1950'
        self.strvar_area1x = tk.StringVar(self.win,text)
        self.ent_area1x = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_area1x)
        if SANTEC_SLM: text='630, 650'
        else: text='470, 480'
        if not CAMERA: text = '2100'
        self.strvar_area1y = tk.StringVar(self.win,text)
        self.ent_area1y = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_area1y)
        self.intvar_area = tk.IntVar()
        self.cbox_area = tk.Checkbutton(frm_ratio, text='view area',
                           variable=self.intvar_area,
                           onvalue=1, offvalue=0)
        if self.CAMERA:
            lbl_direction = tk.Label(frm_ratio, text='Integration direction:')
            self.cbx_dir = tk.ttk.Combobox(frm_ratio, width=10,
                                           values=['horizontal', 'vertical'])
            self.cbx_dir.current(0)
        lbl_setp = tk.Label(frm_pid, text='Setpoint:')
        self.strvar_setp = tk.StringVar(self.win,'0')
        self.ent_setp = tk.Entry(
            frm_pid, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_setp)
        lbl_pidp = tk.Label(frm_pid, text='P-value:')
        self.strvar_pidp = tk.StringVar(self.win,'1')
        self.ent_pidp = tk.Entry(
            frm_pid, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_pidp)
        lbl_pidi = tk.Label(frm_pid, text='I-value:')
        self.strvar_pidi = tk.StringVar(self.win,'0')
        self.ent_pidi = tk.Entry(
            frm_pid, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_pidi)
        but_pid_setp = tk.Button(frm_pid, text='Setpoint', command=self.set_setpoint)
        but_pid_enbl = tk.Button(frm_pid, text='Start PID', command=self.enbl_pid)
        but_pid_stop = tk.Button(frm_pid, text='Stop PID', command=self.pid_stop)
        but_pid_setk = tk.Button(frm_pid, text='Set PID values', command=self.set_pid_val)


        # setting up
        if self.CAMERA:
            frm_cam.grid(row=0, column=0, sticky='nsew')
            frm_cam_but.grid(row=1, column=0, sticky='nsew')
        else:
            frm_spc_but.grid(row=0, column=0, sticky='nsew')
        frm_plt.grid(row=1, column=0, sticky='nsew')
        frm_mid.grid(row=2, column=0, sticky='nsew')
        frm_bot.grid(row=3, column=0)
        frm_ratio.grid(row=0, column=0, padx=5)
        frm_pid.grid(row=0, column=1, padx=5)
        if self.CAMERA:
            frm_ratio.config(width=282, height=108)
        else:
            frm_ratio.config(width=282, height=88)
        frm_ratio.grid_propagate(False)

        # setting up buttons frm_cam / frm_spc
        if self.CAMERA:
            but_cam_img.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5)
            but_cam_line.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5)
            but_cam_phi.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)
            frm_cam_but_set.grid(row=0, column=3, sticky='nsew')
            lbl_cam_ind.grid(row=0, column=0)
            self.ent_cam_ind.grid(row=0, column=1, padx=(0,10))
            lbl_cam_exp.grid(row=1, column=0)
            self.ent_cam_exp.grid(row=1, column=1, padx=(0,10))
            lbl_cam_gain.grid(row=2, column=0)
            self.ent_cam_gain.grid(row=2, column=1, padx=(0,10))
        else:
            frm_spc_but_set.grid(row=0, column=0, sticky='nsew')
            but_spc_start.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5)
            but_spc_stop.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)
            but_spc_phi.grid(row=0, column=3, padx=5, pady=5, ipadx=5, ipady=5)
            lbl_spc_ind.grid(row=0, column=0)
            self.ent_spc_ind.grid(row=0, column=1)
            but_spc_activate.grid(row=0, column=2, padx=(1,5))
            lbl_spc_exp.grid(row=1, column=0)
            self.ent_spc_exp.grid(row=1, column=1)
            but_spc_deactivate.grid(row=1, column=2, padx=(1,5))
            lbl_spc_gain.grid(row=2, column=0)
            self.ent_spc_avg.grid(row=2, column=1)
            but_auto_scale.grid(row=2, column=2, padx=(1,5))

        # setting up buttons frm_bot
        but_exit.grid(row=1, column=0, padx=5, pady=5, ipadx=5, ipady=5)
        but_feedback.grid(row=1, column=1, padx=5, pady=5, ipadx=5, ipady=5)

        # setting up frm_pid
        lbl_setp.grid(row=0, column=0)
        lbl_pidp.grid(row=1, column=0)
        lbl_pidi.grid(row=2, column=0)
        self.ent_setp.grid(row=0, column=1)
        self.ent_pidp.grid(row=1, column=1)
        self.ent_pidi.grid(row=2, column=1)
        but_pid_setp.grid(row=3, column=0)
        but_pid_setk.grid(row=3, column=1)
        but_pid_enbl.grid(row=1, column=2)
        but_pid_stop.grid(row=2, column=2)

        # setting up cam image
        if self.CAMERA:
            self.img_canvas = tk.Canvas(frm_cam, height=350, width=500)
            self.img_canvas.grid(row=0, sticky='nsew')
            self.img_canvas.configure(bg='grey')
            self.image = self.img_canvas.create_image(0, 0, anchor="nw")

        # setting up frm_plt
        if self.CAMERA: sizefactor = 1
        else: sizefactor = 1.05
        
        self.figr = Figure(figsize=(5*sizefactor, 2*sizefactor), dpi=100)
        self.ax1r = self.figr.add_subplot(211)
        self.ax2r = self.figr.add_subplot(212)
        self.trace_line, = self.ax1r.plot([])
        self.fourier_line, = self.ax2r.plot([])
        self.fourier_indicator = self.ax2r.plot([], 'v')[0]
        self.fourier_text = self.ax2r.text(0.4,0.5, "")
        self.ax1r.set_xlim(0, 200)
        self.ax1r.set_ylim(0, 3000)
        self.ax1r.grid()
        self.ax2r.set_xlim(0, 50)
        self.ax2r.set_ylim(0, .6)
        self.figr.canvas.draw()
        self.img1r = FigureCanvasTkAgg(self.figr, frm_plt)
        self.tk_widget_figr = self.img1r.get_tk_widget()
        self.tk_widget_figr.grid(row=0, column=0, sticky='nsew')
        self.img1r.draw()
        self.ax1r_blit = self.figr.canvas.copy_from_bbox(self.ax1r.bbox)
        self.ax2r_blit = self.figr.canvas.copy_from_bbox(self.ax2r.bbox)
        
        self.figp = Figure(figsize=(5*sizefactor, 2*sizefactor), dpi=100)
        self.ax1p = self.figp.add_subplot(111)
        self.phase_line, = self.ax1p.plot([], '.', ms=1)
        self.ax1p.set_xlim(0, 1000)
        self.ax1p.set_ylim([-np.pi, np.pi])
        self.ax1p.grid()
        self.figp.canvas.draw()
        self.img1p = FigureCanvasTkAgg(self.figp, frm_plt)
        self.tk_widget_figp = self.img1p.get_tk_widget()
        self.tk_widget_figp.grid(row=1, column=0, sticky='nsew')
        self.img1p.draw()
        self.ax1p_blit = self.figp.canvas.copy_from_bbox(self.ax1p.bbox)

        # setting up frm_ratio
        self.ent_area1x.grid(row=0, column=0)
        self.ent_area1y.grid(row=0, column=1)
        self.cbox_area.grid(row=0, column=2)
        if self.CAMERA:
            lbl_direction.grid(row=1, column=0, columnspan=2)
            self.cbx_dir.grid(row=1, column=2, columnspan=2, sticky='w')
            lbl_indexfft.grid(row=2, column=0, sticky='e')
            self.ent_indexfft.grid(row=2, column=1)
            lbl_angle.grid(row=2, column=2)
            self.lbl_angle.grid(row=2, column=3)
            lbl_phi.grid(row=3, column=0, sticky='e')
            self.ent_flat.grid(row=3, column=1)
            lbl_phi_2.grid(row=3, column=2, sticky='w')
        else:
            lbl_indexfft.grid(row=1, column=0, sticky='e')
            self.ent_indexfft.grid(row=1, column=1)
            lbl_angle.grid(row=1, column=2)
            self.lbl_angle.grid(row=1, column=3)
            lbl_phi.grid(row=2, column=0, sticky='e')
            self.ent_flat.grid(row=2, column=1)
            lbl_phi_2.grid(row=2, column=2, sticky='w')

        self.im_phase = np.zeros(1000)
        self.pid = PID(0.35, 0, 0, setpoint=0)

        # setting up a listener for catchin esc from cam1 or spec
        self.stop_acquire = 0
        global stop_pid
        stop_pid = False
        l = keyboard.Listener(on_press=self.press_callback)
        l.start()
        # class attributes to store spectrometer state
        if not self.CAMERA:
            self.spec_interface_initialized = False
            self.active_spec_handle = None

    def press_callback(self, key): 
        if key == keyboard.Key.esc:
            self.stop_acquire = 1
        return

    def feedback(self):
        if self.ent_flat.get() != '':
            phi = float(self.ent_flat.get())
        else:
            phi = 0
        phase_map = self.parent.phase_map + phi/2*bit_depth
        if SANTEC_SLM:
            self.slm_lib.SLM_Disp_Open(int(self.parent.ent_scr.get()))
            self.slm_lib.SLM_Disp_Data(int(self.parent.ent_scr.get()), phase_map,
                                          slm_size[1], slm_size[0])
        else:
            self.parent.pub_win.publish_img(phase_map)

    def init_cam(self):
        print("")
        print("Initializing......")
        print("")
        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num == 0:
            print("Number of enumerated devices is 0")
            return

        # open the first device
        cam1 = device_manager.open_device_by_index(int(self.ent_cam_ind.get()))

        # set exposure
        cam1.ExposureTime.set(float(self.ent_cam_exp.get()))

        # set gain
        cam1.Gain.set(float(self.ent_cam_gain.get()))

        if dev_info_list[0].get("device_class") == gx.GxDeviceClassList.USB2:
            # set trigger mode
            cam1.TriggerMode.set(gx.GxSwitchEntry.ON)
        else:
            # set trigger mode and trigger source
            cam1.TriggerMode.set(gx.GxSwitchEntry.ON)
            cam1.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)


        # start data acquisition
        cam1.stream_on()
        self.acq_mono(cam1, 10000)
        self.cam_on_close(cam1)  #TODO: move this to where it actually gets executed

    def acq_mono(self, device, num):
        """
        acquisition function for camera
               :brief      acquisition function of mono device
               :param      device:     device object[Device]
               :param      num:        number of acquisition images[int]
        """
        for i in range(num):
            time.sleep(0.001)

            # send software trigger command
            device.TriggerSoftware.send_command()

            # get raw image
            raw_image = device.data_stream[0].get_image()
            if raw_image is None:
                print("Getting image failed.")
                continue

            # create numpy array with data from raw image
            numpy_image = raw_image.get_numpy_array()
            if numpy_image is None:
                continue

            # # sum to area1
            #TODO: change this so that program does not crash if no comma detected
            #       add Dlab default values -> whiteboard (is this for settings file?)
            try:
                xpoints = np.fromstring(self.ent_area1x.get(), sep=',')
                ypoints = np.fromstring(self.ent_area1y.get(), sep=',')
            except:
                if SANTEC_SLM:
                    xpoints = [400, 1050]
                    ypoints = [630, 650]
                else:
                    xpoints = [200, 550]
                    ypoints = [470, 480]
            if xpoints[1] < xpoints[0]:
                xpoints[1] = xpoints[0]+2
            if ypoints[1] < ypoints[0]:
                ypoints[1] = ypoints[0]+2

            #trying spatial phase extraction
            im_ = numpy_image[int(ypoints[0]):int(ypoints[1]),int(xpoints[0]):int(xpoints[1])]
            if self.cbx_dir.get() == 'horizontal':
                self.trace = np.sum(im_, axis=0)
            else:
                self.trace = np.sum(im_, axis=1)

            im_fft = np.fft.fft(self.trace)
            self.abs_im_fft = np.abs(im_fft)
            ind = round(float(self.ent_indexfft.get()))
            try:
                self.im_angl = np.angle(im_fft[ind])
            except:
                self.im_angl = 0
            self.lbl_angle.config(text=np.round(self.im_angl, 6))

            # Show images
            picture = Image.fromarray(numpy_image)
            picture = picture.resize((500, 350), resample=0)
            picture = ImageTk.PhotoImage(picture)
            
            self.img_canvas.itemconfig(self.image, image=picture)
            self.img_canvas.image = picture # keep a reference!
            
            # Draw selection lines
            if self.intvar_area.get() == 1:
                x1, x2 = xpoints * 500 / 1440
                y1, y2 = ypoints * 350 / 1080
                new_rect_id = self.img_canvas.create_rectangle(x1, y1, x2, y2, outline='orange')
                self.img_canvas.delete(self.rect_id)
                self.rect_id = new_rect_id
            else:
                self.img_canvas.delete(self.rect_id) 

            # creating the phase vector
            self.im_phase[:-1] = self.im_phase[1:]
            self.im_phase[-1] = self.im_angl

            if self.stop_acquire == 1:
                self.stop_acquire = 0
                break
    
    
    def eval_spec(self):
        """
        acquisition function for spectrometer
               :brief      acquisition function of mono device
               :param      num:        number of acquisition images[int]
        """
        while True:
            time.sleep(0.01)

            # get raw trace
            timestamp, data = avs.get_spectrum(self.active_spec_handle)

            start = int(self.ent_area1x.get())
            stop = int(self.ent_area1y.get())
            self.trace = data[start:stop]
            
            #print(timestamp)

            im_fft = np.fft.fft(self.trace)
            self.abs_im_fft = np.abs(im_fft)
            self.abs_im_fft = self.abs_im_fft / np.max(self.abs_im_fft)
            ind = round(float(self.ent_indexfft.get()))
            try:
                self.im_angl = np.angle(im_fft[ind])
            except:
                self.im_angl = 0
            self.lbl_angle.config(text=np.round(self.im_angl, 6))

            # creating the phase vector
            self.im_phase[:-1] = self.im_phase[1:]
            self.im_phase[-1] = self.im_angl

            if self.stop_acquire == 1:
                self.stop_acquire = 0
                break
            
            self.plot_fft_blit()


    def cam_on_close(self, device):
        #TODO: somehow this does not work -> check to reopen in DahengGalaxyView
        device.stream_off()   # stop acquisition
        device.close_device()   # close device

    def cam_img(self):
        self.render_thread = threading.Thread(target=self.init_cam)
        self.render_thread.daemon = True
        self.render_thread.start()
        self.plot_phase()

    def spc_img(self):
        self.render_thread = threading.Thread(target=self.start_measure)
        self.render_thread.daemon = True
        self.render_thread.start()
        self.plot_phase()
        
    def auto_scale_spec_axis(self):
        self.ax1r.clear()
        self.trace_line, = self.ax1r.plot([])
        self.ax1r.set_xlim(0, len(self.trace))
        self.ax1r.set_ylim(0, np.max(self.trace)*1.2)
        self.ax1r.grid('both')
        self.figr.canvas.draw()
        self.img1r.draw()
        self.ax1r_blit = self.figr.canvas.copy_from_bbox(self.ax1r.bbox)
        
    def plot_fft(self):
        # find maximum in the fourier trace
        maxindex = np.where(self.abs_im_fft == np.max(self.abs_im_fft[3:50]))[0][0]
        print(maxindex)
        
        self.ax1r.clear()
        self.ax1r.plot(self.trace)
        self.ax2r.clear()
        self.ax2r.plot(self.abs_im_fft)
        self.ax2r.plot(maxindex, self.abs_im_fft[maxindex]*1.2, 'v')
        self.ax2r.text(maxindex-1, self.abs_im_fft[maxindex]*1.5, str(maxindex))
        self.ax2r.set_xlim(0,50)
        self.img1r.draw()

    def plot_fft_blit(self):
        # find maximum in the fourier trace
        maxindex = np.where(self.abs_im_fft == np.max(self.abs_im_fft[5:50]))[0][0]
        
        self.figr.canvas.restore_region(self.ax1r_blit)
        self.figr.canvas.restore_region(self.ax2r_blit)
        self.trace_line.set_data(np.arange(len(self.trace)), self.trace)
        self.ax1r.draw_artist(self.trace_line)
        self.fourier_line.set_data(np.arange(50), self.abs_im_fft[:50])
        self.ax1r.draw_artist(self.fourier_line)
        self.fourier_indicator.set_data([maxindex], [self.abs_im_fft[maxindex]+0.05])
        self.ax1r.draw_artist(self.fourier_indicator)
        self.fourier_text.set_text(str(maxindex))
        self.fourier_text.set_position((maxindex-1, self.abs_im_fft[maxindex]+0.09))
        self.ax1r.draw_artist(self.fourier_text)
        self.figr.canvas.blit()
        self.figr.canvas.flush_events()

    def plot_phase(self):
        self.figp.canvas.restore_region(self.ax1p_blit)
        self.phase_line.set_data(np.arange(1000), self.im_phase)
        self.ax1p.draw_artist(self.phase_line)
        self.figp.canvas.blit(self.ax1p.bbox)
        self.figp.canvas.flush_events()
        self.win.after(50,self.plot_phase)

    
    def spec_activate(self):
        if not self.spec_interface_initialized:
            avs.AVS_Init()
        if self.active_spec_handle is None:
            speclist = avs.AVS_GetList()
            print(str(len(speclist)) + ' spectrometer(s) found.')
            self.active_spec_handle = avs.AVS_Activate(speclist[0])
            self.ent_spc_ind.config(state='disabled')

    def spec_deactivate(self):
        if self.active_spec_handle is not None:
            avs.AVS_StopMeasure(self.active_spec_handle)
            avs.AVS_Deactivate(self.active_spec_handle)
            self.ent_spc_ind.config(state='normal')
            self.active_spec_handle = None
    
    def start_measure(self):
        self.spec_activate()
        int_time = float(self.ent_spc_exp.get())
        no_avg = int(self.ent_spc_avg.get())
        avs.set_measure_params(self.active_spec_handle, int_time, no_avg)
        avs.AVS_Measure(self.active_spec_handle)
        self.eval_spec()
    
    def stop_measure(self):
        if self.active_spec_handle is not None:
            avs.AVS_StopMeasure(self.active_spec_handle)

    def fast_scan(self):
        phis = np.linspace(0,2,60)
        for phi in phis:
            self.strvar_flat.set(phi)
            self.feedback()
            time.sleep(0.1)

    def set_area1(self):
        poly_1 = draw_polygon.draw_polygon(self.ax1, self.fig)
        print(poly_1)
    
    def set_setpoint(self):
        self.pid.setpoint = float(self.ent_setp.get())

    def set_pid_val(self):
        self.pid.Kp = float(self.ent_pidp.get())
        self.pid.Ki = float(self.ent_pidi.get())
        print(self.pid.tunings)
    
    def pid_strt(self):
        self.set_setpoint()
        self.set_pid_val()
        
        while True:
            time.sleep(0.05)
            correction = self.pid(self.im_angl)
            self.strvar_flat.set(correction)
            self.feedback()
            print(self.pid.components)
            global stop_pid
            if stop_pid:
                break

    def enbl_pid(self):
        #setting up a listener for new im_phase
        global stop_pid
        stop_pid = False
        self.pid_thread = threading.Thread(target=self.pid_strt)
        self.pid_thread.daemon = True
        self.pid_thread.start()

    def pid_stop(self):
        global stop_pid
        stop_pid = True

    def on_close(self):
        plt.close(self.figr)
        plt.close(self.figp)
        if self.CAMERA:
            None
        else:
            self.spec_deactivate()
            avs.AVS_Done()
        self.win.destroy()
        self.parent.fbck_win = None
