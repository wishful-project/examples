#include "../../ForgeUtilities.h"

#include <iostream>
#include <string>

int main(void) {
    iris::anvil_interface::AnvilTcpRx rx(1234);

    while(true) {
    	std::cout << "Gonna read packet...\n";
    	std::cout << rx.read_pkt() << std::endl;
    }
}
