/* 
 * File:   LearningSession.cpp
 * Author: xico
 * 
 * Created on 02 December 2016, 12:49
 */

#include "ChannelSelector.h"
#include <cmath>
#include <iostream>

using std::cout;

ChannelSelector::ChannelSelector(int Nch_) :
        Nch(Nch_),
        total_runs(0),
        channel_distribution(Nch_,0),
        mkr(Nch_)
{
}

/**
 * Computes the current PU channel index. Tries to find a channel that is busy
 * and is not the current SU channel. If it fails to find a busy channel, it
 * checks the power of the current channel. If it is high, returns the current 
 * channel. Otherwise returns -1
 * 
 * If the SU is not transmitting we can set current_channel to -1 and, the channel with
 * highest power is gonna be picked as the one of the PU
 * @param current_channel
 * @param powers array with the received powers per channel, and clipped to zero if empty
 * @return PU channel
 */
int find_PU_channel(int current_channel, std::vector<float> powers)
{
    int pu_channel = -1;
    int pu_power = 0;
    
    // Find highest power to determine the PU channel
    // while ignoring the SU channel
    for(int i=0; i < powers.size(); i++) 
    {
        if(i != current_channel)
            if(powers[i] > pu_power)
            {
                 pu_channel=i;
                 pu_power = powers[i];
            }
    }
    
    // If PU is in the same channel as the SU
    if(pu_channel==-1 && powers[current_channel]>0)
        pu_channel = current_channel;
    
    return pu_channel;
}

/**
 * Update markov chain and channel distributions, considering the current channel of the PU
 * and the SU's current channel.
 * @param update_SU_channel
 * @param timestamp
 * @param powers array of powers per channel, where 0 means that the channel is empty
 * @param type
 */
void ChannelSelector::update_statistics(int pu_channel, double timestamp)
{
    // If we still do not know the PU channel (may not even be there)
    if(pu_channel < 0)
        return; // stay in the same channel
    
    total_runs++;
    channel_distribution[pu_channel] = channel_distribution[pu_channel] + 1;
    
    // First time
    if(previous_pu < 0)
        previous_pu = pu_channel;
    // Same channel
    else if(previous_pu == pu_channel)
        period++;
    // Transition
    else
    {
        // Ignore first transition cause it is not a complete measurement
        if(total_transitions < 0)
        {
            // set new channel & reset period
            previous_pu = pu_channel;
            period = 0;
            total_transitions = 0;
            last_transition_time = timestamp;
        }
        //Full transitions
        else
        {
            // Calculates how many dwell times have passed
            int no_of_transitions = 0;
            if(dwelltime())
                no_of_transitions = (int)ceil((timestamp-last_transition_time)/dwelltime());
            else
            {
                std::cout<<"Please set dwell time"<<std::endl;
                no_of_transitions = 1;
            }

            total_transitions=total_transitions + no_of_transitions;

            // If the PU stayed several dwell times in the same channel
            if(no_of_transitions >=1)
                for(int i=0; i<no_of_transitions-1;i++)
                    mkr.update_chain(previous_pu, previous_pu);
            
            mkr.update_chain(previous_pu, pu_channel);

            last_transition_time = timestamp;
            period=0;
            
            previous_pu=pu_channel;
        }
    }
}

/**
 * This function updates the Markov Chain based on received powers per channel
 * It works both when SU is not transmitting or it is and current_channel is specified
 * @param timestamp
 * @param powers
 */
int ChannelSelector::learning_update(double timestamp, const std::vector<float>& powers, int current_channel)
{
    // update markov chains and other statistics
    int pu_channel = find_PU_channel(current_channel, powers);
    update_statistics(pu_channel, timestamp);
    
    return pu_channel;
}

int ChannelSelector::select_next_channel(int current_channel, double timestamp, const std::vector<float>& powers)
{
    // update markov chains and other statistics
    int pu_channel = find_PU_channel(current_channel, powers);
    update_statistics(pu_channel, timestamp);
    
    // if they are in the same channel, pick a different one
    if(current_channel == pu_channel && (total_runs))
        return MarkovUtils::calculate_best_channel_two_hop(mkr, pu_channel);
    else
        return current_channel;
}

/*
 * 
int learning::statistical(int current_channel, int pu_channel) {
    float best_distribution = 1;
    int next_channel = current_channel;
    int best_channel = 0;
    
    // Check the distributions and find the best new channel to switch to, if the pu and su channels are the same. 
    if(current_channel == pu_channel && (total_runs))
    {       
        su_transitions_s++;
        for(int i=0; i<4; i++)
            if(i!=pu_channel-1 && (float)channel_distribution[i]/total_runs < best_distribution)
            {
                best_distribution = (float)channel_distribution[i]/total_runs;
                best_channel = i;
            }
        
        next_channel = best_channel+1;
    }
    return next_channel;
}
 * 
 * 


void learning::compare_algorithms(){
    std::cout<<"Total SU switches with algorithm 1: " << su_transitions_s << std::endl;
    std::cout<<"Total SU switches with algorithm 2: " << su_transitions_m << std::endl;
}
 * 
 */