import socket, struct, sys
from get_local_ip import *
import anvil_pkt_pb2 as anvil

class EventServer(object):
    def __init__(self, addr):
        self.buf = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # tcp server
        self.s.bind(addr)
        self.connection = None
        
    def socket_read_n(self, n):
        pkt = ''
        src_addr = None
        while(n > 0):
            data = self.connection.recv(n)
            if not data:
                print 'no more data from the client'
                return ''
            pkt += data
            n -= len(data)
            
        return pkt
        
    def get_message(self):
        len_buf = self.socket_read_n(4)
        if len_buf is '':
            return None
        #next_pos, pos = decoder(data, pos)
        #msg.ParseFromString(data[pos:pos + next_pos])
        msg_len = struct.unpack('<i', len_buf)[0]
        print "Size of message in Bytes: ", msg_len
        msg_buf = self.socket_read_n(msg_len)
        if msg_buf is '':
            return None
        #print "message size: ", msg_len, ", ", len(msg_buf), ", ", struct.unpack('>H', len_buf)[0]
        pe = anvil.AnvilProtoPacket()
        pe.ParseFromString(msg_buf)
        print "Received the message successfully!"
        return pe
        
    def print_msg(self, msg):
        print 'Message tag: ', msg.tag
        if len(msg.float_data) > 0:
            ls = list('FLOAT DATA: [')
            for i in msg.float_data:
                ls += list("{0}, ".format(i))
            ls[-2]=']'
            #print "".join(ls)
        if len(msg.cplx_data) > 0:
            ls = list('CPLX DATA: [')
            for i in msg.cplx_data:
                ls += list("{0}+{0}i, ".format(i.real,i.imag))
            ls[-2]=']'
            #print "".join(ls)
        if msg.HasField("header"):
            print 'PSD control data: Nbins=', msg.header.nbins, ', freqmin=', msg.header.freqmin, ', freqmax=', msg.header.freqmax
            
        
    def run(self):
        self.s.listen(1)
        
        while True:
            print 'Waiting for a connection...'
            self.connection, client_address = self.s.accept()
            print 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                msg = self.get_message()#connection.recv(16)
                if msg is None:
                    print 'no more data from ', client_address
                    self.connection.close()
                    break
                self.print_msg(msg)
          
if __name__ == "__main__":
    textport = 1234
    host = "127.0.0.1"#get_lan_ip()

    if len(sys.argv) > 1:
        host = sys.argv[1]
        
    server = EventServer((host, textport))

    print "Looking for replies; press Ctrl-C or Ctrl-Break to stop."
    server.run()
    print "Exiting..."
