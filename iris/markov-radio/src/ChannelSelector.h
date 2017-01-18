/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   LearningSession.h
 * Author: xico
 *
 * Created on 02 December 2016, 12:49
 */

#ifndef CHANNELSELECTOR_H
#define CHANNELSELECTOR_H

#include "MarkovChain.h"

using std::pair;
using std::vector;

class ChannelSelector {
public:
    ChannelSelector(int Nch_);
    ChannelSelector(const ChannelSelector& orig);
    void update_statistics(int pu_channel, double timestamp);
    int learning_update(double timestamp, const std::vector<float>& powers, int current_channel = -1);
    int select_next_channel(int current_channel, double timestamp, const std::vector<float>& powers);
    
    // setters/getters
    inline int num_total_transitions() const {return total_transitions;};
    inline void set_dwelltime(double d) { dwelltime_ = d;};
    inline double dwelltime() const { return dwelltime_;};
    inline MarkovChain& markov_matrix() {return mkr;};
    
private:
    int Nch;
    int total_runs = 0;
    vector<int> channel_distribution;
    int previous_pu = -1;
    int total_transitions = -1;
    double last_transition_time = -1;
    double dwelltime_ = -1;
    int period = 0;
    
    MarkovChain mkr;
};

/**
 * This class will convert the channel power arrays into markov transitions.
 * Requirement: Knowing the dwell time / minimum time a PU stays in a channel
 */
//class ChannelHoppingStatistics
//{
//public:
//    ChannelHoppingStatistics(int Nch_);
//private:
//    int Nch;
//    MarkovChain mkr;
//};

#endif /* CHANNELSELECTOR_H */

