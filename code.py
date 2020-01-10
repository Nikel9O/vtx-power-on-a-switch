import board
import pulseio
import busio
import time
from digitalio import DigitalInOut, Direction, Pull

###########################################
#VTX_PROTOCOL#
###########################################
vtx = "SA21" #type of vtx used: "SA21": smart audio v2.1, "TRAMP": Irc Tramp
###########################################
#VTX_FREQUENCIES#
###########################################
band = [5733,5752,5771,5790,5809,5828,5847,5866]
###########################################
#POWER TABLES #comment the unused protocol
###########################################
#for SA 2.1 power level in db | 128 & 0xFF
#unifying 32 pro
'''
powers = [14 | 128 & 0xFF,
          20 | 128 & 0xFF,
          26 | 128 & 0xFF]
'''
#unifying hv race 2
powers = [13 | 128 & 0xFF,
          20 | 128 & 0xFF,
          26 | 128 & 0xFF]
#for IRC TRAMP
#powers = [25,50,100]
###########################################
#SERVO LEVELS = INPUT FROM Flight controller
###########################################
servo_levels = [1000,1500,2000] #1000 = level 1 1500 = mid level 2000 = high level
###########################################
###########################################
###########################################

def tx_packet(packet,xuart):
    xuart.write(bytes(packet)) #bytearray
    print("sent",packet)

###########################################
#SMART AUDIO#
###########################################
def sa_command(sa_command,sa_payload,sa_uart):
    if sa_payload is not None: #creo il payload (se è nullo non lo metto) altrimenti se è un byte ne metto uno altrimenti 2
        if sa_payload & 0xFF == sa_payload:
            pld = [sa_payload]
        else:
            pld = [(sa_payload >> 8) & 0xFF,sa_payload & 0xFF]
    else:
        pld = []
    cmd = [0x00,0xAA,0x55]
    cmd.append(((sa_command << 1) | 0x01) & 0xFF)
    cmd.append(len(pld) & 0xFF)
    for p in pld:
        cmd.append(p & 0xFF)
    cmd.append(sa_crc8(cmd[1:],len(cmd[1:])))
    cmd.append(0x00)
    tx_packet(cmd,sa_uart)

def sa_crc8(data,xlen):
    POLYGEN = 0xd5
    crc = 0x00
    currByte = 0
    for i in range(0,xlen):
        currByte = data[i]
        crc ^= currByte & 0xFF
        for j in range(0,8):
            if (crc & 0x80)& 0xFF != 0:
                crc = ((crc << 1)& 0xFF ^ POLYGEN & 0xFF)& 0xFF
            else:
                crc <<= 1 & 0xFF
    return crc & 0xFF

def sa_init(version): #version is here for future implementation of older standard
    sa_power_levels = {"command":0x02,"payload":powers}
    sa_frequencies  = {"command":0x04,"payload":band}
    sa_unlock       = {"command":0x05,"payload":0x08}
    sa_get_settings = {"command":0x01,"payload":None}
    sa_uart = busio.UART(board.TX, board.RX, baudrate=4900,bits=8,parity=None,stop=2,timeout=1,receiver_buffer_size=64)
    time.sleep(1)
    sa_command(sa_unlock["command"],sa_unlock["payload"],sa_uart)
    sa_uart.reset_input_buffer()
    response = sa_uart.read()
    if response is not None: #TEMP! do something with the answer?
        print([int(i) for i in response])
    time.sleep(1)
    return sa_power_levels,sa_frequencies,sa_unlock,sa_get_settings,sa_uart

###########################################
#IRC_TRAMP#
###########################################
def tr_init():
    tr_power_levels = {"command":0x46,"payload":powers}
    tr_frequencies  = {"command":0x50,"payload":band}
    tr_unlock       = {"command":None,"payload":None}
    tr_get_settings = {"command":0x76,"payload":None}
    tr_uart = busio.UART(board.TX, board.RX, baudrate=9600,bits=8,parity=None,stop=None,timeout=1,receiver_buffer_size=64)
    return tr_power_levels,tr_frequencies,tr_unlock,tr_get_settings,tr_uart

def tr_command(tr_command,tr_payload,tr_uart):
    cmd = [15,
           tr_command, #command
           tr_payload & 0xFF, #command payload byte 1
           tr_payload >> 8 & 0xFF, #command payload byte 2
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           0x00,
           (tr_command + tr_payload & 0xFF + tr_payload >> 8 & 0xFF)& 0xFF] #checksum (sum cmd[1:] & 0xFF)
    tx_packet(cmd,tr_uart)


###################################
#non-VTX protocol related functions
###################################
def init(vtx_type):
    if vtx_type == "SA21":
        return sa_init(vtx_type)
    elif vtx_type == "TRAMP":
        return tr_init()
    else:
        print("not implemented yet")

def set_power(power_levels,uart,power_index):
    if vtx == "SA21":
        return sa_command(power_levels["command"],power_levels["payload"][int(power_index)],uart)
    elif vtx == "TRAMP":
        return tr_command(power_levels["command"],power_levels["payload"][int(power_index)],uart)
    else:
        print("not implemented yet")

def set_freq(frequencies,uart,freq_index):
    if vtx == "SA21":
        return sa_command(frequencies["command"],frequencies["payload"][int(freq_index)],uart)
    elif vtx == "TRAMP":
        return tr_command(frequencies["command"],frequencies["payload"][int(freq_index)],uart)
    else:
        print("not implemented yet")

###################################
#MAIN LOOP#
###################################


#print("booting")
#input("press any key")
time.sleep(5) #wait 5 second from power on to boot the vtx
power_levels,frequencies,unlock,get_settings,uart = init(vtx)
old_status = servo_levels[0] #init a the lowest servo level
pulses = pulseio.PulseIn(board.A0,maxlen=10,idle_state=False)

while True:
    while len(pulses) < 10:
        pass
    pulses_2 = [pulses[i] for i in range(0,10) if pulses[i] < 3000] #clean useless values (1 out of 2 is inverted 18000-19000)
    average_val = sum(pulses_2)/len(pulses_2)
    actual_val  = min(servo_levels, key=lambda x:abs(x-average_val))
    #print("avg ",average_val)
    #print("act ",actual_val)
    if old_status != actual_val:
        #print("value changed from",old_status,"to ",actual_val)
        old_status = actual_val
        #qui settare la potenza!
        power_index = int(round(float(servo_levels.index(actual_val)/(len(servo_levels)-1)) * (len(power_levels["payload"])-1),0))
        #print("power index ",power_index)
        set_power(power_levels,uart,power_index)
        uart.reset_input_buffer()
        response = uart.read()
    pulses.clear()
    time.sleep(0.5)
