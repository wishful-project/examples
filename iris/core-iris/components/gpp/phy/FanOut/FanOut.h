/**
 * \file components/gpp/phy/Example/ExampleComponent.h
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
 * An example PhyComponent to be used as a template for new PhyComponents.
 */

#ifndef FANOUT_H_
#define FANOUT_H_

#include <boost/bind.hpp>
#include "irisapi/PhyComponent.h"
//#include <functional>

using namespace std;

namespace iris
{
namespace phy
{

/*struct Adder{
  template<typename T> T operator()(T i, T j) const { return i+j; };
};*/

/*template<typename T>
struct Adder : public std::binary_function<T,T,T> {
  T operator() (T a, T b) {return (a+b);}
};
struct Multiplier : public std::binary_function<T,T,T> {
  T operator() (T a, T b) {return (a*b);}
};*/

class FanOut : public PhyComponent {
 public:
  FanOut(std::string name);

  virtual void calculateOutputTypes( std::map<std::string, int>& inputTypes, std::map<std::string, int>& outputTypes);

  virtual void registerPorts();

  virtual void initialize();
  virtual void process();
  template<typename T> void process_op();
  
  //template<typename T> operator_obj;

 private:
 
  string param_datatype_;
  int numoutputs_;
  //int num_calls_;
};

} // namespace phy
} // namespace iris

#endif // FANOUT_H_
