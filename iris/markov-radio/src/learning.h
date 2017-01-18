/* 
 * File:   learning.h
 * Author: jonathan
 *
 * Created on 31 July 2015, 12:46
 */
#include <vector>
#include <list>
#include <complex>
#include "markov_chain.h"
#include <boost/ptr_container/ptr_deque.hpp>
#include <liquid/liquid.h>
#include "dyspanradio.h"
#include "Buffer.h"
#include "channels.h"

#ifndef LEARNING_H
#define	LEARNING_H

class learning{
public:
    learning();
    learning(double);
    int process(int, double, std::vector<float>, char);
    int statistical(int, int);
    int markov(int, int);
    void print_distribution();
    void print_marchov();
    void pass_dwell_time(double);
    ~learning();
    void compare_algorithms();
private:
    int total_runs;
    int total_transitions;
    int channel_distribution[4];
    int previous_pu;
    double last_transition_time;
    double dwelltime;
    int period;
    markov_chain m;
    int su_transitions_s;
    int su_transitions_m;
    //float threshold;
    //int min_period;
    //float average_min_period;
    //int count;
        
};

#endif	/* LEARNING_H */

