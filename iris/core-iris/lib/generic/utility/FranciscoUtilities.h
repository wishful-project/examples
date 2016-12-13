/**
 * \file FirFilter.h
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
 * FIR Filter classes.
 */

#include <vector>
#include <deque>
#include <algorithm>

#include <boost/scoped_ptr.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/thread/condition_variable.hpp>
#include "utility/UdpSocketTransmitter.h"

namespace iris
{

class SuperCondition {
    bool isConditionReady_;
    boost::condition_variable condition_;
    boost::mutex internMutex_;

public:
    SuperCondition() : isConditionReady_(false) {}
    inline void waitOnCondition() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        while(!isConditionReady_) {
            condition_.wait(lock);
        }
        isConditionReady_ = false;
    }
    inline void notify() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        isConditionReady_ = true;
        condition_.notify_one();
    }
    inline bool timed_wait(double &time_sec) {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        bool ret;
        if(!isConditionReady_) {
            ret = condition_.timed_wait(lock, boost::posix_time::milliseconds(time_sec * 1000));
            isConditionReady_ = false; // needed?
            return ret;
        }
        isConditionReady_ = false;
        return true;
    }
};

class SuperGate {
    bool isGateOpen_;
    boost::condition_variable condition_;
    boost::mutex internMutex_;

public:
    SuperGate() : isGateOpen_(true) {}
    inline void waitOnCondition() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        while(!isGateOpen_) {
            condition_.wait(lock);
        }
    }
    inline void open() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        isGateOpen_ = true;
        condition_.notify_all();
    }
    inline void close() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        isGateOpen_ = false;
    }
    inline bool isGateOpen() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        return isGateOpen_;
    }
};

class SuperTunnel {
    int num_inside_;
    int max_num_;
    boost::condition_variable cond_;
    boost::mutex internMutex_;
public:
    SuperTunnel(int max_num = 1) : num_inside_(0), max_num_(max_num) {}
    inline void enter() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        while(num_inside_ == max_num_)
            cond_.wait(lock);
        
        num_inside_++;
    }
    inline bool try_enter() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        if(num_inside_ == max_num_)
            return false;
        num_inside_++;
        return true;
    }
    inline bool try_timed_enter(int &time_sec) {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        bool ret;
        if(num_inside_ == max_num_) {
            ret = cond_.timed_wait(lock, boost::posix_time::milliseconds(time_sec * 1000));
            if(ret == true && num_inside_ != max_num_) {
                num_inside_++;
                return true;
            }
            return false;
        }
        num_inside_++;
        return true;
    }
    inline void exit() {
        boost::unique_lock<boost::mutex> lock(internMutex_);
        if(num_inside_ != 0)
            num_inside_--;
        cond_.notify_one();
    }
};

template<typename T>
void command2Protobuf(T &message, Command &com) {
    uint8_t byte_array[com.data.size()];

    for(uint32_t i = 0; i < com.data.size(); i++)
        byte_array[i] = boost::any_cast<uint8_t>(com.data[i]);

    message.ParseFromArray(byte_array, com.data.size());
}

template<typename T>
void protobuf2Array(std::vector<boost::uint8_t> &byte_vec, T &message) {
    byte_vec.resize(message.ByteSize());
    message.SerializeToArray(&byte_vec[0], message.ByteSize());
}

template<typename T>
void sendEvent2Socket(T &event, boost::scoped_ptr<UdpSocketTransmitter> &tx) {
    std::stringstream ss;
    ss << (boost::posix_time::microsec_clock::local_time()).time_of_day();
    event.set_time_of_day(ss.str());

    uint16_t pkt_length = event.ByteSize();
    std::vector<uint8_t> len_buffer(2);
    for(int i = 0; i < sizeof(pkt_length); i++) {
        len_buffer[i] = (( pkt_length >> ((sizeof(pkt_length) - 1 - i) * 8) ) & 0x00ff);
    }

    std::string buffer;
    event.SerializeToString(&buffer);

    tx->write(len_buffer.begin(), len_buffer.end());
    tx->write(buffer.begin(), buffer.end());
}

} // end of iris namespace

