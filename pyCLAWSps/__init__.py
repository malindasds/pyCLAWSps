"""
Python Code for Power Supply Hamamatsu c11204-01/02
Malinda de Silva
Licence = GNU General Public License v3.0
"""

import serial
import serial.tools.list_ports
import binascii
import numpy as np

def init():
    "Initialise the c11204 power supply. Make sure to connect power supply to the PC before initializing"
    # VARIABLES
    V_conversion=1.812*10**(-3) 	# voltage conversion factor
    I_conversion=4.980*10**(-3)     # current conversion factor (mA)

    # FIXED VALUES
    STX = '02' 			            # start of text
    ETX = '03' 			            # end of text
    CR = '0D' 			            # delimiter

    #USER DEFINED VARIABLES
    V_lim_upper = 60                # Upper high voltage limit in Volts
    ''' NOTE - The applied voltage can be set upto 90 V by c11204 power supply.
               Change the upper voltage limit (V_lim_upper) as required by the MPPC in use'''

    # OPEN SERIAL PORT
    ports = list(serial.tools.list_ports.comports())
    if len(ports) ==0:
        self.logger.warning("Could not find any serial device!")
    for p in ports:
        if "CP2102 USB to UART Bridge Controller" in p[1]:
            prt = p[0]
    try:
        ser = serial.Serial(prt)            # open serial port
        ser.baudrate = 38400                # set baudrate
        ser.parity = serial.PARITY_EVEN     # set parity
        ser.stopbits=serial.STOPBITS_ONE
        ser.bytesize=serial.EIGHTBITS
        print(ser.name)                     # check which port was really used
    except NameError:
        print("No CP2102 USB to UART Bridge Controller was found. Check USB connection")


def _convert(command):
    # Converts command to hex form needed for serial data transfer
    com = command.encode(encoding='utf-8', errors='strict')
    command_str = binascii.hexlify(com).decode('utf-8')
    sum_command = sum(bytearray(com))
    return (command_str, sum_command)

def _checksum(sum_command,sum_voltage):
    #CHECKSUM CALCULATION
    CS=hex(int(STX,16)+sum_command+int(ETX,16)+sum_voltage)
    CS=CS.lstrip('0x')
    CS=CS.upper()
    CS=CS[-2:]
    CS_str,CS_sum=_convert(CS)
    return(CS_str,CS_sum)

def _checkerror(rx):
    # Error Commands
    if rx == b'0001':
        print("UART communication error: Parity error, overrun error, framing error")
    if rx == b'0002':
        print("Timeout error: This indicates that the CR has not been received within 1000ms of receiving the STX. The received packet is discarded.")
    if rx == b'0003':
        print("Syntax error: The beginning of the received command is other than STX, which indicates the length of the command or 256byte.")
    if rx == b'0004':
        print("Checksum error: This indicates that the checksum does not match")
    if rx == b'0005':
        print("Command error: This indicates that it is an undefined command")
    if rx == b'0006':
        print("Parameter error: This indicates that the codes other than ASCII code(0~F) is in the parameter")
    if rx == b'0007':
        print("Parameter size error: This indicates that the data length of the parameter is outside the specified length")

def _checkstatus(rx):
    # Status information
    rx_bin = bin(int(str(rx[4:8])[2:5]))
    if rx_bin[2] == '0':
        print("High Voltage Output      :   OFF")
    else:
        print("High Voltage Output      :   ON")

    if rx_bin[3] == '0':
        print("Over-current protection  :   No")
    else:
        print("Over-current protection  :   Yes")

    if rx_bin[4] == '0':
        print("Current Value            :   Within Specifications")
    else:
        print("Current Value            :   Outside Specifications")

    if rx_bin[5] == '0':
        print("MPPC temparture sensor   :   Disconnected")
    else:
        print("MPPC temparture sensor   :   Connected")

    if rx_bin[6] == '0':
        print("MPPC temparture sensor   :   Within Specifications")
    else:
        print("MPPC temparture sensor   :   Outside Specifications")

    if rx_bin[7] == '0':
        print("Temperature Correction   :   Invalid")
    else:
        print("Temperature Correction   :   Effectiveness")

##### COMMANDS OF POWER SUPPLY ####

def printMonitorInfo():
    "Prints information on the power supply status, voltage and current values"
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HPO')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(28)
    if rx[1:4] == b'hpo':
        volt_out = (int(rx[12:16], 16) * V_conversion)
        mA_out   = (int(rx[16:20], 16) * I_conversion)

        _checkstatus(rx)
        print("High Voltage Output      :   {} V".format(volt_out))
        print("Output current           :   {} mA".format(mA_out))
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def getPowerInfo():
    '''
    Returns the power supply voltage and current values.

    Returns
    -------
    tuple
        (voltage, current)
        Voltage in Volts and current in mA.
    '''
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HPO')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(28)
    if rx[1:4] == b'hpo':
        volt_out= (int(rx[12:16], 16) * V_conversion)
        mA_out = (int(rx[16:20], 16) * I_conversion)
        return (volt_out,mA_out)
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def setHVOff():
    "Set power supply High Voltage OFF"
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HOF')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hof':
        pass
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def setHVOn():
    "Set power supply High Voltage ON"
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HON')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hon':
        pass
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def reset():
    "Reset the power supply"
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HRE')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hre':
        pass
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def setVoltage(voltage_dec):
    '''
    Sets the high voltage output to the voltage specified.

    Arguments
    ---------
    voltage_dec : float
        applied voltage

        NOTE -  The applied voltage can be set upto 90 V by c11204 power supply.
                Change the upper voltage limit (V_lim_upper) as required by the MPPC in use
    '''
    ser.flushInput()
    ser.flushOutput()
    if voltage_dec > V_lim_upper:
        print ("Voltage is too high")
    elif  voltage_dec < 40:
        print ("Voltage is too low")
    else:
        voltage_conv=float(voltage_dec)/V_conversion
        voltage = int(round(voltage_conv))
        voltage_hex=hex(voltage)                 #convert voltage from decimal to hexadecimal number
        voltage_hex=voltage_hex.lstrip('0x')
        voltage_str,sum_voltage=_convert(voltage_hex)
        command_str,sum_command=_convert('HBV')
        CS_str,CS_sum = _checksum(sum_command,sum_voltage)

        #FINAL COMMAND
        command_tosend = STX + command_str + voltage_str + ETX + CS_str + CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        # print("send command:" + command_x)
        tx = ser.write(command_x.encode())
        rx = ser.read(8)
        if rx[1:4] == b'hbv':
            pass
        elif rx[1:4] == b'hxx':
            return(_checkerror(rx[4:8]))
        else:
            print("An error has occured")

def getVoltage():
    '''
    Returns power supply voltage

    Returns
    -------
    float
        Voltage in Volts
    '''
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HGV')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hgv':
        volt_out= (int(rx[4:8], 16) * V_conversion)
        return(volt_out)
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def getCurrent():
    '''
    Returns power supply current

    Returns
    -------
    float
        Current in mA
    '''
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HGC')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hgc':
        I_out= (int(rx[4:8], 16) * I_conversion)
        return(I_out)
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def printStatus():
    "Prints status information on the power supply (similar to getMonitorInfo()) but without voltage and current values"
    ser.flushInput()
    ser.flushOutput()
    command_str,sum_command=_convert('HGS')
    CS_str,CS_sum = _checksum(sum_command,0)

    #FINAL COMMAND
    command_tosend = STX + command_str + ETX + CS_str + CR
    command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
    tx = ser.write(command_x.encode())
    rx = ser.read(8)
    if rx[1:4] == b'hgs':
        _checkstatus(rx)
    elif rx[1:4] == b'hxx':
        return(_checkerror(rx[4:8]))
    else:
        print("An error has occured")

def close():
    "Close serial port"
    ser.close()
