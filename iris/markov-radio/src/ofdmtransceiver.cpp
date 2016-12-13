
#include "ofdmtransceiver.h"
#include <boost/assign.hpp>
#include "RawFileUtility.h"
#include <iostream>
#include <string>
//#include <boost/ptim>
#define DEBUG_MODE

#ifdef DEBUG_MODE
#include <ctime>
#endif

using std::cout;
using std::endl;

OfdmTransceiver::OfdmTransceiver(const RadioParameter params) :
DyspanRadio(params),
seq_no_(0),
payload_len_(1500),
learner(4)
{
    assert(payload_len_ <= MAX_PAYLOAD_LEN);
    reconfigure_counter = 0;
    min_reconfigure_wait = params.reconfig_wait;

    // create frame generator
    ofdmflexframegenprops_init_default(&fgprops);
    fgprops.check = liquid_getopt_str2crc(params_.crc.c_str());
    fgprops.fec0 = liquid_getopt_str2fec(params_.fec0.c_str());
    fgprops.fec1 = liquid_getopt_str2fec(params_.fec1.c_str());
    fgprops.mod_scheme = liquid_getopt_str2mod(params_.mod.c_str());
    fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);

    // allocate memory for frame generator output (single OFDM symbol)
    fgbuffer_len = params_.M + params_.cp_len;
    fgbuffer = (std::complex<float>*) malloc(fgbuffer_len * sizeof (std::complex<float>));

    //create a usrp device
    cout << endl;
    cout << boost::format("Creating the Rx usrp device with: %s...") % params_.txargs << endl;
    cout << boost::format("Creating the Tx usrp device with: %s...") % params_.rxargs << endl;
    usrp_tx = uhd::usrp::multi_usrp::make(params_.txargs);
    usrp_tx->set_tx_subdev_spec(params_.txsubdev);
    std::cout << boost::format("Using Device: %s") % usrp_tx->get_pp_string() << endl;
    usrp_rx = uhd::usrp::multi_usrp::make(params_.rxargs);
    usrp_rx->set_rx_subdev_spec(params_.rxsubdev);

    // std::cout << boost::format("number of channels ::: %s") % usrp_rx->get_rx_num_channels() << std::endl;
    has_learning = params.has_learning;

    // initialize default tx values
    set_tx_freq(params_.f_center);
    set_tx_rate(params_.channel_rate);
    set_tx_gain_soft(params_.tx_gain_soft);
    set_tx_gain_uhd(params_.tx_gain_uhd);
    tx_opt = params_.tx_opt;
    double rx_rf_rate = params_.num_channels * params_.channel_bandwidth;
    set_rx_freq(params_.f_center);
    set_rx_rate(rx_rf_rate);
    set_rx_gain_uhd(params_.rx_gain_uhd);
    if (params_.usrp_type_rx == "n210")
    {
        set_rx_antenna("TX/RX");
    }

    // setting up the energy detector (number of averages,window step size,fftsize)
    e_detec.set_parameters(16, 512, 4, 0.4, 0.4, params.second_av_size); //(150, num_channels, 512, 0.4);// Andre: these are the parameters of the sensing (number of averages,window step size,fftsize)

    // Open the file where we will store the learning data
    if (has_learning)
    {
        hOutFile_.open(params_.filename.c_str(), std::ios::out | std::ios::binary);
        if (hOutFile_.fail() || hOutFile_.bad() || !hOutFile_.is_open())
        {
            cout << "Could not open file " << params_.filename << " for writing." << endl;
            //TODO: Throw an exception
        }
    }



    //hInFile_.seekg(0, std::ios::beg);



    if (params_.use_db)
    {
        // create and connect to challenge database
        tx_ = spectrum_init(0);
        spectrum_eror_t ret = spectrum_connect(tx_, (char*) params_.db_ip.c_str(), 5002, payload_len_, 1);
        spectrum_errorToText(tx_, ret, error_buffer, sizeof (error_buffer));
        std::cout << boost::format("TX connect: %s") % error_buffer << std::endl;
        if (ret < 0)
        {
            throw std::runtime_error("Couldn't connect to challenge database");
        }

        // get radio number
        int radio = spectrum_getRadioNumber(tx_);
        std::cout << boost::format("TX radio number: %d") % radio << std::endl;

        // wait for the start of stage 3 (here you get penalized for interference).
        // The testing database starts in this state so this will instantly return.
        spectrum_waitForState(tx_, 3, -1);
        std::cout << boost::format("Stage 3 has started.") << std::endl;
    }
    
    e_detec_out_step = -1;
}

OfdmTransceiver::~OfdmTransceiver()
{
    if (tx_)
        spectrum_delete(tx_);
    delete fgbuffer;
}


//
// transmitter methods
//

void OfdmTransceiver::start(void)
{
    // start transmission threads
    if (!has_learning)
    {
        threads_.push_back(new boost::thread(boost::bind(&OfdmTransceiver::modulation_function, this)));
        threads_.push_back(new boost::thread(boost::bind(&OfdmTransceiver::random_transmit_function, this)));
    }
    //start sensing thread
    threads_.push_back(new boost::thread(boost::bind(&OfdmTransceiver::receive_function, this)));
    //  threads_.push_back( new boost::thread( boost::bind( &OfdmTransceiver::transmit_function, this ) ) );
}


// This function creates new frames and pushes them on a shared buffer queue

void OfdmTransceiver::modulation_function(void)
{
    boost::this_thread::sleep(boost::posix_time::seconds(2));
    boost::posix_time::time_duration t1;
    boost::posix_time::ptime Start = boost::posix_time::microsec_clock::universal_time();
    boost::posix_time::ptime Now = boost::posix_time::microsec_clock::universal_time();
    // boost::posix_time::time_duration flag = 3000;
    std::vector<unsigned char> header_map = {'0','1','2','3'};

    try
    {
        unsigned char header[8];
        unsigned char payload[MAX_PAYLOAD_LEN];
        memset(payload, 0, MAX_PAYLOAD_LEN);
        int num_packets = 0;
        //int total_payload = 0;
        int mod = 13;
        bool que_change = true;
        if (tx_opt)
            header[5] = 'm';
        while (true)
        {
            boost::this_thread::interruption_point();

            // write header (first four bytes sequence number, remaining are random)
            // TODO: also use remaining 4 bytes for payload
            header[0] = (seq_no_ >> 24) & 0xff;
            header[1] = (seq_no_ >> 16) & 0xff;
            header[2] = (seq_no_ >> 8) & 0xff;
            header[3] = (seq_no_) & 0xff;
            for (int i = 7; i < 8; i++)
                header[i] = rand() & 0xff;

#if 0
            header[4] = header_map[current_channel];


            if (tx_opt)
            {
                if (que_change)
                {
                    header[6] = (unsigned char) mod;
                    switch (mod)
                    {
                    case 1:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("bpsk");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 2:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qpsk");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 3:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qam16");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 4:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qam32");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 5:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qam64");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 6:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qam128");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 7:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("qam256");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 8:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("sqam32");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 9:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("sqam128");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 10:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("arb32opt");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 11:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("arb64opt");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 12:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("arb128opt");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    case 13:
                        Start = boost::posix_time::microsec_clock::universal_time();
                        fgprops.mod_scheme = liquid_getopt_str2mod("arb256opt");
                        fg = ofdmflexframegen_create(params_.M, params_.cp_len, params_.taper_len, params_.p, &fgprops);
                        break;
                    default:

                        break;
                    }
                    que_change = false;
                    num_packets = 0;
                    mod--;
                }
                Now = boost::posix_time::microsec_clock::universal_time();
                
                t1 = Now - Start;

                if (t1.total_milliseconds() > 50000)
                {
                    que_change = true;
                    std::cout << "mod test is :" << mod << std::endl;

                }

                if (mod > 13)
                {
                    tx_opt = false;
                    header[5] = 'd';
                    std::cout << "mod optimization complete" << std::endl;
                }


                //num_packets++;

            }
            else
            {
                //std::cout << "mod optimization complete" << std::endl;
            }
#endif

            /////////////////////
            // Fill the Payload
            ////////////////////
            
            int actual_payload_len = payload_len_;
            if (params_.use_db)
            {
                // get packet from database
                // FIXME: payload_len must not be smaller than the size requested during init
                spectrum_eror_t ret = spectrum_getPacket(tx_, payload, payload_len_, -1);
                spectrum_errorToText(tx_, ret, error_buffer, sizeof (error_buffer));
                if (ret < 0)
                {
                    std::cout << boost::format("Error: %s") % error_buffer << std::endl;
                    throw std::runtime_error("Couldn't connect to challenge database");
                }
                // getPacket returns actual length
                actual_payload_len = ret;
            }
            else
            {
                // fill with dummy payload
                for (int i = 0; i < actual_payload_len; i++)
                    payload[i] = '5'; //rand() & 0xff;
            }

            //////////////////
            // Assemble frame
            //////////////////
            
            ofdmflexframegen_setprops(fg, &fgprops);

            ofdmflexframegen_assemble(fg, header, payload, actual_payload_len);
            if (params_.debug)
                ofdmflexframegen_print(fg);

            size_t num_symbols = ofdmflexframegen_getframelen(fg);
            const size_t frame_size = num_symbols * fgbuffer_len;

            // create fresh buffer for this frame
            boost::shared_ptr<CplxFVec> usrp_buffer(new CplxFVec(frame_size));
            unsigned int bytes_written = 0;
            while (num_symbols--)
            {
                ofdmflexframegen_writesymbol(fg, fgbuffer);
                // copy symbol and apply gain
                for (int i = 0; i < fgbuffer_len; i++)
                    (*usrp_buffer.get())[bytes_written + i] = fgbuffer[i] * tx_gain;
                bytes_written += fgbuffer_len;
            }
            assert(bytes_written == frame_size);
            frame_buffer.pushBack(usrp_buffer);

            if (params_.debug)
                std::cout << boost::format("TX frame %6u (%d Bytes)") % seq_no_ % actual_payload_len << std::endl;

            seq_no_++;
        }
    }
    catch (boost::thread_interrupted)
    {
        std::cout << "Modulation thread interrupted." << std::endl;
    }
}

void OfdmTransceiver::transmit_function(void)
{
    try
    {
        while (true)
        {
            boost::this_thread::interruption_point();

            // check if channel needs to be reconfigured
            // send 50 packets on second channel once every 100 packets
            static int counter = 1;
            if (counter++ % 100 == 0)
            {
                reconfigure_usrp(1);
                for (int i = 0; i < 50; i++)
                    transmit_packet();
                reconfigure_usrp(0);
                boost::this_thread::sleep(boost::posix_time::seconds(1));
            }
            else
            {
                // transmit frame
                transmit_packet();
            }


        }
    }
    catch (boost::thread_interrupted)
    {
        std::cout << "Transmit thread interrupted." << std::endl;
    }
}

// This Function picks frames stored in the shared buffer queue, and transmits them
// TODO: Recycle buffers, instead of always allocating

void OfdmTransceiver::random_transmit_function(void)
{
    try
    {
        reconfigure_usrp(1);
        while (true)
        {
            boost::this_thread::interruption_point();

            // get random channel
            //int num = rand() % channels_.size();
            // reconfigure_usrp(num);
            //for (int i = 0; i < 50; i++)
            transmit_packet();

            //boost::this_thread::sleep(boost::posix_time::milliseconds(500));
        }
    }
    catch (boost::thread_interrupted)
    {
        std::cout << "Random transmit thread interrupted." << std::endl;
    }
}

void OfdmTransceiver::reconfigure_usrp(const int num)
{
    // construct tuning request
    current_channel = num;
    int internal_num;

    if (num == 0)
        internal_num = 3;
    if (num == 1)
        internal_num = 1;
    if (num == 2)
        internal_num = 0;
    if (num == 3)
        internal_num = 2;


    uhd::tune_request_t request;
    // don't touch RF part
    request.rf_freq_policy = uhd::tune_request_t::POLICY_NONE;
    request.rf_freq = 0;
    // only tune DSP frequency
    request.dsp_freq_policy = uhd::tune_request_t::POLICY_MANUAL;
    request.dsp_freq = channels_.at(internal_num).dsp_freq;
    request.args = uhd::device_addr_t("mode_n=integer");
    uhd::tune_result_t result = usrp_tx->set_tx_freq(request);

    if (params_.debug)
    {
        std::cout << result.to_pp_string() << std::endl;
    }
}

void OfdmTransceiver::transmit_packet()
{
    // set up the metadata flags
    metadata_tx.start_of_burst = false; // never SOB when continuous
    metadata_tx.end_of_burst = false; //
    metadata_tx.has_time_spec = false; // set to false to send immediately

    boost::shared_ptr<CplxFVec> buffer;
    frame_buffer.popFront(buffer);

    // send samples to the device
    usrp_tx->get_device()->send(
                                &buffer->front(), buffer->size(),
                                metadata_tx,
                                uhd::io_type_t::COMPLEX_FLOAT32,
                                uhd::device::SEND_MODE_FULL_BUFF
                                );

    // send a few extra samples and EOB to the device
    // NOTE: this seems necessary to preserve last OFDM symbol in
    //       frame from corruption
    metadata_tx.start_of_burst = false;
    metadata_tx.end_of_burst = true;
    CplxFVec dummy(NUM_PADDING_NULL_SAMPLES);
    usrp_tx->get_device()->send(
                                &dummy.front(), dummy.size(),
                                metadata_tx,
                                uhd::io_type_t::COMPLEX_FLOAT32,
                                uhd::device::SEND_MODE_FULL_BUFF
                                );
}

void OfdmTransceiver::receive_function(void)
{

#ifdef DEBUG_MODE
    time_t tnow, tlast = time(0);
#endif

    //create a receive streamer
    std::string wire_format("sc16");
    std::string cpu_format("fc32");
    uhd::stream_args_t stream_args(cpu_format, wire_format);
    uhd::rx_streamer::sptr rx_stream = usrp_rx->get_rx_stream(stream_args);

    //setup streaming
    std::cout << std::endl;
    std::cout << boost::format("Begin streaming now ..") << std::endl;
    uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
    stream_cmd.num_samps = 0; // continuous
    stream_cmd.stream_now = true;
    stream_cmd.time_spec = uhd::time_spec_t();
    usrp_rx->issue_stream_cmd(stream_cmd);

    //meta-data will be filled in by recv()
    uhd::rx_metadata_t metadata;
    bool overflow_message = true;
    int dwell_counter = 0;
    int learn_counter = 0;
    bool have_markov = false;
    //bool c = false;
    bool have_tdwell = false;
    double t_dwell;
    std::vector<char> markov_next_channel;
    markov_next_channel.resize(4);
    double previous_dwelltime = 0.5;
    DwellTimeEstimator Dwell(4, 0.5, 0.20);
    bool go = true;
    try
    {
        while (go)
        {
            boost::this_thread::interruption_point();

            ///////////////////////////
            // Apply Energy Detection
            ///////////////////////////
            
            do
            {
                std::vector<std::complex<float> > rxBuff;
                rxBuff.resize(100);
                
                //////////////////////////////////////////////
                // Read the samples directly to the FFT of the energy detector
                //////////////////////////////////////////////
                
                size_t num_rx_samps = rx_stream->recv(e_detec.fftBins, e_detec.nBins, metadata, 5.0);

                //handle the error code
                if (metadata.error_code == uhd::rx_metadata_t::ERROR_CODE_TIMEOUT)
                {
                    std::cout << boost::format("Timeout while streaming") << std::endl;
                    break;
                }
                if (metadata.error_code == uhd::rx_metadata_t::ERROR_CODE_OVERFLOW)
                {
                    if (overflow_message)
                    {
                        overflow_message = false;
                        std::cerr << boost::format("Got an overflow indication, please reduce sample rate.");
                    }
                    continue;
                }
                if (metadata.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE)
                {
                    throw std::runtime_error(str(boost::format(
                                                               "Unexpected error code 0x%x"
                                                               ) % metadata.error_code));
                }

                timestamp_ = metadata.time_spec;

                // Always call process because we write on fftBins nBins samples from uhd (see above)
                e_detec.process(timestamp_.get_real_secs());
            }
            while (not e_detec.result_exists());

            double tstamp;
            std::vector<float> ch_power;
            e_detec.pop_result(tstamp, ch_power); // ch_power is your sensing results, free channels will appear as a 0

            
            ///////////////////////////
            // If it is learning and needs to estimate dwell time
            ///////////////////////////
            
            if (has_learning && !have_tdwell)
            {
                cout << tstamp << ", " << ch_power[0] << "," << ch_power[1] << "," << ch_power[2] << "," << ch_power[3] << "\n";
                cout << "current channel: " << Dwell.cur_ch << ", dwell time: " << Dwell.dwelltime() << endl;
                Dwell.process(tstamp, ch_power);

                /// Checks if the dwell time estimate has stabilized
                auto DwellPair = DwellEst(Dwell, previous_dwelltime, dwell_counter, 10000, 0.04);
                if (DwellPair.second)
                {
                    have_tdwell = true;
                    t_dwell = DwellPair.first;
                    learner.set_dwelltime(t_dwell);
                    e_detec_out_step = Dwell.tstamp_step();
                    std::cout << "The time interval between tstamps outputs from the e_detec is " << e_detec_out_step << std::endl;
                    std::cout << "Min reconfigure time wait was " << min_reconfigure_wait * e_detec_out_step << ". ";
                    min_reconfigure_wait = t_dwell / e_detec_out_step;
                    std::cout << "Now it is " << min_reconfigure_wait * e_detec_out_step << std::endl;
                }
            }

            ///////////////////////////
            // If it is learning and dwell is already estimated, compute
            // create the markov chain
            ///////////////////////////
            
            if (has_learning && have_tdwell)
            {
                if (learner.num_total_transitions() < 8000)
                {
                    learner.learning_update(tstamp, ch_power);
                    learn_counter++;
                    // std::cout << learner.get_transitions();
                }
                else if (not have_markov)
                {
                    markov_next_channel[0] = (char) learner.select_next_channel(-1, tstamp, {60,0,0,0});
                    markov_next_channel[1] = (char) learner.select_next_channel(-1, tstamp, {0,60,0,0});
                    markov_next_channel[2] = (char) learner.select_next_channel(-1, tstamp, {0,0,60,0});
                    markov_next_channel[3] = (char) learner.select_next_channel(-1, tstamp, {0,0,0,60});

                    std::cout << " writing the markov" << markov_next_channel[0] << markov_next_channel[1] << markov_next_channel[2] << markov_next_channel[3] << std::endl;
                    RawFileUtility::write(markov_next_channel.begin(), markov_next_channel.end(), hOutFile_, "native");
                    has_learning = false;
                    std::cout << " writing the markov2" << std::endl;
                    threads_.push_back(new boost::thread(boost::bind(&OfdmTransceiver::modulation_function, this)));
                    threads_.push_back(new boost::thread(boost::bind(&OfdmTransceiver::random_transmit_function, this)));
                    std::cout << " writing the markov3" << std::endl;
                    hOutFile_.close();
                }
                else
                {
                    std::cout << "Markov chain is ready!!" << std::endl;
                }
            }
            
            ///////////////////////////
            // We are not in the learning phase, read markov chain from file
            ///////////////////////////
            if (not has_learning && not have_markov)
            {
                //hInFile_.open(params_.filename.c_str(), std::ios::in|std::ios::binary);
                hInFile_.open(/*params_.filename.c_str()*/"markov.txt", std::ios::in/*|std::ios::binary|std::ios::ate*/);
                if (hInFile_.fail() || hInFile_.bad() || !hInFile_.is_open())
                {
                    std::cout << "Could not open file " << params_.filename << " for reading." << std::endl;
                    throw "Could not freaking open the file!";
                }


                have_markov = true;
                markov_out.resize(4);
                char tmp_chr;
                std::string line;
                hInFile_.seekg(0, std::ios::beg);
                getline(hInFile_, line);
                // std::cout << "this was what I read: " << line << "\n";
                std::copy(line.begin(), line.end(), markov_out.begin());
                //    hInFile_.read(&(markov_out[0]), 4*sizeof(char));
                std::cout << " reading the markov" << (int) markov_out[0] << "," << (int) markov_out[1] << "," << (int) markov_out[2] << "," << (int) markov_out[3] << std::endl;
            }

            ///////////////////////////
            /// Change Channel depending on channel occupancy by the PU
            ///////////////////////////
            
            if (have_markov)
            {
                process_sensing(ch_power, markov_out);
            }
            else
                process_sensing(ch_power);


            // print power levels for each channel
#ifdef DEBUG_MODE
            tnow = time(0);
            // print power levels for each channel
            if (difftime(tnow, tlast) > 0.01)
            {
                std::cout << "Energy: " << print_vector_dB(ch_power);
                std::cout << "Signal Power: " << e_detec.noise_filter->print_ch_sig_power();
                std::cout << "p(Detection): " << e_detec.noise_filter->print_ch_pdetec();
                std::cout << "Noise Floor: " << e_detec.noise_filter->print_ch_noise_floor();
                //learner.print_marchov();
                tlast = tnow;
            }
#endif


        }
    }
    catch (boost::thread_interrupted)
    {
        std::cout << "Receive thread interrupted." << std::endl;
    }

}

/**
 * Compares the current dwell estimate with the previous one. If they are 
 * approximately the same for more than "steady_state" times, the second return
 * is True
 */
std::pair<double, bool> OfdmTransceiver::DwellEst(DwellTimeEstimator &Dwell, double &previous_dwelltime, int &dwell_counter, int steady_state, double steady_state_Th)
{

    std::pair<double, bool> DwellOut;

    double t_dwell = Dwell.dwelltime();
    DwellOut.first = t_dwell;

    if (pow((t_dwell - previous_dwelltime), 2) < pow((t_dwell * (steady_state_Th)), 2))
    {
        dwell_counter++;
    }
    else
    {
        dwell_counter = 0;
    }
    previous_dwelltime = t_dwell;
    
    if (dwell_counter > steady_state)
    {
        DwellOut.second = true;
        return DwellOut;
    }
    else
    {
        DwellOut.second = false;
        return DwellOut;
    }

}

/**
 * Changes the SU's channel based on spectrum occupancy
 */
void OfdmTransceiver::process_sensing(std::vector<float> ChPowers, std::vector<uint8_t> markov_out)
{
    // std::cout << reconfigure_counter << std::endl;
    reconfigure_counter++;
    // std::vector<int> notfree;
    ChPowers[current_channel] = 0;
    //std::cout << "noise floor: [" << e_detec.noise_filter->ch_noise_floor(0) << ", " << e_detec.noise_filter->ch_noise_floor(1) << ", " << e_detec.noise_filter->ch_noise_floor(2) << ", " << e_detec.noise_filter->ch_noise_floor(3) << "]\n";
    //std::cout << "energy: [" << e_detec.noise_filter->ch_sig_power(0) << ", " << e_detec.noise_filter->ch_sig_power(1) << ", " << e_detec.noise_filter->ch_sig_power(2) << ", " << e_detec.noise_filter->ch_sig_power(3) << "]\n";
    //std::cout << "cur energy: [" << 10*log10(ChPowers[0]) << "," << 10*log10(ChPowers[1]) << "," << 10*log10(ChPowers[2]) << "," << 10*log10(ChPowers[3]) << "], cur ch: " <<  current_channel << "\n";
    e_detec.noise_filter->filter(ChPowers);
    
    int ch = pu_register.hopping_required(ChPowers);

    // If the PU was not detected, it means that it is in our channel
    if (ch >= 0 && reconfigure_counter > min_reconfigure_wait) //|| numfree == ChPowers.size())
    {
        //std::cout << "cur energy: [" << 10*log10(ChPowers[0]) << "," << 10*log10(ChPowers[1]) << "," << 10*log10(ChPowers[2]) << "," << 10*log10(ChPowers[3]) << "], cur ch: " <<  current_channel << "\n";
        //std::cout << "noise floor: [" << e_detec.noise_filter->ch_noise_floor(0) << ", " << e_detec.noise_filter->ch_noise_floor(1) << ", " << e_detec.noise_filter->ch_noise_floor(2) << ", " << e_detec.noise_filter->ch_noise_floor(3) << "]\n";
        //std::cout << "sig energy: [" << e_detec.noise_filter->ch_sig_power(0) << ", " << e_detec.noise_filter->ch_sig_power(1) << ", " << e_detec.noise_filter->ch_sig_power(2) << ", " << e_detec.noise_filter->ch_sig_power(3) << "]\n";

        //std::cout << "CHAAAAAAAAAAANGE PLACES!" << std::endl;

        reconfigure_counter = 0;

        // channel map will be defined by learning code        
        std::map<int, int> channel_map;
        channel_map[0] = 2;
        channel_map[1] = 0;
        channel_map[2] = 3;
        channel_map[3] = 1;

        //std::cout << "size is :" << markov_out.size();
        //if (markov_out.size() != 0)
        //    reconfigure_usrp(markov_out[current_channel] - 1);
        //else
        //    reconfigure_usrp(channel_map[current_channel]);
        // find_next_channel(); LUT based on Jonathans learning;
        reconfigure_usrp(ch);
    }


}


// set transmitter frequency

void OfdmTransceiver::set_tx_freq(float freq)
{
    std::cout << boost::format("Setting TX Center Frequency: %f") % freq << std::endl;
    uhd::tune_request_t request(freq);
    uhd::tune_result_t result = usrp_tx->set_tx_freq(request);

    if (params_.debug)
    {
        std::cout << result.to_pp_string() << std::endl;
    }
    std::cout << "Actual TX Frequency: " << (usrp_tx->get_tx_freq() / 1e6) << " MHz" << std::endl;
}

// set transmitter sample rate

void OfdmTransceiver::set_tx_rate(float rate)
{
    //set transmit parameter
    std::cout << boost::format("Setting TX Rate: %f Msps...") % (rate / 1e6) << std::endl;
    usrp_tx->set_tx_rate(rate);
    std::cout << boost::format("Actual TX Rate: %f Msps...") % (usrp_tx->get_tx_rate() / 1e6) << std::endl << std::endl;
}

// set transmitter software gain

void OfdmTransceiver::set_tx_gain_soft(float gain)
{
    tx_gain = powf(10.0f, gain / 20.0f);
}

// set transmitter hardware (UHD) gain

void OfdmTransceiver::set_tx_gain_uhd(float gain)
{
    std::cout << boost::format("Setting TX Gain %f") % gain << std::endl;
    usrp_tx->set_tx_gain(gain);
    std::cout << "Actual TX gain: " << usrp_tx->get_tx_gain() << std::endl;
}

// set transmitter antenna

void OfdmTransceiver::set_tx_antenna(const string& _tx_antenna)
{
    usrp_tx->set_tx_antenna(_tx_antenna);
    std::cout << "Using TX Antenna: " << usrp_tx->get_tx_antenna() << std::endl;
}

// reset transmitter objects and buffers

void OfdmTransceiver::reset_tx()
{
    ofdmflexframegen_reset(fg);
}


//
// receiver methods
//

// set receiver frequency

void OfdmTransceiver::set_rx_freq(float _rx_freq)
{
    usrp_rx->set_rx_freq(_rx_freq);
    std::cout << "Actual RX Frequency: " << (usrp_rx->get_rx_freq() / 1e6) << " MHz" << std::endl;
    boost::this_thread::sleep(boost::posix_time::milliseconds(500));

    // check LO Lock
    std::vector<std::string> sensor_names;
    sensor_names = usrp_rx->get_rx_sensor_names(0);
    if (std::find(sensor_names.begin(), sensor_names.end(), "lo_locked") != sensor_names.end())
    {
        uhd::sensor_value_t lo_locked = usrp_rx->get_rx_sensor("lo_locked", 0);
        std::cout << "Checking RX: " << lo_locked.to_pp_string() << "..." << std::endl;
        if (!lo_locked.to_bool())
            std::cout << "Failed to lock LO" << std::endl;
    }
}

// set receiver sample rate

void OfdmTransceiver::set_rx_rate(float _rx_rate)
{
    usrp_rx->set_rx_rate(_rx_rate);
    std::cout << "Actual RX Rate: " << (usrp_rx->get_rx_rate() / 1e6) << " Msps" << std::endl;
}

// set receiver hardware (UHD) gain

void OfdmTransceiver::set_rx_gain_uhd(float _rx_gain_uhd)
{
    usrp_rx->set_rx_gain(_rx_gain_uhd);
    std::cout << "Actual RX gain: " << usrp_rx->get_rx_gain() << " dB" << std::endl;
}

// set receiver antenna

void OfdmTransceiver::set_rx_antenna(const std::string& _rx_antenna)
{
    usrp_rx->set_rx_antenna(_rx_antenna);
    std::cout << "Using RX Antenna: " << usrp_rx->get_rx_antenna() << std::endl;
}

// reset receiver objects and buffers

void OfdmTransceiver::reset_rx()
{
    //ofdmflexframesync_reset(fs);
}


