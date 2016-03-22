
#using Pyserial to communicate with MCU


import serial
import time
import sys
import Intelhex


def send(z):
    opcode = ''
    for abc in bytearray(z,"UTF-8"):
        ser.write(chr(abc))
        byte = ser.read()
        if byte == '':
            return ''
        opcode+=byte
    return opcode

machine_blocks = Intelhex.intelhex("Middleware.hex")
count123=0
for x in machine_blocks:
    count123 += len(x)
per = count123
per = int(per/30)
to_print=1
opcode =''
machine_bytes2=[]

ser = serial.Serial('COM4',500000,timeout=4)
byte=''
byte=ser.read()
if(byte!='K'):
    print"MCU not ready"
    ser.close()
else:
    print "Writing: |",
    #print byte
    #machine_bytes2=[]
    k=0
    flag=False
    while k<len(machine_blocks) and flag ==False:
        #print machine_blocks[k]
        #print
        ser.write('S')
        byte=ser.read()
        #print byte
        if (byte=='' or byte!='S'):
            #print "breaking from here"
            flag=True
            break
        for z in machine_blocks[k]:
            opcode = send(z)
            if (to_print%per==0):
                print "#",
            to_print+=1
            if opcode == '':
                flag = True
                break
            #print opcode,
            machine_bytes2.append(opcode)
            opcode=''
        if(flag==False):
            if(machine_blocks[k]==machine_bytes2):
                k+=1
            else:
                ser.write('E')
                print ("Error in transmission of block # %u. Retransmitting..." %(k+1))
        machine_bytes2[:]=[]
    if flag==True:
        print "MCU busy/not responding. Exiting..."         #Unsuccessful transmission
        ser.close()
        sys.exit(1)
        
    ser.write('F')                #Successful transmission
    byte= ser.read()
    #print byte
    ser.close()
    print    
    print "Number of machine blocks: %u" %len(machine_blocks)
    print "No. of bytes written: %u" %count123
    m = count123
    m/=2
    print "No. of words written: %u" %m
    print "Success!"
    
