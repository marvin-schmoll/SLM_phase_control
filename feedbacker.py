from settings import SANTEC_SLM, slm_size, bit_depth
import cam
import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import gxipy as gx
from PIL import Image, ImageTk
import time
import draw_polygon
from skimage.draw import polygon
from simple_pid import PID
import threading
from pynput import keyboard



class feedbacker(object):
    """works back and forth with publish_window"""

    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel()
        if not SANTEC_SLM:
            self.win.geometry('500x950+300+100')

        # creating frames
        frm_cam = tk.Frame(self.win)
        frm_bot = tk.Frame(self.win)
        frm_cam_but = tk.Frame(frm_cam)
        frm_cam_but_set = tk.Frame(frm_cam_but)
        frm_pid = tk.Frame(frm_bot)
        frm_mid = tk.Frame(self.win)
        frm_ratio = tk.Frame(frm_mid)

        # creating buttons n labels
        but_exit = tk.Button(frm_bot, text='EXIT', command=self.on_close)
        but_feedback = tk.Button(frm_bot, text='Feedback', command=self.feedback)
        but_cam_img = tk.Button(frm_cam_but, text='Get image', command=self.cam_img)
        but_cam_line = tk.Button(frm_cam_but, text='Plot fft', command=self.plot_fft)
        self.bVar_cam = tk.BooleanVar(self.win,True)
        but_cam_phi = tk.Button(frm_cam_but, text='Scan 2pi', command=self.fast_scan)
        lbl_phi = tk.Label(frm_bot, text='Phase shift (in pi):')
        vcmd = (self.win.register(self.callback))
        self.strvar_flat = tk.StringVar()
        self.ent_flat = tk.Entry(
            frm_bot, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_flat)
        lbl_cam_ind = tk.Label(frm_cam_but_set, text='Camera index:')
        self.strvar_cam_ind = tk.StringVar(self.win,'2')
        self.ent_cam_ind = tk.Entry(
            frm_cam_but_set, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_cam_ind)
        lbl_cam_exp = tk.Label(frm_cam_but_set, text='Camera exposure (us):')
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
        self.strvar_indexfft = tk.StringVar(self.win,'8')
        lbl_indexfft = tk.Label(frm_ratio, text='Index fft:')
        lbl_angle = tk.Label(frm_ratio, text='Phase:')
        self.ent_indexfft = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_indexfft)
        self.lbl_angle = tk.Label(frm_ratio, text='angle')
        self.strvar_area1x = tk.StringVar(self.win,'255, 420')
        self.ent_area1x = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_area1x)
        self.strvar_area1y = tk.StringVar(self.win,'470, 480')
        self.ent_area1y = tk.Entry(
            frm_ratio, width=11,
            textvariable=self.strvar_area1y)
        lbl_pidp = tk.Label(frm_pid, text='P-value:')
        self.strvar_pidp = tk.StringVar(self.win,'1')
        self.ent_pidp = tk.Entry(
            frm_pid, width=11,  validate='all',
            validatecommand=(vcmd, '%d', '%P', '%S'),
            textvariable=self.strvar_pidp)
        lbl_pidi = tk.Label(frm_pid, text='i-value:')
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
        frm_cam.grid(row=0, column=0, sticky='nsew')
        frm_mid.grid(row=1, column=0, sticky='nsew')
        frm_bot.grid(row=2, column=0, sticky='nsew')
        frm_cam_but.grid(row=1, column=0, sticky='nsew')


        # setting up buttons frm_cam
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

        # setting up buttons frm_bot
        lbl_phi.grid(row=0, column=0, sticky='e', padx=(10, 0), pady=5)
        self.ent_flat.grid(row=0, column=1, sticky='w', padx=(0, 10))
        but_exit.grid(row=1, column=0, padx=5, pady=5, ipadx=5, ipady=5)
        but_feedback.grid(row=1, column=1, padx=5, pady=5, ipadx=5, ipady=5)
        frm_pid.grid(row=5, column=0)

        #setting up frm_pid
        lbl_pidp.grid(row=0, column=0)
        lbl_pidi.grid(row=1, column=0)
        self.ent_pidp.grid(row=0, column=1)
        self.ent_pidi.grid(row=1, column=1)
        but_pid_setp.grid(row=2, column=0)
        but_pid_enbl.grid(row=2, column=2)
        but_pid_setk.grid(row=2, column=1)
        but_pid_stop.grid(row=2, column=3)

        # setting up cam image
        self.ImageLabel = tk.Label(frm_cam, bg = "#4682B4")
        self.ImageLabel.grid(row=0, sticky='nsew')

        #setting up frm_mid
        self.figr = Figure(figsize=(5, 2), dpi=100)
        self.ax1r = self.figr.add_subplot(211)
        self.ax2r = self.figr.add_subplot(212)
        self.img1r = FigureCanvasTkAgg(self.figr, frm_mid)
        self.tk_widget_figr = self.img1r.get_tk_widget()
        self.tk_widget_figr.grid(row=0, column=0, sticky='nsew')
        self.figp = Figure(figsize=(5, 2), dpi=100)
        self.ax1p = self.figp.add_subplot(111)
        self.img1p = FigureCanvasTkAgg(self.figp, frm_mid)
        self.tk_widget_figp = self.img1p.get_tk_widget()
        self.tk_widget_figp.grid(row=1, column=0, sticky='nsew')
        frm_ratio.grid(row=2, column=0, sticky='nsew')

        #setting up frm_ratio
        lbl_indexfft.grid(row=0, column=0)
        lbl_angle.grid(row=1, column=0)
        self.ent_indexfft.grid(row=0, column=1)
        self.lbl_angle.grid(row=1, column=1)
        self.ent_area1x.grid(row=3, column=0)
        self.ent_area1y.grid(row=3, column=1)

        self.im_phase = np.zeros(1000)
        self.pid = PID(0.35, 0, 0, setpoint=0)

        #setting up a listener for catchin esc from cam1
        global stop_cam
        stop_cam = 0
        global stop_pid
        stop_pid = False
        l = keyboard.Listener(on_press=self.press_callback)
        l.start()

    def press_callback(self, key):

        if key == keyboard.Key.esc:
            def stop_loop():
                global stop_cam
                stop_cam = 1
                return stop_cam
            print('Get Out')
            stop_cam = stop_loop()

        return stop_cam

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

    def feedback(self):
        if self.ent_flat.get() != '':
            phi = float(self.ent_flat.get())
        else:
            phi = 0
        phase_map = self.parent.phase_map + phi/2*bit_depth
        if SANTEC_SLM:
            self.parent.slm.SLM_Disp_Open(int(self.ent_scr.get()))
            self.parent.slm.SLM_Disp_Data(int(self.ent_scr.get()), phase_map,
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
        if dev_num is 0:
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
        single = False
        if single:
            self.acq_mono(cam1, 1)
            self.cam_on_close(cam1)
        else:
            self.acq_mono(cam1, 10000)
            self.cam_on_close(cam1)

    def acq_mono(self, device, num):
        """
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
            try:
                xpoints1 = np.fromstring(self.ent_area1x.get(), sep=',')
                ypoints1 = np.fromstring(self.ent_area1y.get(), sep=',')
            except:
                xpoints1 = [200, 550]
                ypoints1 = [470, 480]


            #trying spatial phase extraction
            im_ = numpy_image[int(ypoints1[0]):int(ypoints1[1]),int(xpoints1[0]):int(xpoints1[1])]
            self.im_sum = np.sum(im_, axis=0)

            im_fft = np.fft.fft(self.im_sum)
            self.abs_im_fft = np.abs(im_fft)
            ind = round(float(self.ent_indexfft.get()))
            try:
                self.im_angl = np.angle(im_fft[ind])
            except:
                self.im_angl = 0
            self.lbl_angle.config(text=self.im_angl)

            # Show images
            picture = Image.fromarray(numpy_image)
            picture = picture.resize((500, 350), resample=0)
            CaptureFrame = picture.copy()
            picture = ImageTk.PhotoImage(picture)
            self.ImageLabel.configure(image = picture)
            self.ImageLabel.photo = picture

            # creating the phase vector
            self.im_phase[:-1] = self.im_phase[1:]
            self.im_phase[-1] = self.im_angl
            self.im_phase = np.unwrap(self.im_phase)

            global stop_cam
            if stop_cam ==1:
                stop_cam = 0
                break


    def cam_on_close(self, device):

        # stop acquisition
        device.stream_off()

        # close device
        device.close_device()

    def cam_img(self):
        self.render_thread = threading.Thread(target=self.init_cam)
        self.render_thread.daemon = True
        self.render_thread.start()
        self.plot_phase()


    def plot_fft(self):
        self.ax1r.clear()
        self.ax1r.plot(self.im_sum)
        self.ax2r.clear()
        self.ax2r.plot(self.abs_im_fft)
        self.img1r.draw()

    def plot_phase(self):
        self.ax1p.clear()
        self.ax1p.plot(self.im_phase)
        self.img1p.draw()
        self.win.after(500,self.plot_phase)

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
        self.pid.setpoint = self.ent_pidp.get()

    def set_pid_val(self):
        self.pid.Ki = self.ent_pidi.get()

    def pid_strt(self):
        while True:
            correction = self.pid(self.im_angl)
            self.strvar_flat.set(correction)
            self.feedback()
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
        self.win.destroy()
