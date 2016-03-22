#Device reprogramming - An 8 bit device is sending the .hex file to another device to reprogram it using the PC as an intermediary node.
# This Python script receives the .hex file from the source and orwards it to the destination device. 


import bluetooth
def decimal_to_ascii(abc):
    st=''
    if (abc>=0 and abc<=9):
        
        st+=chr(abc + ord('0'))
        
    elif (abc>=10 and abc<=15):
        
        st += chr(abc-10 + ord('A'))
        
    else:
        
        i=abc/16
        st += decimal_to_ascii(i)
        i=abc%16
        st += decimal_to_ascii(i)

    return st

def send(z):
    opcode = ''
    for abc in bytearray(z,"UTF-8"):
        sock.send(chr(abc))
        byte = sock.recv(1)
        if byte == '':
            return ''
        opcode+=byte
    return opcode


bd_addr = "20:15:07:27:84:86"

port = 1

sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
bluetooth.BluetoothSocket.settimeout(sock,5)
print "Connecting to bluetooth device"
sock.connect((bd_addr, port))
print "Connected"
byte=''
i=0
j=0
sock.send('R')
machine_list1=[]
machine_list=[]
while i<384:
    byte = sock.recv(1)
    #print ord(byte)
    machine_list1.append(ord(byte))
    i+=1
sock.close()
for z in machine_list1:
    st = decimal_to_ascii(z)
    if len(st)==1:
        st2 = '0'
        st2 += st
        st = st2
    machine_list.append(st)
#print machine_list


machine_blocks=[]
temp=[]     
i=0
k=0
j=len(machine_list)
    #print "No. of machine instructions to write: %u" %(_byte/2)
    #print "No. of bytes to write: %u"%(_byte)
while(i<j):
    while i<(k+128):
        temp.append(machine_list[i])
        i+=1
    k=i
    machine_blocks.append(list(temp))
    temp[:]=[]

print machine_blocks    



bd_addr = "20:15:07:27:88:49"

port = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM)
bluetooth.BluetoothSocket.settimeout(sock,10)
print "Establishing connection with bluetooth device"

sock.connect((bd_addr, port))

print "Connected"
#machine_blocks = Intelhex.intelhex("Bluetooth.hex")
#print machine_blocks
count123=0
for x in machine_blocks:
    count123 += len(x)
per = count123
per = int(per/30)
to_print=1
opcode =''
machine_bytes2=[]
byte=''

#time.sleep(4)
sock.send('R')

byte=sock.recv(1)
#print byte
if(byte!='K'):
    print"MCU not ready"
    sock.close()
else:
    print "Writing: |",
    #print byte
    #machine_bytes2=[]
    k=0
    flag=False
    while k<len(machine_blocks) and flag ==False:
#        print "Machine_blocks"
#        print machine_blocks[k]
#        print "End of Machine_blocks"
        sock.send('S')
        byte=sock.recv(1)
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
                #print machine_bytes2
                k+=1
            else:
                sock.send('E')
                print ("Error in transmission of block # %u. Retransmitting..." %(k+1))
        machine_bytes2[:]=[]
    if flag==True:
        print "MCU busy/not responding. Exiting..."         #Unsuccessful transmission
        sock.close()
        sys.exit(1)
    #print "Out of loop transmitting 'F'...."    
    sock.send('X')                #Successful transmission
    byte= sock.recv(1)
#    print byte
    sock.close()
    print    
    print "Number of machine blocks: %u" %len(machine_blocks)
    print "No. of bytes written: %u" %count123
    m = count123
    m/=2
    print "No. of words written: %u" %m
    print "Success!"
