/**
 * \file controllers/RfFrontEnd/ForgeController.h
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

#ifndef CONTROLLERS_FORGECONTROLLER_H_
#define CONTROLLERS_FORGECONTROLLER_H_

#include "boost/scoped_ptr.hpp"
#include "irisapi/Controller.h"

#include "ForgeEventInterface.h"
#include "utility/ForgeUtilities.h"

namespace iris {

using namespace std;

typedef std::complex<float> Cplx;

/**
 * Structure to order events in a set based on their name
 */
struct event_comparator {

    std::string as_string(const ForgeEvent* ev) const {
        return ev->event_name;
    }

    std::string as_string(const string &ev_name) const {
        return ev_name;
    }

    std::string as_string(const ForgeEvent& ev) const {
        return ev.event_name;
    }

    template< typename T1, typename T2 >
    bool operator()(T1 const& t1, T2 const& t2) const {
        return as_string(t1) < as_string(t2);
    }
};

class ForgeController : public Controller {
public:
    ForgeController();
    virtual void subscribeToEvents();
    /**
     * Define here the handlers for each type of event.
     */
    virtual void initialize();
    /**
     * Processes the incoming event, attaching it to its specific handler. The handler must be stored in the ev_handlers
     * @param e Object with the event name and associated data
     */
    virtual void processEvent(Event &e);
    virtual void destroy();

    // Components names
    string usrptx_comp_name_x;
    string usrptx_engine_name_x;
    string usrprx_comp_name_x;
    string usrprx_engine_name_x;
    string radarmac_comp_name_x;
    string radarmac_engine_name_x;
    string powervstime_comp_name_x;
    string spectrogram_comp_name_x;
    string radarrx_comp_name_x;
    string radartx_comp_name_x;
    string radartx_engine_name_x;

    int command_port_x;

    AnvilSession *anvil_session;
    
    double* sample_rate_ptr;
    double* frequency_ptr;
    
    // wait for forgecommand ack
    boost::mutex pevent_mutex;
    int waiting_for_ack;
    list<Event> postponed_events;

    /**
     * Once the IP and port are set, this function is called by the anvil_session
     */
    void start_radio();
    void reset_anvil_session();
private:
    /**
     * Thread function to interface with the TCP connection
     */
    void socketThreadFunction();
    void consumer(iris::socket_command::TCPEventReceiver *ev);

    // PHP Socket Thread
    boost::scoped_ptr< boost::thread > socketThread_;

    set<ForgeEvent*, event_comparator> ev_handlers;
    typedef set<ForgeEvent*>::iterator EvIt;
};

} // namespace iris

#endif // CONTROLLERS_ANVILDISPLAYCONTROLLER_H_
