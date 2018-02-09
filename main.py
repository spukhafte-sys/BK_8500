


import serial


# Set DC load to remote mode.
import serial
length_packet = 26 # Number of bytes in a packet
 def DumpCommand(bytes):
     assert(len(bytes) == length_packet)
     header = " "*3
     print header,
     for i in xrange(length_packet):
         if i % 10 == 0 and i != 0:
             print
             print header,
         if i % 5 == 0:
             print " ",
         s = "%02x" % ord(bytes[i])
         if s == "00":
             s = chr(250)*2
         print s,
print
def CalculateChecksum(cmd):
assert((len(cmd) == length_packet - 1) or (len(cmd) == length_packet)) checksum = 0
for i in xrange(length_packet - 1):
         checksum += ord(cmd[i])
     checksum %= 256
     return checksum
def main():
port = 3 # COM4 for my computer
baudrate = 38400
sp = serial.Serial(port, baudrate) # Open a serial connection # Construct a set to remote command
cmd = chr(0xaa) + chr(0x00) + chr(0x20) # First three bytes cmd += chr(0x01) + chr(0x00)*(length_packet - 1 - 4)
cmd += chr(CalculateChecksum(cmd))
assert(len(cmd) == length_packet)
     # Send command to DC load
     sp.write(cmd)
     print "Set to remote command:"
     DumpCommand(cmd)
     # Get response from DC load
     response = sp.read(length_packet)
     assert(len(response) == length_packet)
     print "Response:"
     DumpCommand(response)
main()
