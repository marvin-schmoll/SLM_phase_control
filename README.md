# SLM_phase_control
A small GUI application for controlling the phase of the SLM.
The project was first created for the Hamamatsu SLM (Attolab), but has been updated to work with the santec SLM-300 (D-Lab).

To run the program, execute "controlPhaseSLM.py", it wil load all the other files as it needs to.

Some settings (the wavelength used in the lab and the SLM type used) still need to be made on the code level before the program is run.
These can be found and changed in the file "settings.py".


## Structure

"background" contains the wavefront correction images for the SLMs provided by their manufacturer.

"santec_driver" contains drivers to communicate with the Santec-SLMs.

"avaspec_driver" contains drivers to communicate with the Aventes Spectrometer.

"gxipy" contains drivers to communicate with the Daheng camera.


### New features

- Can now generate Hologram phase patterns with the Gerchberg-Saxton-algorithm.

- Now includes PID-controller to work use the SLM for delay stabilization in interferometry.
	This works on spatial fringes with a camera (Daheng) or on spectral fringes with a spectrometer (Avspec).
