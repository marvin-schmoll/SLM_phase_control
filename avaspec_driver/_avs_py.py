# -*- coding: utf-8 -*-
import _avs_win as dll
import numpy as np



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
                    -24: "ERR_ACCESS"}
    
    if avs_status == 0:   # ERR_SUCCESS
        return
    elif avs_status in error_dict:
        raise RuntimeError('Avantes driver failed: ' + error_dict[avs_status] +
                           ', error code ' + str(avs_status))
    raise RuntimeError('Avantes driver failed: error code ' + str(avs_status))
 
 
 
def MeasConfig_DeafaultValues(handle):
    """Function to return an initialized version of the MeasConfigType.
        Can be modiefied but also passed on directly."""
        
    measconfig = dll.MeasConfigType()
    
    pixels = dll.AVS_GetParameter(handle).m_Detector_m_NrPixels
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
    """
    Closes the communication and releases internal storage.
    """

    ret = dll.AVS_Done()
    AVS_Status(ret)
    
    return



def AVS_UpdateUSBDevices():
    """
    Internally checks the list of connected USB devices and returns the number 
    of devices attached. If AVS_Init() was called with port='both', the return 
    value also includes the number of ETH devices.
    
     Parameters
    ----------
    None.

    Returns
    -------
    int
        Number of devices found.    
    """
    
    ret = dll.AVS_UpdateUSBDevices()
    
    if ret > 0:
        return ret
    
    elif ret == 0:
        raise RuntimeError('No spectrometers found.')
        
    else:
        AVS_Status(ret)



def AVS_GetList():
    """
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
    """   
    
    spec_list = dll.AVS_GetList()
    
    return spec_list



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
    
    pixels = dll.AVS_GetParameter(handle).m_Detector_m_NrPixels
    wavelengths = np.array(dll.AVS_GetLambda(handle))
    
    return wavelengths[:pixels]



def AVS_Measure():
    pass