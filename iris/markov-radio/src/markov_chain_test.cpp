/* 
 * File:   markov_chain_test.cpp
 * Author: xico
 *
 * Created on 03 December 2016, 19:21
 */

#include <stdlib.h>
#include <iostream>
#include <chrono>
#include <random>
#include <vector>

#include "ChannelSelector.h"

void test_markov_matrix_generation()
{
    std::cout << "markov_chain test 1" << std::endl;
    
    int Nch = 8;
    
    // Initialize random generator
    unsigned seed1 = std::chrono::system_clock::now().time_since_epoch().count();
    std::mt19937 g (seed1);
    //std::default_random_engine generator;
    std::uniform_int_distribution<int> randi(0,Nch-1);
    
    // Initialize Markov and set first state
    MarkovChain mrk(Nch);
    int current_state = randi(g);
    vector<int> jump_choice1(Nch), jump_choice2(Nch);
    std::iota(jump_choice1.begin(), jump_choice1.end(), 0);
    for(auto & j : jump_choice2)
        j = randi(g);
    
    for(int i = 0; i < 10000; ++i)
    {
        int new_state = (randi(g) > Nch/2) ? jump_choice1[current_state] : jump_choice2[current_state];
        mrk.update_chain(current_state,new_state);
        current_state = new_state;
    }
    
    MarkovUtils::print_markov_matrix(mrk);
}

void test2()
{
    std::cout << "\nmarkov_chain_test test 2\n";
    
    int Nch = 4;
    
    // Initialize random generator
    unsigned seed1 = std::chrono::system_clock::now().time_since_epoch().count();
    std::mt19937 g (seed1);
    //std::default_random_engine generator;
    std::uniform_int_distribution<int> randi(0,Nch-1);
    
    // Initialize markov matrix
    vector<vector<float>> mat = {{0.1,0.3,0.4,0.2},{0.3,0.0,0.4,0.3},{0.2,0.0,0.0,0.8},{0.3,0.5,0.2,0.0}};
    
    // Create objects
    ChannelSelector selector(Nch);
    selector.markov_matrix().set_markov_chain(mat);
    
    MarkovUtils::print_markov_matrix(selector.markov_matrix());
    
    std::cout << "%TEST_FAILED% time=0 testname=test2 (markov_chain_test) message=error message sample" << std::endl;
}

int main(int argc, char** argv)
{
    std::cout << "%SUITE_STARTING% markov_chain_test" << std::endl;
    std::cout << "%SUITE_STARTED%" << std::endl;

    std::cout << "%TEST_STARTED% test1 (markov_chain_test)" << std::endl;
    test_markov_matrix_generation();
    std::cout << "%TEST_FINISHED% time=0 test1 (markov_chain_test)" << std::endl;

//    std::cout << "%TEST_STARTED% test2 (markov_chain_test)\n" << std::endl;
    test2();
//    std::cout << "%TEST_FINISHED% time=0 test2 (markov_chain_test)" << std::endl;

    std::cout << "%SUITE_FINISHED% time=0" << std::endl;

    return (EXIT_SUCCESS);
}

