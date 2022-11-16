# -*- coding: utf-8 -*-
#  This script is on fire!!! 

import _avs_win as dll
import numpy as np
import time as tm


def AVS_Status(avs_status):
    '''Used to check the return value of certain functions,
        should be == 0.
        If that is not the case, error is raised with given error code.'''
    
    error_dict = {-1: "ERR_INVALID_PARAMETER", -2: "ERR_OPERATION_NOT_SUPPORTED",
                    -3: "ERR_DEVICE_NOT_FOUND", -4: "ERR_INVALID_DEVICE_ID",
                    -5: "ERR_OPERATION_PENDING", -6: "ERR_TIMEOUT",
                    -8: "ERR_INVALID_MEAS_DATA", -9: "ERR_INVALID_SIZE",
                    -10: "ERR_INVALID_PIXEL_RANGE", -11: "ERR_INVALID_INT_TIME",
                    -12: "ERR_INVALID_COMBINATION", -14: "ERR_NO_MEAS_BUFFER_AVAIL",
                    -15: "ERR_UNKNOWN", -16: "ERR_COMMUNICATION",
                    -17: "ERR_NO_SPECTRA_IN_RAM", -18: "ERR_INVALID_DLL_VERSION",
                    -19: "ERR_NO_MEMORY", -20: "ERR_DLL_INITIALIZATION",
                    -21: "ERR_INVALID_STATE", -22: "ERR_INVALID_REPLY",
                    -24: "ERR_ACCESS", -25: "ERR_INTERNAL_READ",
                    -26: "ERR_INTERNAL_WRITE", -27: "ERR_ETHCONN_REUSE",
                    -28: "ERR_INVALID_DEVICE_TYPE", -29: "ERR_SECURE_CFG_NOT_READ",
                    -30: "ERR_UNEXPECTED_MEAS_RESPONSE",
                    -100: "ERR_INVALID_PARAMETER_NR_PIXEL",
                    -101: "ERR_INVALID_PARAMETER_ADC_GAIN",
                    -102: "ERR_INVALID_PARAMETER_ADC_OFFSET",
                    -110: "ERR_INVALID_MEASPARAM_AVG_SAT2",
                    -111: "ERR_INVALID_MEASPARAM_AVG_RAM",
                    -112: "ERR_INVALID_MEASPARAM_SYNC_RAM",
                    -112: "ERR_INVALID_MEASPARAM_LEVEL_RAM"}
    
    if avs_status == 0:   # ERR_SUCCESS
        return
    elif avs_status in error_dict:
        raise RuntimeError('Avantes driver failed: ' + error_dict[avs_status] +
                           ', error code ' + str(avs_status))
    raise RuntimeError('Avantes driver failed: error code ' + str(avs_status))
 
 
 
def MeasConfig_DefaultValues(handle):
    """Function to return an initialized version of the MeasConfigType.
        Can be modiefied but also passed on directly."""
        
    measconfig = dll.MeasConfigType()
    
    pixels = AVS_GetParameter(handle)['Detector_NrPixels']
    measconfig.m_StartPixel = 0
    measconfig.m_StopPixel = pixels - 1
    
    measconfig.m_IntegrationTime = 100
    measconfig.m_NrAverages = 1
    
    measconfig.m_IntegrationDelay = 0
    measconfig.m_CorDynDark_m_Enable = 0
    measconfig.m_CorDynDark_m_ForgetPercentage = 0
    measconfig.m_Smoothing_m_SmoothPix = 0
    measconfig.m_Smoothing_m_SmoothModel = 0
    measconfig.m_SaturationDetection = 0
    measconfig.m_Trigger_m_Mode = 0
    measconfig.m_Trigger_m_Source = 0
    measconfig.m_Trigger_m_SourceType = 0
    measconfig.m_Control_m_StrobeControl = 0
    measconfig.m_Control_m_LaserDelay = 0
    measconfig.m_Control_m_LaserWidth = 0
    measconfig.m_Control_m_LaserWaveLength = 0.0
    measconfig.m_Control_m_StoreToRam = 0
    
    return measconfig





def AVS_Init(port = 'USB'):
    '''
    Initializes the communication interface with the spectrometers.
    
    Parameters
    ----------
    port : str
        Define where to look for spectrometers: "USB", "Ethernet", or "both"

    Returns
    -------
    None.
    '''
    
    if port == 'USB':
        ret = dll.AVS_Init(0)
    elif port == 'Ethernet':
        ret = dll.AVS_Init(256)
    elif port == 'both':
        ret = dll.AVS_Init(-1) 
    else:
        raise ValueError('Specify port from "USB", "Ethernet", or "both"')
    
    if ret > 0:
        return ret
    elif ret == 0:
        raise RuntimeError('No spectrometers found.')
    else:
        AVS_Status(ret)



def AVS_Done():
    '''
    Closes the communication and releases internal storage.

    Returns
    -------
    None.

    ''' 
    
    ret = dll.AVS_Done()
    AVS_Status(ret)
    
    return



def AVS_UpdateUSBDevices():
    '''
    Internally checks the list of connected USB devices and returns the number 
    of devices attached. If AVS_Init() was called with port='both', the return 
    value also includes the number of ETH devices.

    Returns
    -------
    int
        Number of devices found.    
    '''
    
    ret = dll.AVS_UpdateUSBDevices()
    
    if ret > 0:
        return ret
    
    elif ret == 0:
        raise RuntimeError('No spectrometers found.')
        
    else:
        AVS_Status(ret)



def AVS_GetList():
    '''
    Returns device information for each spectrometer connected to the ports
    indicated at AVS_Init(). Wrapper function has been modified to 
    automatically update to correct listsize.
    
    Parameters
    ----------
    None.

    Returns
    -------
    tuple
        Tuple containing AvsIdentityType for each found device. Devices 
        are sorted by UserFriendlyName   
    '''   
    
    spec_list = dll.AVS_GetList()
    
    return spec_list



def AVS_Activate(deviceId):
    '''
    Activates spectrometer for communication
    
    Parameters
    ----------
    AvsIdentityType
        Device identifier.

    Returns
    -------
    int
        AvsHandle, handle to be used in subsequent function calls
    '''
    
    ret = dll.AVS_Activate(deviceId)
    return ret



def AVS_Deactivate(handle):
    '''
    Activates spectrometer for communication
    
    Parameters
    ----------
    int
        Device handle.

    Returns
    -------
    None.
    '''
    
    ret = dll.AVS_Deactivate(handle)
    
    if ret is False:
        raise ValueError('Invalid device handle.')
    
    return ret 



def AVS_GetParameter(handle):
    '''
    Returns the device information of the spectrometer..

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    dict
        Dictionary containing spectrometer configuration data 
        converted to native python types.
    '''
    
    structure = dll.AVS_GetParameter(handle)
    
    dictionary = {}
    for (name, dtype) in structure._fields_:
        newname = name.replace('m_', '')
        newname = newname.replace('_1', '1')
        newname = newname.replace('_2', '1')
        newname = newname.replace('_3', '1')
        content = structure.__getattribute__(name)
        if type(content) not in [int, float, bool, bytes]:
            content = np.array(content)
        dictionary[newname] = content
    
    if dictionary['Len'] == 0:
        raise RuntimeError('Could not read spectrometer parameters.')
    
    return dictionary



def AVS_GetLambda(handle):
    '''
    Returns the wavelength values corresponding to the pixels.

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    np.array
        Array of wavelength values for pixels (in nm).
    '''
    
    pixels = AVS_GetParameter(handle)['Detector_NrPixels']
    wavelengths = np.array(dll.AVS_GetLambda(handle))
    
    return wavelengths[:pixels]



def AVS_PrepareMeasure(handle, config=None):
    '''
    Prepares measurement on the spectrometer using the specificed configuration.

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer
    config : MeasConfigType, optional
        Measurement Configuration. 
        Defaults to MeasConfig_DefaultValues.

    Returns
    -------
    None.
    '''
    
    if config is None:
        config = MeasConfig_DefaultValues(handle)
    
    ret = dll.AVS_PrepareMeasure(handle, config)
    AVS_Status(ret)
    
    return



def AVS_Measure(handle, nummeas=-1, windowhandle=0):
    '''
    Starts measurement on the spectrometer.

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer
    nummeas : int
            number of measurements to do. 
            -1 is infinite, -2 is used to start Dynamic StoreToRam.
            Default is continuos acquisition.
    windowhandle : TYPE
        Window handle to notify application measurement result
        data is available. The library sends a Windows message to the window with 
        command WM_MEAS_READY, with SUCCESS, the number of scans that were saved in
        RAM (if enabled), or INVALID_MEAS_DATA as WPARM value and handle as LPARM 
        value. 
        0 to disable, which is default.

    Returns
    -------
    None.
    '''
    
    ret = dll.AVS_Measure(handle, windowhandle, nummeas)
    AVS_Status(ret)
    
    return



def AVS_StopMeasure(handle):
    '''
    Stops a running measurement.

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    None.
    '''    

    ret = dll.AVS_StopMeasure(handle)
    AVS_Status(ret)
    
    return



def AVS_PollScan(handle):
    '''
    Will show whether new measurement data are available

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    ret : bool
        0 = no data available or 1 = data available

    '''      
    
    ret = dll.AVS_PollScan(handle)
    return ret



def AVS_GetScopeData(handle):
    '''
    Returns the pixel values of the last performed measurement. Should be 
    called after the notification on AVS_Measure is triggered. 

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    int
        Timestamp: Ticks count at which last pixel of spectrum is received by microcontroller.
        Ticks are in 10µs units since spectrometer started.
    np.array
        pixel values of the spectrometer
    '''
    
    timestamp, spectrum = dll.AVS_GetScopeData(handle)
    pixels = AVS_GetParameter(handle)['Detector_NrPixels']
    
    return timestamp, np.array(spectrum[:pixels])



def AVS_GetSaturatedPixels(handle):
    '''
    Returns the saturation values of the last performed measurement. Should be 
    called after AVS_GetScopeData. 
    
    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer

    Returns
    -------
    np.array
        Array of bool indicating if pixels are saturated.
    '''

    saturated = AVS_GetSaturatedPixels(handle)
    pixels = AVS_GetParameter(handle)['Detector_NrPixels']
    
    return np.array(saturated[:pixels], dtype=bool)





def acquire_single_spectrum(handle, config=None):
    '''
    Simple function to acquire a single spectrum with the provided 
    measurement configuration.

    Parameters
    ----------
    handle : int
        the AvsHandle of the spectrometer
    config : MeasConfigType, optional
        Measurement Configuration. 
        Defaults to MeasConfig_DefaultValues.

    Returns
    -------
    float
        Timestamp: Ticks count at which last pixel of spectrum is received by microcontroller.
        Ticks are in seconds since spectrometer started.
    np.array
        pixel values of the spectrometer

    '''
    
    AVS_PrepareMeasure(handle, config)
    AVS_Measure(handle, nummeas=1, windowhandle=0)
    dataready = False
    while dataready == False:
        tm.sleep(0.001)
        dataready = dll.AVS_PollScan(handle)
    
    timestamp, data = AVS_GetScopeData(handle)
    return timestamp/100000, data
