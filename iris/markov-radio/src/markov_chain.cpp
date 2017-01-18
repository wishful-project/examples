/* 
 * File:   marchov_chain.cpp
 * Author: jonathan
 * 
 * Created on 31 July 2015, 13:30
 */

#include "markov_chain.h"



markov_chain::markov_chain() {
    total_transitions = 0;
    for(int i=0; i<4; i++){
        decisions_lvl1[i] = 0;
        decisions_lvl2[i] = 0;
        for(int j=0; j<4;j++)
            transition[i][j]=0;
    }
}

void markov_chain::update_chain(int previous, int next){
    transition[previous][next]++;
    total_transitions++;
}

void markov_chain::print_transitions(){
    std::cout << "Marchov Transition Matrix: "<<std::endl<<"\tChannel 1\tChannel 2\tChannel 3\tChannel4 "<<std::endl;
    std::cout <<"____________________________________________________________________"<<std::endl;
    for(int i=0; i<4; i++){
        std::cout<< i+1 <<" | \t";
        for(int j=0; j<4;j++)
            std::cout << (float)transition[i][j]/total_transitions << "\t\t";
        std::cout<<std::endl;
    }
    std::cout << "Total transitions: " << total_transitions<<std::endl;
}

int markov_chain::next_channel(int current_pu, int lvl){
    //cout<<"Clash: PU is " << current_pu << ". SU to " << decisions_lvl1[current_pu-1]<<endl;
    if(lvl = 1)
       return decisions_lvl1[current_pu-1];
    if(lvl = 2)
        return decisions_lvl2[current_pu-1];
}

void markov_chain::calculate_decisions(){
    float lvl1_best = 1;
    float lvl2_best = 1;
    int lvl1_next = 0;
    int lvl2_next = 0;
    
    for(int i=0; i<4; i++){
        // calculate smallest probability for lvl1
        for(int j =0; j<4;j++)
            if(j!=i && ((float)transition[i][j]/total_transitions < lvl1_best)){
                 lvl1_best = (float)transition[i][j]/total_transitions;
                 lvl1_next = j;
            }
        decisions_lvl1[i]=lvl1_next+1;  
        //cout<<"If in " << i+1 << " go to " << decisions_lvl1[i]<<endl;
        lvl1_best = 1;
        lvl1_next = 0;
            
        //cout<< "starting lvl2" <<endl;
        //calculate smallest probability for lvl2
        for(int j =0; j<4;j++){
            float sum_j=0;
            for(int k=0; k<4; k++){
                float prob1 = (float)transition[i][k]/total_transitions;
                float prob2 = (float)transition[k][j]/total_transitions;
                sum_j = sum_j + prob1*prob2; 
                //cout<<"Sum j: " << prob1 <<" * " << prob2 <<endl;
                
            }
            //cout<< "______" <<endl;
            if(j!=i && sum_j<lvl2_best){
                lvl2_best = sum_j;
                lvl2_next = j;
            }
                
        }
        decisions_lvl2[i]=lvl2_next+1;  
        //cout<<"If in " << i+1 << " go to " << decisions_lvl2[i]<<endl;
        lvl2_best = 1;
        lvl2_next = 0;
        
    }
}

markov_chain::~markov_chain() {
}

