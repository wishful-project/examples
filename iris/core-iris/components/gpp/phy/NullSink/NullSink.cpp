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

#include "NullSink.h"

#include "irisapi/LibraryDefs.h"
#include "irisapi/Version.h"

using namespace std;

namespace iris
{
namespace phy
{

// export library symbols
IRIS_COMPONENT_EXPORTS(PhyComponent, NullSink);

NullSink::NullSink(std::string name)
  : PhyComponent(name,                      // component name
                "example",                  // component type
                "Clears the buffer. Does nothing with input data", // description
                "Francisco",              // author
                "0.1")                      // version
{
}

void NullSink::registerPorts()
{
  registerInputPort("input1", TypeInfo< complex<float> >::identifier);
}

void NullSink::calculateOutputTypes(
    std::map<std::string,int>& inputTypes,
    std::map<std::string,int>& outputTypes)
{
}

void NullSink::initialize()
{
}

void NullSink::process()
{
  //Get a DataSet from the input DataBuffer
  DataSet< complex<float> >* readDataSet = NULL;
  getInputDataSet("input1", readDataSet);
  //std::size_t size = readDataSet->data.size();

  // DO NOTHING
  //Release the DataSets
  releaseInputDataSet("input1", readDataSet);
}

} // namesapce phy
} // namespace iris
