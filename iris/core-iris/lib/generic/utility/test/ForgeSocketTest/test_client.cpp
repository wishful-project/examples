#include <cstdlib>
#include <boost/aligned_storage.hpp>
#include <boost/array.hpp>
#include <boost/bind.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/noncopyable.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/asio.hpp>
#include <iostream>
#include <string> 
#include <sstream>
#include <boost/thread.hpp>

namespace std {
    template<typename T>
    std::string to_string(const T &n) {
        std::ostringstream s;
        s << n;
        return s.str();
    }
}

struct Client
{
    boost::asio::io_service& io_service;
    boost::asio::ip::tcp::socket socket;

    Client(boost::asio::io_service& svc, std::string const& host, std::string const& port) 
        : io_service(svc), socket(io_service) 
    {
        boost::asio::ip::tcp::resolver resolver(io_service);
        boost::asio::ip::tcp::resolver::iterator endpoint = resolver.resolve(boost::asio::ip::tcp::resolver::query(host, port));
        boost::asio::connect(this->socket, endpoint);
    };

    void send(std::string const& message) {
        socket.send(boost::asio::buffer(message));
    }
};

static const int PORT = 1235;

void client_thread(std::string cmd) {
    boost::asio::io_service svc; //set IP Server - IRIS
    Client client(svc, "192.168.5.108", std::to_string(PORT));
    client.send(std::string(cmd));
}

int main() {
  
  char command[128];
  
  while(1) {
    std::cout << "Write command: ";
    std::cin >> command;
    client_thread(command);
    std::cout << "Command sent: " << command << std::endl;
    
  }
}
