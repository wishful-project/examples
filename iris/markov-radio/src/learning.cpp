/* 
 * File:   learning.cpp
 * Author: jonathan
 * 
 * Created on 31 July 2015, 12:46
 */

#include "learning.h"
#include <iostream>


learning::learning() {

    total_runs = 0;
    total_transitions = -1;
    channel_distribution [0] = 0;
    channel_distribution [1] = 0;
    channel_distribution [2] = 0;
    channel_distribution [3] = 0;
    previous_pu = 0; 
    //average_min_period = 0;
    period = 0;
    dwelltime=0;
    last_transition_time=0;
    su_transitions_s = 0;
    su_transitions_m = 0;
    //threshold = 0.1;
    //count =0;
    //min_period = 1000;
    }

learning::learning(double dwell_time) {

    total_runs = 0;
    total_transitions = -1;
    channel_distribution [0] = 0;
    channel_distribution [1] = 0;
    channel_distribution [2] = 0;
    channel_distribution [3] = 0;
    previous_pu = 0; 
    //average_min_period = 0;
    period = 0;
    dwelltime=dwell_time;
    last_transition_time=0;
    su_transitions_s = 0;
    su_transitions_m = 0;
    //threshold = 0.1;
    //count =0;
    //min_period = 1000;
    }

// return the channel to switch to

void learning::pass_dwell_time(double dwell_time){
    dwelltime= dwell_time;
}

int learning::process(int update_channel, double timestamp, std::vector<float> powers, char type){
    int current_channel = update_channel; 
    int pu_channel=0; 
    int best_channel=0;
    float pu_power = 0; 
    
    //cout<<"timestamp: " << timestamp <<endl;
   // Find highest power to determine the PU channel
   // while ignoring the SU channel
    for(int i=0; i < powers.size(); i++) {
        if(i != current_channel-1)
            if(powers[i] > pu_power){
                 pu_channel=i+1;
                 pu_power = powers[i];
            } 
    }
    
    
    
    if(pu_channel==0 && powers[current_channel-1]>0)
        pu_channel = current_channel;
               
    if(pu_channel){
        total_runs++;   
        channel_distribution[(unsigned int)(pu_channel-1)] = channel_distribution[(unsigned int)(pu_channel-1)]+1;
    }
    
    //Find the PU transitions for the Marchov chain
    if(pu_channel){
        // First time
        if(!previous_pu){
            previous_pu=pu_channel;     
        }
        // Same channel
        else if(previous_pu==pu_channel)
            period++;
        // Transition
        else{
            // Ignore first transition cause it is not a complete measurement
            if(total_transitions ==-1){
                // set new channel & reset period
                previous_pu=pu_channel;
                //cout<<"Ignore " <<endl;
                period=0;
                total_transitions = 0;
                last_transition_time = timestamp;
            }
            /*
            // Estimate the minimum period
            else if(count <10){
                count++;
                previous_pu=pu_channel;
                if(period<min_period)
                     min_period = period+1;
                period=0;
            }
            */
            //Full transitions
            else{
                int no_of_transitions = 0;
                if(dwelltime)
                    no_of_transitions = (int)(timestamp-last_transition_time)/dwelltime;
                else
                    std::cout<<"Please set dwell time"<<std::endl;
                
                //cout<<"no_of_transitions: " << no_of_transitions <<endl;
                
                total_transitions=total_transitions + no_of_transitions;
                m.update_chain(previous_pu-1, pu_channel-1);  
                
                if(no_of_transitions >=1)
                    for(int i=0; i<no_of_transitions-1;i++)
                        m.update_chain(pu_channel-1, pu_channel-1);
                
                previous_pu=pu_channel;
                last_transition_time = timestamp;
                period=0;
                
            /*
            if(average_min_period ==0){
                average_min_period = period+1;
            }                
            else {
                int no_of_transitions = (int)((period+1)/average_min_period);
                average_min_period = (float)(average_min_period*total_transitions + (float)(period+1)/no_of_transitions)/(total_transitions + no_of_transitions);
                total_transitions = total_transitions + no_of_transitions; 
            }   
            period=0;
             */
            }
        }
    }
    
    //cout<<"average period: " << average_min_period <<endl;
    //cout<<"min_period: " <<min_period <<endl;
    //cout<<"transitions: " <<total_transitions <<endl;
    
    
    if(type == 's'){
        markov(current_channel, pu_channel);
        return statistical(current_channel, pu_channel);
    }
    else if(type =='m'){
        if(total_transitions > 0)
            statistical(current_channel, pu_channel);
            return markov(current_channel, pu_channel);
    }
    else
        return current_channel;
}

int learning::markov(int current_channel, int pu_channel){
    int next_channel = current_channel;
    
    if(current_channel == pu_channel && (total_runs)){
        su_transitions_m++;
        //m.print_transitions();
        m.calculate_decisions();
        next_channel = m.next_channel(pu_channel, 2);
    }
    
    return next_channel;
}

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

void learning::compare_algorithms(){
    std::cout<<"Total SU switches with algorithm 1: " << su_transitions_s << std::endl;
    std::cout<<"Total SU switches with algorithm 2: " << su_transitions_m << std::endl;
}

void learning::print_distribution() {
    std::cout << "Distribution is: "<<std::endl<<"Channel 1\tChannel 2\tChannel 3\tChannel4 " <<std::endl;
            for(int i=0; i<4; i++)
                std::cout<< (float)channel_distribution[i]/total_runs << "\t\t";
    std::cout<<std::endl;
}

void learning::print_marchov(){
    m.calculate_decisions();
    m.print_transitions();
}

learning::~learning() {
}

