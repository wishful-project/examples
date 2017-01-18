#include "ForgeController.h"

#include <sstream>

#include "irisapi/LibraryDefs.h"
#include "irisapi/Version.h"
#include <google/protobuf/io/coded_stream.h>
#include "../../lib/generic/utility/SerializationUtilities.h"

using namespace std;

namespace iris {

////////////////////////////////////////////////////////////////////////////////
////////////////////////////// Auxiliary Functions /////////////////////////////
////////////////////////////////////////////////////////////////////////////////

Command generate_forgecommand(const std::string &ev_name, const std::string &param_value, const string &engine_name, const string &comp_name) {
    return generate_command("forgecommand", convert_to_bytes(socket_command::create_forgecommand_string(ev_name, param_value)), engine_name, comp_name);
}

/**
 * Extracts the parameter value (in string format) from the event e. It may scale the parameter value by a factor "mult_factor" defined at the constructor.
 */
std::string get_param_value(const Event &e, double mult_factor = 1)
{
    std::string param_val;
    if (e.data.size() == 0)
    {
        param_val = "";
    }
    else
    {
        param_val = boost::any_cast<string>(e.data.front());
        if (mult_factor != 1)
        {
            double val;
            sscanf(param_val.c_str(), "%lf", &val);
            stringstream str;
            str << val * mult_factor;
            param_val = str.str();
        }
    }
    return param_val;
}

////////////////////////////////////////////////////////////////////////////////
///////////////////////////// Event handler classes ////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void ParamSetterEvent::process(const Event &e) {
    last_param_value = get_param_value(e, mult_factor);
    ReconfigSet r;
    std::list<std::string>::const_iterator comp_it = comp_names.begin(), eng_it = eng_names.begin();
    while (comp_it != comp_names.end()) {
        r.paramReconfigs.clear();
        r.paramReconfigs.push_back(reconfigure_parameter(param_name, last_param_value, *eng_it, *comp_it));
        controller_ptr->reconfigureRadio(r);
        comp_it++;
        eng_it++;
    }
}

void ForgeCommandEvent::process(const Event &e) {
    boost::unique_lock<boost::mutex> lock(controller_ptr->pevent_mutex);
    if(controller_ptr->waiting_for_ack > 0)
    {
        std::cout << "Event with name " << e.eventName << " was postponed\n";
        controller_ptr->postponed_events.push_back(e);
        return;
    }
    last_param_value = get_param_value(e, mult_factor);
    auto comp_it = comp_names.begin();
    auto eng_it = eng_names.begin();
    while (comp_it != comp_names.end()) 
    {
        controller_ptr->postCommand(generate_forgecommand(event_name, last_param_value, *eng_it, *comp_it));
        comp_it++;
        eng_it++;
        controller_ptr->waiting_for_ack++;
    }
}

void GenericReconfEvent::process(const Event &e)
{
    // Receive command with format: <engine>.<component>.<parameter>=<value>
    std::string command_data = get_param_value(e);
    auto delim1 = string_delimiter(command_data, "=\n");
    if(delim1.size() != 2)
        std::cout << "Error: Command format not valid\n";
    auto delim2 = string_delimiter(delim1.front(), ".");
    if(delim2.size() != 3)
        std::cout << "Error: Command format not valid\n";
        
    auto delim_it = delim2.begin();
    auto eng_it = delim_it++;
    auto comp_it = delim_it++;
    auto param_it = delim_it;
    auto value_it = delim1.rbegin();
    
    //std::cout << "Got generic event. set:" << *eng_it << "." << *comp_it << "." << *param_it << "=" << *value_it << std::endl;
    
    ReconfigSet r;
    r.paramReconfigs.push_back(reconfigure_parameter(*param_it, *value_it, *eng_it, *comp_it));
    controller_ptr->reconfigureRadio(r);
}

void AnvilEvent::process(const Event &e) {
    if (controller_ptr->anvil_session->is_closed()) {
        return;
    }
    bool ret;
    if (open == false) {
        if (data_type == anvil_interface::PSD_DATA) {
            //controller_ptr->nbins_x = e.data.size();
            ret = controller_ptr->anvil_session->initiate_session(tag, *(controller_ptr->frequency_ptr) - *(controller_ptr->sample_rate_ptr)/2, *(controller_ptr->frequency_ptr) + *(controller_ptr->sample_rate_ptr)/2, e.data.size());
        } else {
            ret = controller_ptr->anvil_session->initiate_session(tag, data_type);
        }
        if (ret == false)
            controller_ptr->reset_anvil_session();
        open = true;
    }
    if (controller_ptr->anvil_session->write_pkt(e.data, tag) == false)
        controller_ptr->reset_anvil_session();
}

void AnvilSession::start() {
    close_connection();
    anvil_socket = new anvil_interface::AnvilProtobufTcpTx(address, port);
    
    if(anvil_socket->is_open())
        controller->start_radio();
    else {
        reset();
        LOG(LERROR) << "Couldn't connect to host! Recheck your port and address.";
    }
}


} // namespace iris
