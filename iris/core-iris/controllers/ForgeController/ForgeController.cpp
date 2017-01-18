/**
 * \file controllers/RfFrontEnd/ForgeController.cpp
 * \version 1.0
 *
 * \section COPYRIGHT
 *
 * Copyright 2012-2013 The Iris Project Developers. See the
 * COPYRIGHT file at the top-level directory of this distribution
 * and at http://www.softwareradiosystems.com/iris/copyright.html.
 *
 * \section LICENSE
 *
 * This file is part of the Iris Project.
 *
 * Iris is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * Iris is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * A copy of the GNU Lesser General Public License can be found in
 * the LICENSE file in the top-level directory of this distribution
 * and at http://www.gnu.org/licenses/.
 *
 * \section DESCRIPTION
 *
 * A generic RF front-end controller. This controller
 * provides a gui to manually adjust parameters including frequency,
 * bandwidth and power.
 */

#include "ForgeController.h"

#include <sstream>

#include "irisapi/LibraryDefs.h"
#include "irisapi/Version.h"
#include <google/protobuf/io/coded_stream.h>


using namespace std;

namespace iris
{

class AddressSetter : public ForgeEvent
{
    string address;
public:

    AddressSetter(ForgeController* ptr) : ForgeEvent(ptr, "set_address")
    {
    }

    virtual void process(const Event &e)
    {
        string param = boost::any_cast<string>(e.data.front());
        controller_ptr->anvil_session->set_address(param); // "127.0.0.1";//"192.168.5.13";
        LOG(LDEBUG) << "Anvil Addr: " << param;
    }

    string getName()
    {
        return "IPAddressSetter";
    }

    string get_value()
    {
        return address;
    }
};

class PortSetter : public ForgeEvent
{
    int port;
public:

    PortSetter(ForgeController* ptr) : ForgeEvent(ptr, "set_port")
    {
    }

    virtual void process(const Event &e)
    {
        string param = boost::any_cast<string>(e.data.front());
        sscanf(param.c_str(), "%d", &port);
        controller_ptr->anvil_session->set_port(port);
        LOG(LDEBUG) << "Anvil Port: " << param;
    }

    string getName()
    {
        return "portSetter";
    }

    float get_value()
    {
        return port;
    }
};

class ParameterExposer : public ForgeEvent
{
public:
    ParameterExposer(ForgeController* ptr) : ForgeEvent(ptr, "expose_parameter")
    {
    }
    virtual void process(const Event &e)
    {
        vector<uint8_t> value_bytes = convert_to_bytes(e.data);
        TaggedValue taggedvalue(value_bytes);
        if(taggedvalue.tag == "rate")
        {
            controller_ptr->sample_rate_ptr = taggedvalue.get_value<double*>();
        }
        else if(taggedvalue.tag == "frequency")
        {
            controller_ptr->frequency_ptr = taggedvalue.get_value<double*>();
        }
        else
            LOG(LERROR) << "Tag not recognized";
    }
    string getName()
    {
        return "ParameterExposer";
    }
};
        
// END PHP Handlers

//! Export library functions
IRIS_CONTROLLER_EXPORTS(ForgeController);

ForgeController::ForgeController() : Controller("forgecontroller", "A generic front-end controller", "Francisco Paisana", "0.1")
{
    registerParameter("commandport", "Port for receiving commands", "1235", false, command_port_x);

    // Config. components
    registerParameter("usrptxcomponent", "Name of USRP-Tx component", "", false, usrptx_comp_name_x);
    registerParameter("usrptxengine", "Name of USRP-Tx engine", "", false, usrptx_engine_name_x);
    registerParameter("usrprxcomponent", "Name of USRP-Rx component", "", false, usrprx_comp_name_x);
    registerParameter("usrprxengine", "Name of USRP-Rx engine", "", false, usrprx_engine_name_x);
    registerParameter("maccomponent", "Name of ofdm mod component", "", false, radarmac_comp_name_x);
    registerParameter("macengine", "Name of mod engine", "", false, radarmac_engine_name_x);
    registerParameter("powervstimecomponent", "Name of spectrogram component", "", false, powervstime_comp_name_x);
    registerParameter("spectrogramcomponent", "Name of spectrogram component", "", false, spectrogram_comp_name_x);
    registerParameter("radarrxcomponent", "Name of radar Rx component", "", false, radarrx_comp_name_x);
    registerParameter("radartxcomponent", "Name of radar Tx component", "", false, radartx_comp_name_x);
    registerParameter("radartxengine", "Name of radar Tx component", "", false, radartx_engine_name_x);
}

void ForgeController::subscribeToEvents()
{
    subscribeToEvent("framedropevent", radarmac_comp_name_x);
    subscribeToEvent("powervstimeevent", powervstime_comp_name_x);
    subscribeToEvent("radarinterferenceevent", radarrx_comp_name_x);
    subscribeToEvent("cur_phase", radartx_comp_name_x);
    subscribeToEvent("expose_parameter", usrprx_comp_name_x);
    subscribeToEvent("psdevent", spectrogram_comp_name_x);
    subscribeToEvent("forgecommandack", radarmac_comp_name_x);
}

void ForgeController::initialize()
{
    waiting_for_ack = 0;
    anvil_session = new AnvilSession(this);

    // Register Anvil Events
    ev_handlers.insert(new AnvilEvent(this, "framedropevent", FRAME_DROP, anvil_interface::FLOAT_DATA));
    ev_handlers.insert(new AnvilEvent(this, "powervstimeevent", RX_POWER_TIME, anvil_interface::FLOAT_DATA));
    ev_handlers.insert(new AnvilEvent(this, "psdevent", PSD_BINS, anvil_interface::PSD_DATA));
    ev_handlers.insert(new AnvilEvent(this, "cur_phase", ROTATION, anvil_interface::FLOAT_DATA));
    ev_handlers.insert(new AnvilEvent(this, "radarinterferenceevent", TR_POWER_TIME, anvil_interface::FLOAT_DATA));

    list<string> usrp_comp_names;
    list<string> usrp_eng_names;
    if (usrptx_comp_name_x != "")
    {
        usrp_comp_names.push_back(usrptx_comp_name_x);
        usrp_eng_names.push_back(usrptx_engine_name_x);
        ev_handlers.insert(new ParamSetterEvent(this, "set_txgain", "gain", usrptx_comp_name_x, usrptx_engine_name_x));
    }
    if (usrprx_comp_name_x != "")
    {
        usrp_comp_names.push_back(usrprx_comp_name_x);
        usrp_eng_names.push_back(usrprx_engine_name_x);
        ev_handlers.insert(new ParamSetterEvent(this, "set_rxgain", "gain", usrprx_comp_name_x, usrprx_engine_name_x));
    }

    // Register Reconfig. Events
    ev_handlers.insert(new ParamSetterEvent(this, "set_frequency", "frequency", usrp_comp_names, usrp_eng_names, 1000.0));
    if (usrptx_comp_name_x != "" && radarmac_comp_name_x != "")
    {
        ev_handlers.insert(new ForgeCommandEvent(this, "set_safety_margin", radarmac_comp_name_x, radarmac_engine_name_x));
        ev_handlers.insert(new ForgeCommandEvent(this, "set_sensing_time", radarmac_comp_name_x, radarmac_engine_name_x));
        ev_handlers.insert(new ForgeCommandEvent(this, "force_sensing", radarmac_comp_name_x, radarmac_engine_name_x));
        ev_handlers.insert(new ForgeCommandEvent(this, "sharing_enable", radarmac_comp_name_x, radarmac_engine_name_x));
        ev_handlers.insert(new ForgeCommandEvent(this, "tx_enable", radarmac_comp_name_x, radarmac_engine_name_x));
    }
    if (radartx_comp_name_x != "")
    {
        ev_handlers.insert(new ParamSetterEvent(this, "radar_enable", "radar_enable", radartx_comp_name_x, radartx_engine_name_x));
        ev_handlers.insert(new ParamSetterEvent(this, "startradio", "startradio", radartx_comp_name_x, radartx_engine_name_x));
        // I have to set the sample rate at the Radar
        usrp_comp_names.push_back(radartx_comp_name_x);
        usrp_eng_names.push_back(radartx_engine_name_x);
    }
    ev_handlers.insert(new ParamSetterEvent(this, "set_bandwidth", "rate", usrp_comp_names, usrp_eng_names, 1000.0));
    ev_handlers.insert(new GenericReconfEvent(this, "set"));
    ev_handlers.insert(new AddressSetter(this));
    ev_handlers.insert(new PortSetter(this));
    
    ev_handlers.insert(new ParameterExposer(this));
    
    frequency_ptr = NULL;
    sample_rate_ptr = NULL;

    socketThread_.reset(new boost::thread(boost::bind(&ForgeController::socketThreadFunction, this)));
}

void ForgeController::processEvent(Event &e)
{
    // WARNING: THIS IS A RUSHED SOLUTION. Only works if we are sending forgecommands to a single component
    if(e.eventName == "forgecommandack")
    {
        boost::unique_lock<boost::mutex> lock(pevent_mutex);
        waiting_for_ack--;
        //LOG(LDEBUG) << "Received an ack for the command " << convert_to_string(e.data) << ". acks waiting: " << waiting_for_ack;
        if(waiting_for_ack == 0 && postponed_events.empty() == false)
        {
            Event ev = postponed_events.front();
            postponed_events.pop_front();
            LOG(LDEBUG) << "Gonna process the postponed event " << ev.eventName;
            lock.unlock();
            processEvent(ev);
        }
        return;
    }
    
    ForgeEvent* tmp = new ForgeEvent(this, e.eventName); // dummy object
    EvIt ev_it = ev_handlers.find(tmp);
    delete tmp;

    if (ev_it == ev_handlers.end())
    {
        LOG(LINFO) << "Event " << e.eventName << " not recognized. Ignored.";
        return;
    }
    
    //LOG(LINFO) << "Received event: " << e.eventName;
    (*ev_it)->process(e);
}

void ForgeController::destroy()
{
}

void
ForgeController::consumer(iris::socket_command::TCPEventReceiver *event_rx)
{
    list<pair<string, string> > event_list;

    int cont = 0;
    while( 1 )
    {
	    sleep(1);
	    if (event_rx->get_events(event_list))
	    {
		for (list<pair<string, string> >::iterator it = event_list.begin();
				it != event_list.end();
				it++)
		{
		    cont++;
		    Event *e = new Event();
		    e->eventName = it->first;
		    if (it->second != "")
		    {
			    std::cout << "Received Event: (" << it->first << ", " << it->second << ")" << std::endl;;
			e->data.push_back(it->second);
		    }
		    else
			std::cout << "Received Event: " << it->first << std::endl;
		    postEvent(*e);
		    delete e;
        	}

		event_list.clear();
	    }

	    std::cout << "Events Received: " << cont << std::endl;
    }
}

void ForgeController::socketThreadFunction()
{
    boost::asio::io_service io_service;
    iris::socket_command::TCPEventReceiver event_rx(io_service, command_port_x);
    event_rx.start_server();

    boost::thread iot(boost::bind(&ForgeController::consumer, this, &event_rx));
    io_service.run();

#if 0
    iris::socket_command::TCPEventReceiver event_rx(command_port_x);
    list<pair<string, string> > event_list;
    Event *e;
    while (true)
    {
        event_rx.receive_command(event_list);
        for (list<pair<string, string> >::iterator it = event_list.begin(); it != event_list.end(); it++)
        {
            e = new Event();
            e->eventName = it->first;
            if (it->second != "")
            {
                LOG(LINFO) << "Received Event: (" << it->first << ", " << it->second << ")";
                e->data.push_back(it->second);
            }
            else
                LOG(LINFO) << "Received Event: " << it->first;
            postEvent(*e);
            delete e;
        }
    }
#endif
}

void ForgeController::start_radio()
{
    if (radarmac_comp_name_x != "")
    { // Give the signal to the modulator to setup
        postCommand(generate_forgecommand("startradio", "", radarmac_engine_name_x, radarmac_comp_name_x));
        waiting_for_ack++;
    }
    else if (radartx_comp_name_x != "")
    {
        ReconfigSet r;
        r.paramReconfigs.push_back(reconfigure_parameter("startradio", true, radartx_engine_name_x, radartx_comp_name_x));
        reconfigureRadio(r);
    }
}

void ForgeController::reset_anvil_session()
{
    AnvilEvent *ev;
    for (EvIt it = ev_handlers.begin(); it != ev_handlers.end(); it++)
        if ((ev = dynamic_cast<AnvilEvent*> (*it)) != NULL)
            ev->open = false;
    anvil_session->reset();
}

} // namespace iris
