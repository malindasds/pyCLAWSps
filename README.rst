*********
pyCLAWSps
*********

python 3 script for the Hamamatsu c11204-01/02 power supply

Prerequisites
""""""""""""""

This module requires **numpy** and **pySerial** and will be installed automatically

Installation
"""""""""""""

Install this package by the following command on a console::

  pip install pyCLAWSps

Compatibility
""""""""""""""

Tested with only python 3

Using the package
"""""""""""""""""""
To use this code simply import module and initialise with commands. Make sure to connect power supply to the PC before initializing

    >>> from pyCLAWSps import CLAWSps
    >>> ps = CLAWSps()
    >>> ps.printStatus()

Functions
""""""""""

* **printMonitorInfo()**   - Prints information on the power supply status, voltage (V) and current (mA) values
* **getPowerInfo()**       - Returns the power supply voltage (V) and current (mA) values as tuple
* **setHVOff()**           - Set power supply High Voltage OFF
* **setHVOn()**            - Set power supply High Voltage ON
* **reset()**              - Reset the power supply
* **setVoltage(voltage_dec)** - Sets the high voltage output to the voltage specified (V)
* **getVoltage()**         - Returns power supply voltage in Volts
* **getCurrent()**         - Returns power supply current in mA
* **printStatus()**        - Prints status information on the power supply (similar to 'getMonitorInfo()') but without voltage and current values
* **close()**              - Close serial port

NOTE -  The applied voltage can be set upto 90 V by c11204 power supply. Change the upper voltage limit (*self.V_lim_upper* in **pyCLAWSps/__init__**) as required by the MPPC in use. Default is set to 60 V
