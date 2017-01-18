/* 
 * File:   marchov_chain.h
 * Author: jonathan
 *
 * Created on 31 July 2015, 13:30
 */
#include <vector>
#include <iostream>

#ifndef MARKOV_CHAIN_H
#define	MARKOV_CHAIN_H

class markov_chain {
public:
    markov_chain();
    void update_chain(int, int);
    void print_transitions();
    int next_channel(int, int);
    ~markov_chain();
    void calculate_decisions();
    
private:
    int total_transitions;
    int transition[4][4];
    float decisions_lvl1[4];
    float decisions_lvl2[4];
};

#endif	/* MARCHOV_CHAIN_H */

