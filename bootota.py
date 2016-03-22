import serial
import time
import math
import sys
def send(z):
    opcode = ''
    for abc in bytearray(z,"UTF-8"):
        ser.write(chr(abc))
        byte = ser.read()
        if byte == '':
            return ''
        opcode+=byte
    return opcode
def asciitohex(ch):
    if (ord(ch)>=ord('0') and ord(ch)<=ord('9')):
        return (ord(ch)-ord('0'))
    else:
        return ((ord(ch)-ord('A') )+ 10)


def hextodecimal(ptr,no):
    dec=0
    i=0
    while(i<no):
        dec +=((16**(no-i-1)) * ptr[i])
        i+=1
    return dec

def boot(ser, machine_blocks, to_print,per):
    machine_bytes2=[]
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

def parseintelhex(st):
#hexa = [1,0]
#abc = hextodecimal(hexa,2)
    byte=[]
    address=[]
    record=[]
    opcode=""
    _byte = 0
    _address=0
    _record=0
    _count =0

    f = open(st,'rb')
    s= f.read()
    i=0
    ch=0

    machine_bytes=[]
    machine_instr=[]
    while(i<len(s)):

        i+=1
        ch = asciitohex(s[i])
        byte.append(ch)
        i+=1
        ch=asciitohex(s[i])
        byte.append(ch)

        i+=1
        ch=asciitohex(s[i])
        address.append(ch)
        i+=1
        ch=asciitohex(s[i])
        address.append(ch)
        i+=1
        ch=asciitohex(s[i])
        address.append(ch)
        i+=1
        ch=asciitohex(s[i])
        address.append(ch)
    
        i+=1
        ch=asciitohex(s[i])
        record.append(ch)
        i+=1
        ch=asciitohex(s[i])
        record.append(ch)
    
        _count = hextodecimal(byte,2)
        _address = hextodecimal(address,4)
        _record = hextodecimal(record,2)
    
        if(_record==0):
            _byte+=_count

            while(_count>0):
            
                i+=1
                #ch=asciitohex(s[i])
                opcode+=s[i]
                i+=1
                #ch=asciitohex(s[i])
                opcode+=s[i]
                #op = hextodecimal(opcode,2)
                _count-=1
                #print ("%x\t%x" %(_address,op))
                machine_bytes.append((opcode))
            
                _address+=1
                opcode=""
        elif (_record==1):
            break
        while(s[i]!='\n'):
            i+=1
        i+=1
        address[:] =[]
        record[:] =[]
        byte[:] =[]
            
    if (_byte%128!=0):
        pad = 128*int(math.ceil(float(_byte)/float(128))) - _byte
    m=1
    while m<=pad:
        machine_bytes.append("FF")
        m+=1
    per = len(machine_bytes)
    per = int(per/30)
    to_print=1
    machine_blocks=[]
    temp=[]
    i=0
    k=0
    j=len(machine_bytes)
    print "No. of machine instructions to write: %u" %(_byte/2)
    print "No. of bytes to write: %u"%(_byte)
    while(i<j):
        while i<(k+128):
            temp.append(machine_bytes[i])
            i+=1
        k=i
        machine_blocks.append(list(temp))
        temp[:]=[]

    opcode =''
    machine_bytes2=[]

ser = serial.Serial('COM4',500000,timeout=4)
boot(ser, machine_blocks, to_print, per)
ser.write('R')
boot(ser, machine_blocks,to_print, per)
ser.close()
m = len(machine_bytes)
m/=2
print    
print "Number of machine blocks: %u" %len(machine_blocks)
print "No. of bytes written: %u" %len(machine_bytes)
print "No. of words written: %u" %m
print "Success!"
