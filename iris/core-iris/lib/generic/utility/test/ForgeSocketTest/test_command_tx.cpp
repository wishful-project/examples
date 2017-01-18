#include "../../ForgeUtilities.h"

#include <iostream>
#include <string>

using namespace std;

int main(int argc, char *argv[]) {
    int port = 1235;
    std::string addr("127.0.0.1");
    std::vector<std::string> command_list;
    command_list.reserve(argc-1);
    std::string remote_comm("remote:");

    for(int i = 1; i < argc; i++)
    {
	std::string stri(argv[i]);
        int pos = stri.find(remote_comm);
        if(pos == string::npos)
            command_list.push_back(stri);
        else
        {
            cout << "Commanding a remote node...\n";
            //cout << "received a remote: " << stri << endl;
            stri = stri.substr(pos+remote_comm.length(), stri.length() - (pos+remote_comm.length()));
            //cout << "Selected substring: " << stri << endl;
            //auto addr_tuple = string_delimiter(stri, ", )\n");
            cout << "addr: (" << stri << ")\n";// << ", port: " << addr_tuple.back() << endl;
            addr = stri;//addr_tuple.front();
            //port = atoi(addr_tuple.back().c_str());
        }
    }
    iris::socket_command::TCPEventTransmitter tx(port, addr);

    if(command_list.size() > 0)
    {
        std::stringstream ss;
        for(int i = 0; i < command_list.size() - 1; i++) {
            ss << command_list[i] << ";";
        }
        ss << command_list[command_list.size()-1] << "\n";
        tx.send_event(ss.str());
        std::cout << "Command sent: " << ss.str() << std::endl;
    }

    char command[128];
    while(1) {
        std::cout << "Write command: ";
        std::cin >> command;
        tx.send_event(std::string(command));
        std::cout << "Command sent: " << command << std::endl;
    }
}
