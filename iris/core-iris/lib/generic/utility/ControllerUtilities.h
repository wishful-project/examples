#ifndef CONTROLLERUTILITIES_H
#define	CONTROLLERUTILITIES_H

#include "SerializationUtilities.h"
#include "irisapi/Controller.h"

namespace iris {

/**
 * An auxiliary procedural function that adds a reconfigured parameter to a reconfiguration set object.
 * @param param_name string representing the name of the parameter exposed by the component
 * @param param_value new parameter value
 * @param engine_name engine containing the affected component
 * @param comp_name affected component
 */
inline ParametricReconfig reconfigure_parameter(const std::string &param_name, const std::string &param_value, const std::string &engine_name, const std::string &comp_name) {
    ParametricReconfig p;
    p.parameterName = param_name;
    p.parameterValue = param_value;
    p.engineName = engine_name;
    p.componentName = comp_name;
    //LOG(LDEBUG) << "Parameter " << p.parameterName << " set to " << p.parameterValue << " in " << p.engineName << ":" << p.componentName;
    return p;   // copy elision
}

template<typename T>
inline ParametricReconfig reconfigure_parameter(const std::string &param_name, const T &param_value, const std::string &engine_name, const std::string &comp_name) {
    ParametricReconfig p;
    p.parameterName = param_name;
    std::stringstream ss;
    ss << param_value;
    p.parameterValue = ss.str();
    p.engineName = engine_name;
    p.componentName = comp_name;
    //LOG(LDEBUG) << "Parameter " << p.parameterName << " set to " << p.parameterValue << " in " << p.engineName << ":" << p.componentName;
    return p;   // copy elision
}

/**
 * An auxiliary procedural function that fills a Command object with a "forgecommand" message. 
 * This is an alternative to the function "reconfigure_parameter()" in case the reconfiguration is done through commands instead of direct reconfiguration
 * of exposed parameters in the component.
 * The command data member will be a vector of bytes containing a string with the format: "e.eventName:e.data.front()\n", where e is the event given as argument
 * @param comm_name Command name string
 * @param data Data to place inside the command
 * @param engine_name engine containing the affected component
 * @param comp_name name of the component that will receive the command
 */
inline Command generate_command(const std::string &comm_name, const Event &e, const std::string &engine_name, const std::string &comp_name) {
    Command comm;
    comm.data = e.data;
    comm.typeId = e.typeId;
    comm.commandName = comm_name;
    comm.componentName = comp_name;
    comm.engineName = engine_name;
    
    return comm; // copy elision
}

template<typename T>
inline Command generate_command(const std::string &comm_name, const std::vector<T> &data, const std::string &engine_name, const std::string &comp_name) {
    Command comm;
    comm.data.reserve(data.size());
    for(int i = 0; i < data.size(); i++) {
        comm.data.push_back(data[i]);
    }
    comm.typeId = TypeInfo<T>::identifier;
    comm.commandName = comm_name;
    comm.componentName = comp_name;
    comm.engineName = engine_name;
    
    return comm; // copy elision
}

}

#endif	/* CONTROLLERUTILITIES_H */

