"""
Python Code for Power Supply Hamamatsu c11204-01/02
Malinda de Silva
Licence = GNU General Public License v3.0
"""

import serial
import serial.tools.list_ports
import binascii
import numpy as np

class CLAWSps():
    def __init__(self):
        self.ser = 0
        "Initialise the c11204 power supply. Make sure to connect power supply to the PC before initializing"
        # VARIABLES
        self.V_conversion=1.812*10**(-3) 	# voltage conversion factor
        self.I_conversion=4.980*10**(-3)     # current conversion factor (mA)

        # FIXED VALUES
        self.STX = '02' 			            # start of text
        self.ETX = '03' 			            # end of text
        self.CR = '0D' 			            # delimiter

        #USER DEFINED VARIABLES
        self.V_lim_upper = 60                # Upper high voltage limit in Volts
        ''' NOTE - The applied voltage can be set upto 90 V by c11204 power supply.
                   Change the upper voltage limit (self.V_lim_upper) as required by the MPPC in use'''

        # OPEN SERIAL PORT
        ports = list(serial.tools.list_ports.comports())
        if len(ports) ==0:
            self.logger.warning("Could not find any serial device!")
        for p in ports:
            if "CP2102 USB to UART Bridge Controller" in p[1]:
                prt = p[0]
        try:
            self.ser = serial.Serial(prt)            # open serial port
            self.ser.baudrate = 38400                # set baudrate
            self.ser.parity = serial.PARITY_EVEN     # set parity
            self.ser.stopbits=serial.STOPBITS_ONE
            self.ser.bytesize=serial.EIGHTBITS
            print(self.ser.name)                     # check which port was really used
        except NameError:
            print("No CP2102 USB to UART Bridge Controller was found. Check USB connection")


    def _convert(self, command):
        # Converts command to hex form needed for serial data transfer
        com = command.encode(encoding='utf-8', errors='strict')
        command_str = binascii.hexlify(com).decode('utf-8')
        sum_command = sum(bytearray(com))
        return (command_str, sum_command)

    def _checksum(self, sum_command,sum_voltage):
        #CHECKSUM CALCULATION
        CS=hex(int(self.STX,16)+sum_command+int(self.ETX,16)+sum_voltage)
        CS=CS.lstrip('0x')
        CS=CS.upper()
        CS=CS[-2:]
        CS_str,CS_sum=self._convert(CS)
        return(CS_str,CS_sum)

    def _checkerror(self, rx):
        # Error Commands
        if rx == b'0001':
            print("UART communication error: Parity error, overrun error, framing error")
        if rx == b'0002':
            print("Timeout error: This indicates that the self.CR has not been received within 1000ms of receiving the self.STX. The received packet is discarded.")
        if rx == b'0003':
            print("Syntax error: The beginning of the received command is other than self.STX, which indicates the length of the command or 256byte.")
        if rx == b'0004':
            print("Checksum error: This indicates that the checksum does not match")
        if rx == b'0005':
            print("Command error: This indicates that it is an undefined command")
        if rx == b'0006':
            print("Parameter error: This indicates that the codes other than ASCII code(0~F) is in the parameter")
        if rx == b'0007':
            print("Parameter size error: This indicates that the data length of the parameter is outside the specified length")

    def _checkstatus(self, rx):
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

    def printMonitorInfo(self):
        "Prints information on the power supply status, voltage and current values"
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HPO')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(28)
        if rx[1:4] == b'hpo':
            volt_out = (int(rx[12:16], 16) * self.V_conversion)
            mA_out   = (int(rx[16:20], 16) * self.I_conversion)

            self._checkstatus(rx)
            print("High Voltage Output      :   {} V".format(volt_out))
            print("Output current           :   {} mA".format(mA_out))
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def getPowerInfo(self):
        '''
        Returns the power supply voltage and current values.

        Returns
        -------
        tuple
            (voltage, current)
            Voltage in Volts and current in mA.
        '''
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HPO')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(28)
        if rx[1:4] == b'hpo':
            volt_out= (int(rx[12:16], 16) * self.V_conversion)
            mA_out = (int(rx[16:20], 16) * self.I_conversion)
            return (volt_out,mA_out)
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def setHVOff(self):
        "Set power supply High Voltage OFF"
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HOF')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hof':
            pass
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def setHVOn(self):
        "Set power supply High Voltage ON"
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HON')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hon':
            pass
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def reset(self):
        "Reset the power supply"
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HRE')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hre':
            pass
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def setVoltage(self, voltage_dec):
        '''
        Sets the high voltage output to the voltage specified.

        Arguments
        ---------
        voltage_dec : float
            applied voltage

            NOTE -  The applied voltage can be set upto 90 V by c11204 power supply.
                    Change the upper voltage limit (self.V_lim_upper) as required by the MPPC in use
        '''
        self.ser.flushInput()
        self.ser.flushOutput()
        if voltage_dec > self.V_lim_upper:
            print ("Voltage is too high")
        elif  voltage_dec < 40:
            print ("Voltage is too low")
        else:
            voltage_conv=float(voltage_dec)/self.V_conversion
            voltage = int(round(voltage_conv))
            voltage_hex=hex(voltage)                 #convert voltage from decimal to hexadecimal number
            voltage_hex=voltage_hex.lstrip('0x')
            voltage_str,sum_voltage=self._convert(voltage_hex)
            command_str,sum_command=self._convert('HBV')
            CS_str,CS_sum = self._checksum(sum_command,sum_voltage)

            #FINAL COMMAND
            command_tosend = self.STX + command_str + voltage_str + self.ETX + CS_str + self.CR
            command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
            # print("send command:" + command_x)
            tx = self.ser.write(command_x.encode())
            rx = self.ser.read(8)
            if rx[1:4] == b'hbv':
                pass
            elif rx[1:4] == b'hxx':
                return(self._checkerror(rx[4:8]))
            else:
                print("An error has occured")

    def getVoltage(self):
        '''
        Returns power supply voltage

        Returns
        -------
        float
            Voltage in Volts
        '''
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HGV')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hgv':
            volt_out= (int(rx[4:8], 16) * self.V_conversion)
            return(volt_out)
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def getCurrent(self):
        '''
        Returns power supply current

        Returns
        -------
        float
            Current in mA
        '''
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HGC')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hgc':
            I_out= (int(rx[4:8], 16) * self.I_conversion)
            return(I_out)
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def printStatus(self):
        "Prints status information on the power supply (similar to getMonitorInfo()) but without voltage and current values"
        self.ser.flushInput()
        self.ser.flushOutput()
        command_str,sum_command=self._convert('HGS')
        CS_str,CS_sum = self._checksum(sum_command,0)

        #FINAL COMMAND
        command_tosend = self.STX + command_str + self.ETX + CS_str + self.CR
        command_x =  "".join(chr(int(command_tosend[n : n+2],16)) for n in range(0, len(command_tosend), 2))
        tx = self.ser.write(command_x.encode())
        rx = self.ser.read(8)
        if rx[1:4] == b'hgs':
            self._checkstatus(rx)
        elif rx[1:4] == b'hxx':
            return(self._checkerror(rx[4:8]))
        else:
            print("An error has occured")

    def close(self):
        "Close self.serial port"
        self.ser.close()
