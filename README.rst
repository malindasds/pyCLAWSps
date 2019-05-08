pyCLAWSps
--------
python script for the Hamamatsu c11204-01/02 power supply

Installation


To use
Simply import module and initialise with commands

    >>> import pyCLAWSps
    >>> pyCLAWSps.init()

Functions

init():                 Initialise the c11204 power supply. Make sure to connect power supply to the PC before initializing
printMonitorInfo():     Prints information on the power supply status, voltage and current values
getPowerInfo():         Returns the power supply voltage and current values.
    Returns
    -------
    tuple   (voltage, current)
            Voltage in Volts and current in mA.
setHVOff():             Set power supply High Voltage OFF
setHVOn():              Set power supply High Voltage ON
reset():                Reset the power supply
setVoltage(voltage_dec):Sets the high voltage output to the voltage specified.
    Arguments
    ---------
    voltage_dec : float
        applied voltage

        NOTE -  The applied voltage can be set upto 90 V by c11204 power supply.
                Change the upper voltage limit (V_lim_upper) as required by the MPPC in use
getVoltage():           Returns power supply voltage
    Returns
    -------
    float
        Voltage in Volts
getCurrent():   Returns power supply current
    Returns
    -------
    float
        Current in mA
printStatus():          Prints status information on the power supply (similar to getMonitorInfo()) but without voltage and current values
    close():            Close serial port
