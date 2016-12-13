#include "../../ForgeUtilities.h"

#include <iostream>
#include <sstream>
#include <string>

int main(void) {
    iris::anvil_interface::AnvilProtobufTcpTx tx("127.0.0.1", 1234);
    float min_freq = 10000.0, max_freq = 15000.0;
    int Nbins = 20;
    AnvilTag tag = PSD_BINS;
    std::cout << "Initializing PSD session...\n";
    tx.initiate_psd_session(tag, min_freq, max_freq, Nbins);
    std::vector<float> vec(Nbins);
    for(int i = 0; i < Nbins; i++) {
    	vec[i] = (float)i;
    }
    std::cout << "Writing the first set of bins...\n";
    tx.write_pkt(vec, tag);

    tag = MOD_PREAMBLE;
    tx.initiate_session(tag, iris::anvil_interface::CPLX_DATA);
    std::vector<std::complex<float> > vec2(1000);
        for(int i = 0; i < 1000; i++) {
        	vec2[i] = std::complex<float>((float)10*i, (float) 20*i);
        }
        std::cout << "Writing the first set of bins...\n";
        tx.write_pkt(vec2, tag);
}
