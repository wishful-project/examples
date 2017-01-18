#include "ForgeUtilities.h"

#include <iostream>
#include <iterator>
#include <boost/lexical_cast.hpp>
#include <boost/asio.hpp>

namespace iris {

using namespace std;
namespace bip = boost::asio::ip;


/* Tcp Helpers */
namespace tcp_helper {

/**
 * Sends exactly n Bytes
 */
void send_n_bytes(tcp::socket &socket, const char *_buf, std::size_t n) {
    boost::asio::write(socket, boost::asio::buffer(_buf, n));
}

void send_n_bytes(tcp::socket &socket, const string &str) {
    boost::asio::write(socket, boost::asio::buffer(str.c_str(), str.size() + 1));
}

/**
 * Receives exactly n Bytes
 */
int recv_n_bytes(tcp::socket &socket, char *_buf, std::size_t n) {
    int nrec_v = n;
    try {
        boost::system::error_code ec;
        boost::asio::read(socket, boost::asio::buffer(_buf, n), boost::asio::transfer_at_least(n), ec); // can't compile with ec argument...
        if (ec == boost::asio::error::eof)
            return -1;
        else
            if (ec)
            throw boost::system::system_error(ec); // Some other error.
    } catch (std::exception& e) {
        std::cerr << e.what() << std::endl;
    }
    return nrec_v;
}

int recv_endline(tcp::socket &socket, char *_buf, int size) {
    int nrecv = 0, nprev = 0;
    for (int i = 0; i < size; i++)
        _buf[i] = '\0';

    while ((size - nrecv) > 0 && strchr(&_buf[nprev], '\n') == NULL) {
        try {
            boost::system::error_code ec;
            nprev = nrecv;
            nrecv += socket.read_some(boost::asio::buffer(&_buf[nrecv], size - nrecv), ec); // can't compile with ec argument...

            if (ec == boost::asio::error::eof)
                return -1;
            else
                if (ec)
                throw boost::system::system_error(ec); // Some other error.
        } catch (std::exception& e) {
            std::cerr << e.what() << std::endl;
        }
    }
    if ((size - nrecv) <= 0)
        return -1;
    else
        return nrecv;
}

TcpSocketClient::TcpSocketClient(std::string _address, int _port) : open(true)
{
        //Create socket
        boost::asio::ip::tcp::resolver resolver(ioService);
        boost::asio::ip::tcp::resolver::query query(_address, boost::lexical_cast<std::string>(_port));
        boost::asio::ip::tcp::resolver::iterator endpoint_iterator = resolver.resolve(query);
        boost::asio::ip::tcp::resolver::iterator end;

        socket =  new boost::asio::ip::tcp::socket(ioService) ;
        boost::system::error_code error = boost::asio::error::host_not_found;
        while (error && endpoint_iterator != end) {
                socket->close();
                socket->connect(*endpoint_iterator++, error);
        }
        if (error)
                open = false;
}

TcpSocketClient::~TcpSocketClient() {
    //Close socket
    try {
        socket->close();
    } catch (boost::system::system_error &e) {
        std::cout << "Failed to close socket: " << e.what();
    }
    delete socket;
}

template <typename Iterator> void TcpSocket::write(Iterator begin, Iterator end) {
    int bufSize = (end - begin) * sizeof (typename std::iterator_traits<Iterator>::value_type);
    //Send data to socket
    try {
        boost::asio::write(*socket, boost::asio::buffer((char *) &(*begin), bufSize));
    } catch (boost::system::system_error &e) {
        std::cout << "Error sending data to socket: " << e.what() << std::endl;
    }
}

int TcpSocket::write(const char *buf, int bufSize)
{
    int n;
    try {
        n = boost::asio::write(*socket, boost::asio::buffer(buf, bufSize));
    } catch (boost::system::system_error &e) {
        std::cout << "Error sending data to socket: " << e.what() << std::endl;
        return -1;
    }
    return n;
}

template <typename Iterator> int TcpSocket::read(Iterator begin, Iterator end)
{
    int bufSize = (end - begin) * sizeof (typename std::iterator_traits<Iterator>::value_type);

    //Get data from socket
    int size;
    try {
        size = recv_n_bytes(*socket, &(*begin), bufSize);
    } catch (boost::system::system_error &e) {
        std::cout << "Error receiving from socket: " << e.what();
        size = -1;
    }
    return size;
}

int TcpSocket::read(char *buf, int bufSize)
{
    //Get data from socket
    int size;
    try {
        size = recv_n_bytes(*socket, buf, bufSize);
    } catch (boost::system::system_error &e) {
        std::cout << "Error receiving from socket: " << e.what();
        size = -1;
    }
    return size;
}

int
TcpSocket::read_line(string &message)
{
   //Get data from socket
   boost::system::error_code error;
   boost::array<char, 1024> buf;

   size_t len = 0;

   try {
           len = socket->read_some(boost::asio::buffer(buf), error);
           message = std::string(buf.begin(), buf.begin() + len);
   } catch (boost::system::system_error &e) {
           std::cout << "Error receiving from socket: " << e.what();
           return -1;
   }
   return len;
}

void
TcpConnection::start_read(TcpConnection::msg_ready_callback callback)
{
	size_t bytes_transferred = boost::asio::read(socket_, input_buffer_, boost::asio::transfer_at_least(1));

	handle_read(bytes_transferred, callback);
	/*
	boost::asio::async_read(socket_, input_buffer_,
		boost::bind(&TcpConnection::handle_read, shared_from_this(),
		boost::asio::placeholders::error,
		boost::asio::placeholders::bytes_transferred,
		callback)
	);
	*/
}

//void TcpConnection::handle_read(const boost::system::error_code &ec, size_t bytes_transferred, TcpConnection::msg_ready_callback callback)
void
TcpConnection::handle_read(size_t bytes_transferred,
		TcpConnection::msg_ready_callback callback)
{
	// input_buffer is a class parameter in which the data received is stored
	std::istream is(&input_buffer_);

	std::string line;
	std::getline(is, line);

	// Empty messages are heartbeats and so ignored.
	if (!line.empty())
	{
		std::cout << "Received cmd: " << line << std::endl;

		callback(line);

		cout <<  __func__ << ": Sending ok: "  << std::endl;
		start_write( "ok\n" );
	}

	//close_connection();
}

void
TcpConnection::start_write(const std::string &message)
{
	boost::system::error_code ignored_error;
	boost::asio::write(socket_, boost::asio::buffer(message),
			boost::asio::transfer_all(), ignored_error);

	/*
	boost::asio::async_write(socket_, boost::asio::buffer(message),
			boost::bind(&TcpConnection::handle_write, shared_from_this(),
				boost::asio::placeholders::error,
				boost::asio::placeholders::bytes_transferred));
	*/
}

void
TcpConnection::close_connection()
{
	try {
		socket_.shutdown(boost::asio::ip::tcp::socket::shutdown_both);
		socket_.close();
	} catch (boost::system::system_error &e) {
		std::cout << "Failed to close socket: " << e.what();
	}
}

TcpSocketServer::TcpSocketServer(int _port)
{
    //if(verbose)
    //std::cout << "Waiting for connection..." << std::endl;
    acceptor = new tcp::acceptor(ioService, tcp::endpoint(tcp::v4(), _port));
    socket = new tcp::socket(ioService);
    acceptor->accept(*socket);
    //if(verbose)
    //std::cout << "Connection accepted!" << std::endl;
}

TcpSocketServer::~TcpSocketServer() {
    try {
        socket->shutdown(boost::asio::ip::tcp::socket::shutdown_both);
        socket->close();
    } catch (boost::system::system_error &e) {
        std::cout << "Failed to close socket: " << e.what();
    }
    delete socket;
    delete acceptor;
}

}
/*
namespace udp_helper {
template <typename Iterator> void send_n_bytes(Iterator begin, Iterator end, boost::scoped_ptr<UdpSocketTransmitter> &tx) {
        //std::vector<uint8_t> len_buffer(4);
        std::string len_buffer;
        int size = std::distance(begin,end);
        serialize_num(len_buffer, size);
        //numToString(len_buffer, size);

        tx->write(len_buffer.begin(), len_buffer.end());
    tx->write(begin, end);
}
}
 */
namespace socket_command {

std::string create_forgecommand_string(const std::string &command_name, const std::string &param_value) {
    stringstream ss;
    ss << command_name;
    if (param_value != "") {
        ss << ":" << param_value << "\n";
    } else {
        ss << "\n";
    }
    return ss.str(); // Are we copy elising?
}

TCPEventTransmitter::TCPEventTransmitter(int _port_x, const std::string &_address_x)
{
    port_x = _port_x;
    address_x = _address_x;
    socket = NULL;
}

void TCPEventTransmitter::create_socket()
{
    socket = new tcp_helper::TcpSocketClient(address_x, port_x);
}

void TCPEventTransmitter::send_event(const std::string &event_name, double value) {
    create_socket();
	
	std::cout << "*** send - event - 0 ***" << std::endl;
    
    std::ostringstream os;
    os << event_name << ":" << value << "\n";
    std::string event_string(os.str());
    socket->write(event_string.begin(), event_string.end());

    string ack_str;
    socket->read_line(ack_str);
    if (ack_str != "ok")
        std::cout << "ack was not received! Received: " << ack_str << endl;
    else
        std::cout << "ack received!\n";
    
	//~ close_connection();

}

void TCPEventTransmitter::send_event(const std::string &event_name, const std::string &value) {
    create_socket();

	//~ std::cout << "*** send - event - 1 ***" << std::endl;

    std::ostringstream os;
    os << event_name << ":" << value << "\n";
    std::string event_string(os.str());
    socket->write(event_string.begin(), event_string.end());
	
	//~ close_connection();

}

void TCPEventTransmitter::send_event(const std::string &event_string)
{
	create_socket();

	std::string tmp = event_string + "\n";
	socket->write(tmp.c_str(), tmp.size());

	string ack_str;
	socket->read_line(ack_str);

	if (ack_str != "ok")
		std::cout << "ack was not received! I received this: " << ack_str << std::endl;
	else
		std::cout << "ack received!" << std::endl;

	delete socket;
}

/*
void TCPEventTransmitter::send_event_2(const std::string &event_name, double value) {
        std::ostringstream os;
        os << event_name << ":" << value;
        std::string event_string(os.str());
        int size = event_string.size() + 1;
        std::string size_str;
        serialize_num(size_str, size);

        //tcp_helper::send_n_bytes(*socket, size_str.data(), sizeof(size)); //copy the bytes with the size
        //tcp_helper::send_n_bytes(*socket, event_string.c_str(), event_string.size() + 1);
}
 */

TCPEventReceiver::TCPEventReceiver(boost::asio::io_service &ios, int _port_x):
	io_service(ios), port_x(_port_x)
{
    acceptor_ = new boost::asio::ip::tcp::acceptor(io_service, boost::asio::ip::tcp::endpoint(tcp::v4(), _port_x));
}

void
TCPEventReceiver::start_server()
{
	//~ std::cout << "*** STARTING SERVER ***" << std::endl;
	tcp_helper::TcpConnection::pointer new_connection =
		tcp_helper::TcpConnection::create(acceptor_->get_io_service());

	acceptor_->async_accept(new_connection->socket(),
			boost::bind(&TCPEventReceiver::handle_accept,
				this,
				new_connection,
				boost::asio::placeholders::error)
			);
}

void
TCPEventReceiver::handle_accept(tcp_helper::TcpConnection::pointer new_connection,
      const boost::system::error_code& error)
{
    if (!error)
    {
      new_connection->start_read(boost::bind(&TCPEventReceiver::receive_command, this, _1));
    }
    start_server();
 }


void
TCPEventReceiver::receive_command(std::string &received_cmd)
{
	vector< std::string > split_commands; 
	boost::split( split_commands, received_cmd,
			boost::is_any_of(";"), boost::token_compress_on); 


	for (std::vector<string>::iterator it = split_commands.begin();
			it != split_commands.end();
			++it)
	{
		vector< std::string > split_cmd_val; 
		boost::split( split_cmd_val, received_cmd,
				boost::is_any_of(":"), boost::token_compress_on ); 

		event_list_.push_back(pair<string, string>(split_cmd_val[0],
					(split_cmd_val.size() == 1 ? string(""):split_cmd_val[1]))
				);
	}
}

bool
TCPEventReceiver::get_events(std::list<std::pair<std::string, std::string> > &ev)
{
	if (event_list_.size() > 0){
		ev.splice(ev.end(), event_list_);
		return true;
	}

	return false;
}


// OLD IMPLEMENTATION OF THE TCPEventReceiver
#if 0

TCPEventReceiver::TCPEventReceiver(int _port_x) {
    port_x = _port_x;
    socket = NULL;
}

void TCPEventReceiver::start_server() {
    //std::cout << "TCPEventReceiver:Waiting for connection..." << std::endl;
    socket = new tcp_helper::TcpSocketServer(port_x);
    //std::cout << "TCPEventReceiver:Connection accepted!" << std::endl;
}

bool TCPEventReceiver::receive_command(list<pair<string, string> > &event_list) {
    if (socket == NULL)
        start_server();

    string buf_str;
    if (socket->read_line(buf_str) < 0) {
        close_connection();
        return false;
    }
    std::cout << "Received string: " << buf_str << endl;

    event_list.clear();
    char *param, *val;
    param = strtok(&buf_str[0], ":");
    val = strtok(NULL, ";\n");
    if(val != NULL)
        event_list.push_back(pair<string, string>(string(param), string(val)));
    else
        event_list.push_back(pair<string, string>(string(param), ""));
    while (val != NULL && param != NULL) {
        param = strtok(NULL, ":");
        if (param == NULL) break;
        val = strtok(NULL, ";\n");
        if (val == NULL) break;
        event_list.push_back(pair<string, string>(string(param), string(val)));
    }
    //sscanf(pch, "%lf", &value);

    string ack("ok\n");
    socket->write(ack.begin(), ack.end());
    close_connection();

    return true;
}

/*bool TCPEventReceiver::receive_event_2(std::string &parameter, double &value) {
//	if(tcp_helper::recv_n_bytes(*socket, buf_header, 4) < 0) {
//		erase_connection();
//		return false;
//	}
        int size, nrecv;
        bytesToInt(size, buf_header);

        if(size > buf_size)
                size = buf_size;
//	if(tcp_helper::recv_n_bytes(*socket, buf_payload, size) < 0) {
//		erase_connection();
//		return false;
//	}

        char *pch = strtok(buf_payload, ":");//" ,.-");
        parameter.assign(pch);
        pch = strtok(NULL, ":");//" ,.-");
        sscanf(pch, "%lf", &value);

        return true;
}*/

#endif

}

namespace anvil_interface {

/*
AnvilTcpTx::AnvilTcpTx(std::string _address, int _port) : address_x(_address), port_x(_port) {
    tx_socket = new tcp_helper::TcpSocketClient(address_x, port_x);
}

void AnvilTcpTx::initiate_psd_session(char tag, float min_freq, float max_freq, int Nbins) {
    sessions.insert(pair<char, DATA_TYPE>(tag, PSD_DATA));
    ostringstream os;
    os << tag << serialize_num(min_freq) << serialize_num(max_freq) << serialize_num(Nbins);
    string data(os.str());

    tx_socket->write(data.begin(), data.end());
}

void AnvilTcpTx::initiate_session(char tag, DATA_TYPE type) {
    sessions.insert(pair<char, DATA_TYPE>(tag, type));
}

*//**
 * writes data to socket with a tag associated to it. The stream_type defines how the header will be generated. stream_type is ignored if the session for char 'tag' is already initiated
 *//*
void AnvilTcpTx::write(const char *buf, const int size_bytes, const char tag) {
    if (sessions.find(tag) == sessions.end()) {
        std::cerr << "Session PSD was still not initialized!" << std::endl;
    }
    int header_size = 5;

    buffer.reserve(size_bytes);
    buffer[0] = tag;
    memcpy((char*) &buffer[1], (char*) &size_bytes, sizeof (size_bytes));
    memcpy((char*) &buffer[header_size], &buf[0], size_bytes);
    tx_socket->write((char*) &buffer[0], header_size + size_bytes);
}

AnvilTcpRx::AnvilTcpRx(int _port) : port_x(_port) {
    rx_socket = new tcp_helper::TcpSocketServer(port_x);
    std::cout << "Exiting constructor...\n";
}

void AnvilTcpRx::read(char *buf, int size) {
    if (rx_socket->read(buf, size) < 0) {
        delete rx_socket;
        rx_socket = new tcp_helper::TcpSocketServer(port_x);
        std::cout << "Exiting constructor...\n";
    }
}

inline DATA_TYPE AnvilTcpRx::guess_data_type(const char tag) {
    switch (tag) {
        case 'w': return PSD_DATA;
        case 'f': return FLOAT_DATA;
        default: return CPLX_DATA;
    }
}

std::string AnvilTcpRx::read_pkt() {
    char tag;
    read(&tag, sizeof (tag));
    map<char, session_data>::iterator it = sessions.find(tag);
    if (it == sessions.end()) { // create session
        session_data sd(guess_data_type(tag));
        sessions.insert(pair<char, session_data>(tag, sd));
        it = sessions.find(tag);
        if (it->second.dt == PSD_DATA) {
            float minfreq, maxfreq;
            int Nbins;
            read((char*) &minfreq, sizeof (minfreq));
            read((char*) &maxfreq, sizeof (maxfreq));
            read((char*) &Nbins, sizeof (Nbins));
            if (it->second.ctrl_ptr != NULL)
                delete it->second.ctrl_ptr;
            it->second.ctrl_ptr = new ctrl_data(minfreq, maxfreq, Nbins);
            return "";
        }
    }

    int num_bytes;
    read((char*) &num_bytes, sizeof (num_bytes));
    if (num_bytes == 0) return '\0';
    char buf[num_bytes];
    read(buf, num_bytes);

    ostringstream os;
    os << "tag: " << tag << " | data: [";
    int num_elem, size_data;
    if (it->second.dt == CPLX_DATA) {
        std::complex<float> cval;
        size_data = sizeof (cval);
        num_elem = num_bytes / size_data;
        std::vector<std::complex<float> > cvec;
        cvec.resize(num_elem);
        int n_read = 0;
        memcpy((char*) &cvec[0], buf, num_bytes);
        for (int i = 0; i < num_elem; i++)
            os << cvec[i] << ", ";
    } else {
        float val;
        size_data = sizeof (val);
        num_elem = num_bytes / size_data;
        std::vector<float> vec;
        vec.resize(num_elem);
        memcpy((char*) &vec[0], buf, num_bytes);
        for (int i = 0; i < num_elem; i++)
            os << vec[i] << ", ";
    }

    string ret(os.str());
    ret[ret.size() - 1 - 1] = ']';
    return ret;
}*/

AnvilProtobufTcpTx::AnvilProtobufTcpTx(std::string _address, int _port) : address_x(_address), port_x(_port), tx_socket(NULL) {
    tx_socket = new tcp_helper::TcpSocketClient(address_x, port_x);
    if(tx_socket->is_open() == false)
        close_socket();
}

void AnvilProtobufTcpTx::initiate_psd_session(AnvilTag tag, float min_freq, float max_freq, int Nbins) {
    sessions.insert(pair<AnvilTag, DATA_TYPE>(tag, PSD_DATA));
    set_psd_param(min_freq, max_freq, Nbins);
}

void AnvilProtobufTcpTx::set_psd_param(float min_freq, float max_freq, int Nbins) {
    AnvilProtoPacket pkt;
    anvil_add_protopsdheader(pkt, Nbins, max_freq, min_freq);
    if (write(pkt) == false) {
        std::cerr << "Couldn't send PSD session data through the socket!" << endl;
    }
}

void AnvilProtobufTcpTx::initiate_session(AnvilTag tag, DATA_TYPE type) {
    if (type == PSD_DATA) {
        std::cerr << "Can't initiate a PSD session without control data!" << endl;
        return;
    }
    sessions.insert(pair<AnvilTag, DATA_TYPE>(tag, type));
}

bool AnvilProtobufTcpTx::write(const AnvilProtoPacket& message) {
    vector<google::protobuf::uint8> buffer;
    serialize_with_prefix(buffer, message);
    int sent_bytes = tx_socket->write((char*) &buffer[0], buffer.size());
    if (sent_bytes < 0) {
    	return false;
    }
    return true;
}

bool AnvilProtobufTcpTx::write_pkt(const vector<float> &data, AnvilTag tag) {
    map<AnvilTag, DATA_TYPE>::iterator it = sessions.find(tag);
    if (sessions.find(tag) == sessions.end()) {
        std::cerr << "Session PSD was still not initialized!" << std::endl;
        return false;
    }

    AnvilProtoPacket pkt;
    pkt.set_tag(tag);
    for (int i = 0; i < data.size(); ++i) {
        pkt.add_float_data(data[i]);
    }
    return write(pkt);
}

bool AnvilProtobufTcpTx::write_pkt(const vector<Cplx> &data, AnvilTag tag) {
    map<AnvilTag, DATA_TYPE>::iterator it = sessions.find(tag);
    if (sessions.find(tag) == sessions.end()) {
        std::cerr << "Session PSD was still not initialized!" << std::endl;
        return false;
    }

    AnvilProtoPacket pkt;
    pkt.set_tag(tag);
    for (int i = 0; i < data.size(); ++i) {
        CplxNumber* num_ptr = pkt.add_cplx_data();
        num_ptr->set_real(data[i].real());
        num_ptr->set_imag(data[i].imag());
    }
    return write(pkt);
}

bool AnvilProtobufTcpTx::write_pkt(const vector<boost::any> &data, AnvilTag tag) {
    map<AnvilTag, DATA_TYPE>::iterator it = sessions.find(tag);
    if (sessions.find(tag) == sessions.end()) {
        std::cerr << "Session PSD was still not initialized!" << std::endl;
        return false;
    }

    AnvilProtoPacket pkt;
    pkt.set_tag(tag);
    if (it->second == PSD_DATA || it->second == FLOAT_DATA) {
        for (int i = 0; i < data.size(); ++i) {
            pkt.add_float_data(boost::any_cast<float>(data[i]));
        }
    } else { // CPLXDATA
        for (int i = 0; i < data.size(); ++i) {
            CplxNumber* num_ptr = pkt.add_cplx_data();
            Cplx num = boost::any_cast<Cplx>(data[i]);
            num_ptr->set_real(num.real());
            num_ptr->set_imag(num.imag());
        }
    }
    return write(pkt);
}

inline void anvil_add_protopsdheader(AnvilProtoPacket &pkt, int Nbins, float fmax, float fmin) {
    pkt.set_tag(PSD_BINS);
    PSDHeader *header = pkt.mutable_header();
    header->set_nbins(Nbins);
    header->set_freqmax(fmax);
    header->set_freqmin(fmin);
}

/*
 * bool recv_message(int socket, my_protobuf::Message *message)
{
  google::protobuf::uint32 message_length;
  int prefix_length = sizeof(message_length);
  google::protobuf::uint8 prefix[prefix_length];

  if (prefix_length != read(socket, prefix, prefix_length)) {
    return false;
  }
  google::protobuf::io::CodedInputStream::ReadLittleEndian32FromArray(prefix,
      &message_length);

  google::protobuf::uint8 buffer[message_length];
  if (message_length != read(socket, buffer, message_length)) {
    return false;
  }
  google::protobuf::io::ArrayInputStream array_input(buffer, message_length);
  google::protobuf::io::CodedInputStream coded_input(&array_input);

  if (!message->ParseFromCodedStream(&coded_input)) {
    return false;
  }

  return true;
}
 */

/*class AnvilUdpTx {
        boost::scoped_ptr<UdpSocketTransmitter> tx_socket;
public:
        AnvilUdpTx(std::string address_x, int port_x) {
                tx_socket.reset(new UdpSocketTransmitter(address_x, port_x));
        }

        template <typename Iterator>
        void write(Iterator begin, Iterator end) {
                send_n_bytes(begin, end, tx_socket);
        }
};*/

/*class AnvilPsdUdpTx {
        boost::scoped_ptr<UdpSocketTransmitter> tx_socket;
        float min_freq, max_freq;
        int Nbins;
        bool first_time;

public:
        AnvilPsdUdpTx(std::string address_x, int port_x, float _min_freq, float _max_freq, int _Nbins): min_freq(_min_freq), max_freq(_max_freq), Nbins(_Nbins) {
            tx_socket.reset(new UdpSocketTransmitter(address_x, port_x));
            first_time = true;
        }

        template <typename Iterator>
        void write(Iterator begin, Iterator end) {
                if(first_time) {
                        std::string str;
                        union {
                                float a;
                                char bytes[4];
                        } thing;
                        thing.a = min_freq;
                        str.assign(thing.bytes, 4);
                        tx_socket->write(str.begin(), str.end());
                        thing.a = max_freq;
                        str.assign(thing.bytes, 4);
                        tx_socket->write(str.begin(), str.end());
                        numToString(str, Nbins);
                        tx_socket->write(str.begin(), str.end());
                        first_time = false;
                }
                tx_socket->write(begin, end);
        }
};*/

}


}
