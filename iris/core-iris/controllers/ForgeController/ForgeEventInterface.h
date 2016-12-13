#ifndef FORGEEVENTINTERFACE_H_
#define FORGEEVENTINTERFACE_H_

#include "utility/ForgeUtilities.h"

namespace iris
{

using namespace std;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////// Auxiliary Functions /////////////////////////////
////////////////////////////////////////////////////////////////////////////////

/**
 * An auxiliary procedural function that adds a reconfigured parameter to a reconfiguration set object.
 * @param r reconfiguration set object to which the reconfigured parameter will be added
 * @param param_name string representing the name of the parameter exposed by the component
 * @param param_value new parameter value
 * @param engine_name engine containing the affected component
 * @param comp_name affected component
 */
void reconfigure_parameter(ReconfigSet &r, const std::string &param_name, const std::string &param_value, const std::string &engine_name, const std::string &comp_name);

/**
 * An auxiliary procedural function that fills a Command object with a "forgecommand" message. 
 * This is an alternative to the function "reconfigure_parameter()" in case the reconfiguration is done through commands instead of direct reconfiguration
 * of exposed parameters in the component.
 * The command data member will be a vector of bytes containing a string with the format: "e.eventName:e.data.front()\n", where e is the event given as argument
 * @param comm Command that will be filled with data
 * @param e Event name (e.g. set_frequency) that will be interpreted by the component
 * @param engine_name engine containing the affected component
 * @param comp_name name of the component that will receive the command
 */
Command generate_forgecommand(const std::string &ev_name, const std::string &param_value, const string &engine_name, const string &comp_name);



////////////////////////////////////////////////////////////////////////////////
///////////////////////////// Event handler classes ////////////////////////////
////////////////////////////////////////////////////////////////////////////////

class ForgeController;

/**
 * Parent Event handler class to make the Forge interface. It does nothing on itself. It just has an event name (e.g. "set_parameter")
 * associated to it and the controller where it will act.
 * Note: I couldn't make it an abstract class because for set find procedures I need to be able to create dummy objects
 */
class ForgeEvent
{
protected:
    ForgeController *controller_ptr;
public:
    string event_name;

    ForgeEvent(ForgeController *_controller_ptr, const std::string &_event_name) : controller_ptr(_controller_ptr), event_name(_event_name)
    {
    }

    virtual void process(const Event &e)
    {
    } // can't make it abstract class because of stupid dummy search in sets

    bool operator<(const ForgeEvent &rhs) const
    {
        return event_name < rhs.event_name;
    }
};

/**
 * Event handler class that is used to send data to the Anvil server for GUI display.
 */
class AnvilEvent : public ForgeEvent
{
public:
    bool open; ///< Flag that tells if a packet was already sent in the current session
    AnvilTag tag; ///< Tag sent in every protobuf packet to help Anvil distinguish packets directed at different plots
    anvil_interface::DATA_TYPE data_type; ///< What data type will we send? (options: cplx (IQ or mag/phase), float or power spectrum density)

    AnvilEvent(ForgeController *_controller_ptr, const std::string &_event_name, AnvilTag _tag, anvil_interface::DATA_TYPE _type) :
    ForgeEvent(_controller_ptr, _event_name), open(false), tag(_tag), data_type(_type)
    {
    }
    virtual void process(const Event &e);

    string getName()
    {
        return "AnvilEventHandler";
    }
};

/**
 * Event handler class that is used to process commands that come from the PHP or any other interface external to IRIS. It is an abstract class.
 * It may configure more than one component in the radio. For instance a parameter like the frequency may be configured both at the usrp tx and rx.
 */
class ReconfEvent : public ForgeEvent
{
protected:
    std::list<std::string> comp_names;
    std::list<std::string> eng_names;
    double mult_factor; ///< if we want to change the scale of the new value for the affected parameter (e.g. convert from Hz to kHz). Default value is 1
    std::string last_param_value;

    ReconfEvent(ForgeController* ptr, const string&_ev_name, const string &_comp_name, const string &_eng_name, double _mult_factor = 1)
    : ForgeEvent(ptr, _ev_name), mult_factor(_mult_factor)
    {
        comp_names.push_back(_comp_name);
        eng_names.push_back(_eng_name);
    }

    ReconfEvent(ForgeController* ptr, const string&_ev_name, const std::list<std::string> &_comp_names, const std::list<std::string> &_eng_names, double _mult_factor = 1)
    : ForgeEvent(ptr, _ev_name), mult_factor(_mult_factor)
    {
        if (_eng_names.size() != _comp_names.size())
            throw std::invalid_argument("Number of engines and components does not match");
        std::list<std::string>::const_iterator comp_it = _comp_names.begin(), eng_it = _eng_names.begin();
        while (comp_it != _comp_names.end())
        {
            comp_names.push_back(*comp_it);
            eng_names.push_back(*eng_it);
            comp_it++;
            eng_it++;
        }
    }

    virtual void process(const Event &e) = 0;
};

/**
 * Event handler class that is used to configure directly the parameters of the radio.
 */
class ParamSetterEvent : public ReconfEvent
{
    std::string param_name;
public:

    ParamSetterEvent(ForgeController*ptr, const string&_ev_name, const std::string &_param_name, const std::string &_comp_name, const std::string &_eng_name, double _mult_factor = 1) :
    ReconfEvent(ptr, _ev_name, _comp_name, _eng_name, _mult_factor), param_name(_param_name)
    {
    }

    ParamSetterEvent(ForgeController*ptr, const string&_ev_name, const std::string &_param_name, const std::list<std::string> &_comp_names, const std::list<std::string> &_eng_names, double _mult_factor = 1) :
    ReconfEvent(ptr, _ev_name, _comp_names, _eng_names, _mult_factor), param_name(_param_name)
    {
    }

    virtual void process(const Event &e);

    virtual std::string getName()
    {
        return "ParamSetter";
    }
};

/**
 * Event handler class that is used to send commands to a component.
 */
class ForgeCommandEvent : public ReconfEvent
{
public:

    ForgeCommandEvent(ForgeController* ptr, const string&_ev_name, const std::string &_comp_name, const std::string &_eng_name, double _mult_factor = 1)
    : ReconfEvent(ptr, _ev_name, _comp_name, _eng_name, _mult_factor)
    {
    }

    ForgeCommandEvent(ForgeController*ptr, const string&_ev_name, const std::list<std::string> &_comp_names, const std::list<std::string> &_eng_names, double _mult_factor = 1) :
    ReconfEvent(ptr, _ev_name, _comp_names, _eng_names, _mult_factor)
    {
    }

    virtual void process(const Event &e);

    virtual std::string getName()
    {
        return "ForgeCommander";
    }
};


class GenericReconfEvent : public ForgeEvent
{
public:
    GenericReconfEvent(ForgeController* ptr, const string&_ev_name)
    : ForgeEvent(ptr, _ev_name)
    {
    }
    
    virtual void process(const Event &e);
    
    std::string getName() {return "GenericReconfEvent";}
};
/**
 * Handler of an Anvil Session. It only starts the radio once the IP and port are set.
 */
class AnvilSession
{
private:
    ForgeController *controller;
    std::string address;
    int port;
    anvil_interface::AnvilProtobufTcpTx *anvil_socket;
public:

    AnvilSession(ForgeController *ptr) : controller(ptr), anvil_socket(NULL)
    {
        reset();
    }

    void close_connection()
    {
        if (!is_closed())
        {
            delete anvil_socket;
            anvil_socket = NULL;
        }
    }

    inline bool is_closed()
    {
        return anvil_socket == NULL;
    }

    void reset()
    {
        close_connection();
        address = "";
        port = -1;
    }

    void set_address(const string &_addr)
    {
        if (address == _addr)
            return;
        address = _addr;
        if (address != "" && port > 0)
            start();
    }

    void set_port(const int _port)
    {
        if (port == _port)
            return;
        port = _port;
        if (address != "" && port > 0)
            start();
    }

    std::string get_address()
    {
        return address;
    }

    int get_port()
    {
        return port;
    }

    void start();

    bool write_pkt(const std::vector<boost::any> &data, AnvilTag tag)
    {
        if (!is_closed())
            return anvil_socket->write_pkt(data, tag);
        return false;
    }

    bool initiate_session(AnvilTag tag, anvil_interface::DATA_TYPE data_type)
    {
        if (is_closed())
            return false;
        anvil_socket->initiate_session(tag, data_type);
        return true;
    }

    bool initiate_session(AnvilTag tag, float min_freq, float max_freq, int Nbins)
    {
        if (is_closed())
            return false;
        anvil_socket->initiate_psd_session(tag, min_freq, max_freq, Nbins);
        return true;
    }

    std::string getName()
    {
        return "AnvilSession";
    }
};

} //namespace iris

#endif