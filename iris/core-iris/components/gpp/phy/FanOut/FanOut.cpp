/**
 * \file components/gpp/phy/Example/ExampleComponent.cpp
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
 * Implementation of an example PhyComponent to be used as a template
 * for new PhyComponents.
 */

#include "FanOut.h"

#include "irisapi/LibraryDefs.h"
#include "irisapi/Version.h"

#include <boost/lambda/lambda.hpp>

using namespace std;
//using namespace boost::lambda;

namespace iris {
namespace phy {

// export library symbols
IRIS_COMPONENT_EXPORTS(PhyComponent, FanOut);

FanOut::FanOut(std::string name) : PhyComponent(name, "operatorcomponent", "An operator phy component", "Francisco Paisana", "0.1") {
  list<string> allowedTypes;
  allowedTypes.push_back(TypeInfo< uint8_t >::name());
  allowedTypes.push_back(TypeInfo< uint16_t >::name());
  allowedTypes.push_back(TypeInfo< uint32_t >::name());
  allowedTypes.push_back(TypeInfo< uint64_t >::name());
  allowedTypes.push_back(TypeInfo< int8_t >::name());
  allowedTypes.push_back(TypeInfo< int16_t >::name());
  allowedTypes.push_back(TypeInfo< int32_t >::name());
  allowedTypes.push_back(TypeInfo< int64_t >::name());
  allowedTypes.push_back(TypeInfo< float >::name());
  allowedTypes.push_back(TypeInfo< double >::name());
  allowedTypes.push_back(TypeInfo< long double >::name());
  allowedTypes.push_back(TypeInfo< complex<float> >::name());
  allowedTypes.push_back(TypeInfo< complex<double> >::name());
  allowedTypes.push_back(TypeInfo< complex<long double> >::name());
  
  registerParameter("datatype", "Type of data in input and outputs", "uint8_t", false, param_datatype_, allowedTypes);
  registerParameter("numoutputs", "Number of outputs", "2", false, numoutputs_);
}

void FanOut::registerPorts() {
  //Register all ports
  vector<int> validTypes;
  validTypes.push_back( int(TypeInfo< uint8_t >::identifier) );
  validTypes.push_back( int(TypeInfo< uint16_t >::identifier) );
  validTypes.push_back( int(TypeInfo< uint32_t >::identifier) );
  validTypes.push_back( int(TypeInfo< uint64_t >::identifier) );
  validTypes.push_back( int(TypeInfo< int8_t >::identifier) );
  validTypes.push_back( int(TypeInfo< int16_t >::identifier) );
  validTypes.push_back( int(TypeInfo< int32_t >::identifier) );
  validTypes.push_back( int(TypeInfo< int64_t >::identifier) );
  validTypes.push_back( int(TypeInfo< float >::identifier) );
  validTypes.push_back( int(TypeInfo< double >::identifier) );
  validTypes.push_back( int(TypeInfo< long double >::identifier) );
  validTypes.push_back( int(TypeInfo< complex<float> >::identifier) );
  validTypes.push_back( int(TypeInfo< complex<double> >::identifier) );
  validTypes.push_back( int(TypeInfo< complex<long double> >::identifier) );

  registerInputPort("input1", validTypes);
  for(int i = 1; i <= numoutputs_; i++) {
    stringstream ss;
    ss << "output";
    ss << i;
    registerOutputPort(ss.str(), validTypes);
  }
}

void FanOut::calculateOutputTypes( std::map<std::string,int>& inputTypes, std::map<std::string,int>& outputTypes) {
//Set output type
    for(int i = 1; i <= numoutputs_; i++) {
        stringstream ss;
        ss << "output";
        ss << i;
        if( param_datatype_ == "uint8_t" )
            outputTypes[ss.str()] = TypeInfo< uint8_t >::identifier;
        if( param_datatype_ == "uint16_t" )
          outputTypes[ss.str()] = TypeInfo< uint16_t >::identifier;
        if( param_datatype_ == "uint32_t" )
          outputTypes[ss.str()] = TypeInfo< uint32_t >::identifier;
        if( param_datatype_ == "uint64_t" )
          outputTypes[ss.str()] = TypeInfo< uint64_t >::identifier;
        if( param_datatype_ == "int8_t" )
          outputTypes[ss.str()] = TypeInfo< int8_t >::identifier;
        if( param_datatype_ == "int16_t" )
          outputTypes[ss.str()] = TypeInfo< int16_t >::identifier;
        if( param_datatype_ == "int32_t" )
          outputTypes[ss.str()] = TypeInfo< int32_t >::identifier;
        if( param_datatype_ == "int64_t" )
          outputTypes[ss.str()] = TypeInfo< int64_t >::identifier;
        if( param_datatype_ == "float" )
          outputTypes[ss.str()] = TypeInfo< float >::identifier;
        if( param_datatype_ == "double" )
            outputTypes[ss.str()] = TypeInfo< double >::identifier;
        if( param_datatype_ == "long double" )
            outputTypes[ss.str()] = TypeInfo< long double >::identifier;
        if( param_datatype_ == "complex<float>" )
            outputTypes[ss.str()] = TypeInfo< complex<float> >::identifier;
        if( param_datatype_ == "complex<double>" )
            outputTypes[ss.str()] = TypeInfo< complex<double> >::identifier;
        if( param_datatype_ == "complex<long double>" )
            outputTypes[ss.str()] = TypeInfo< complex<long double> >::identifier;
    }
}

void FanOut::initialize() {
  //num_calls_=0;
}

void FanOut::process() {
  switch (outputBuffers[0]->getTypeIdentifier()) {
    case TypeInfo<uint8_t>::identifier:
      process_op<uint8_t> ();
      break;
    case TypeInfo<uint16_t>::identifier:
      process_op<uint16_t> ();
      break;
    case TypeInfo<uint32_t>::identifier:
      process_op<uint32_t> ();
      break;
    //case TypeInfo<uint64_t>::identifier:
    //  process_op<uint64_t> ();
    //  break;
    case TypeInfo<int8_t>::identifier:
      process_op<int8_t> ();
      break;
    case TypeInfo<int16_t>::identifier:
      process_op<int16_t> ();
      break;
    case TypeInfo<int32_t>::identifier:
      process_op<int32_t> ();
      break;
    //case TypeInfo<int64_t>::identifier:
    //  process_op<int64_t> ();
    //  break;
    case TypeInfo<float>::identifier:
      process_op<float> ();
      break;
    case TypeInfo<double>::identifier:
      process_op<double> ();
      break;
    case TypeInfo<long double>::identifier:
      process_op<long double> ();
      break;
    case TypeInfo<complex<float> >::identifier:
      process_op<complex<float> > ();
      break;
    case TypeInfo<complex<double> >::identifier:
      process_op<complex<double> > ();
      break;
    case TypeInfo<complex<long double> >::identifier:
      process_op<complex<long double> > ();
      break;
    default:
      break;
  }
}

template<typename T> void FanOut::process_op() {
  DataSet< T >* readDataSet;
  getInputDataSet("input1", readDataSet);
  std::size_t curSize = readDataSet->data.size();

  //if(abs(readDataSet->timeStamp - round(readDataSet->timeStamp)) < 0.0003)
   //   LOG(LDEBUG) << "timestamp: " << readDataSet->timeStamp;

  vector< DataSet< T >* > outSets(numoutputs_);
  for(int i = 0; i < numoutputs_; i++)
  {
    stringstream ss;
    ss << "output";
    ss << (i+1);
    getOutputDataSet(ss.str(), outSets[i], curSize);
    outSets[i]->sampleRate = readDataSet->sampleRate;
    outSets[i]->timeStamp = readDataSet->timeStamp;
    copy(readDataSet->data.begin(), readDataSet->data.end(), outSets[i]->data.begin());
  
    //Release the DataSets
    releaseOutputDataSet(ss.str(), outSets[i]);
  }
  releaseInputDataSet("input1", readDataSet);
}

} // namesapce phy
} // namespace iris
