#include "MarkovChain.h"
#include <cassert>
#include <algorithm>
#include <iostream>
#include <iomanip>

using std::cout;
using std::endl;

/**
 * MarkovChain constructor
 * @param Nch_ Number of Frequency Channels and possible frequency hops
 */
MarkovChain::MarkovChain(int Nch_) : 
        Nch(Nch_)
//        decisions_lvl1(Nch, 0),
//        decisions_lvl2(Nch, 0)
{
    // initialize markov matrix
    transition_matrix.resize(Nch);
    for(auto& el : transition_matrix)
        el.resize(Nch,0);
}

/**
 * Update the markov matrix during a learning phase
 * @param previous channel before PU transition
 * @param next channel after PU transition
 */
void MarkovChain::update_chain(int previous, int next)
{
    transition_matrix[previous][next]++;
    total_transitions++;
}

void MarkovChain::set_markov_chain(const vector<vector<float> >& mat)
{
    int Nch = mat.size();
    long precision = 1e9;
    
    long sum = 0;
    transition_matrix.resize(Nch);
    for(int i = 0; i < Nch; ++i)
    {
        transition_matrix[i].resize(Nch);
        for(int j = 0; j < Nch; ++j)
        {
            transition_matrix[i][j] = (long)round(precision * mat[i][j]);
        }
        sum += std::accumulate(transition_matrix[i].begin(), transition_matrix[i].end(), 0);
    }
    total_transitions = sum;
}

/**
 * based on the current channel, decide which one is the next
 * @param current_pu
 * @param lvl
 * @return 
 */
//int MarkovChain::next_channel(int current_pu, int lvl)
//{
//    //cout<<"Clash: PU is " << current_pu << ". SU to " << decisions_lvl1[current_pu-1]<<endl;
//    if(lvl = 1)
//       return decisions_lvl1[current_pu-1];
//    if(lvl = 2)
//        return decisions_lvl2[current_pu-1];
//}


namespace MarkovUtils
{
/**
 * Print current transition matrix
 */
void print_markov_matrix(const MarkovChain& mrk)
{
    std::cout << "Markov Transition Matrix: "<< std::endl;//<<"\tChannel 1\tChannel 2\tChannel 3\tChannel4 "<<std::endl;
    
    if(mrk.num_total_transitions() > 0)
    {
        cout << "______";
        for(int i = 0; i < mrk.num_channels(); ++i)
            cout << "________";
        cout << endl;

        for(int i=0; i<mrk.num_channels(); i++)
        {
            cout << i+1 << " |\t";
            for(int j=0; j < mrk.num_channels(); j++)
                cout << std::setprecision(4) << conditional_probability(mrk,i,j) << "\t";
            cout<< endl;
        }

        cout << "______";
        for(int i = 0; i < mrk.num_channels(); ++i)
            cout << "________";
        cout << endl;
    }
    
    std::cout << "Total transitions: " << mrk.num_total_transitions() <<std::endl;
}

float conditional_probability(const MarkovChain& mrk, int previous, int next)
{
    float prob = prior_probability(mrk, previous);
    
    return mrk.transition_probability(previous, next) / prob;
}

float prior_probability(const MarkovChain& mrk, int state)
{
    float prob;
    
    for(int j = 0; j < mrk.num_channels(); ++j)
        prob += mrk.transition_probability(state,j);
    
    return prob;
}

vector<float> prior_probability(const MarkovChain& mrk)
{
    std::vector<float> prob(mrk.num_channels(), 0);
    
    for(int i=0; i < mrk.num_channels(); ++i)
        prob[i] = prior_probability(mrk, i);
    
    return prob;
}

/**
 * Computes probability p(X_{k+1} | X{k}==current_state), for all Xs.
 * @param mrk
 * @param current_state
 * @return 
 */
vector<float> calculate_next_probabilities(const MarkovChain& mrk, int current_state)
{
    float prior_prob = prior_probability(mrk, current_state);
    int Nch = mrk.num_channels();
    std::vector<float> prob_values(Nch, 0);
    
    for(int j = 0; j < Nch; ++Nch)
        prob_values[j] = mrk.transition_probability(current_state, j) / prior_prob;
    
    assert(abs(std::accumulate(prob_values.begin(), prob_values.end(), 0.0)-1)<1e-5);
    
    return prob_values;
}

int calculate_best_channel_one_hop(const MarkovChain& mrk, int current_state)
{
    vector<float> next_state_probs = calculate_next_probabilities(mrk, current_state);
    // select minimum probability that is not equal to "i"

    float prob = 100000000;
    int sel_idx = -1;
    for(int j = 0; j < mrk.num_channels(); ++j)
        if(j != current_state && next_state_probs[j] < prob)
        {
            sel_idx = j;
            prob = next_state_probs[j];
        }

    //decisions_lvl1[i] = std::distance(next_state_probs.begin(), 
    //                             std::min_element(next_state_probs.begin(), next_state_probs.end()),
    //                                  [&i](float a, float b){ return a!=i && (b==i || a<b); });
    return sel_idx;// + 1;
}

/**
 * Calculates the "arg min_{X_{k+1}} { p(X_{k+1} | X_{k} }", i.e. the next state
 * with the lowest probability.
 */
std::vector<int> calculate_best_channel_one_hop(const MarkovChain& mrk)
{
    int Nch = mrk.num_channels();
    std::vector<int> decisions_lvl1(Nch, 0);
    
    for(int i=0; i<Nch; i++)
        decisions_lvl1[i] = calculate_best_channel_one_hop(mrk, i);
    
    return decisions_lvl1;
}

/**
 * Calculates the "arg min_{X_{k+2}} { p(X_{k+2} | X_{k} }", i.e. the next 2-hop state
 * with the lowest probability. We do a marginalization over X_{k+1}
 */
vector<int> calculate_best_channel_two_hop(const MarkovChain& mrk)
{
    int Nch = mrk.num_channels();
    vector<int> decisions_lvl2(Nch, 0);
    
    // Calculate smallest transition probability for 2 hops
    for(int i=0; i<Nch; i++)
        decisions_lvl2[i] = calculate_best_channel_two_hop(mrk, i);
    
    return decisions_lvl2;
}
/**
 * Calculates the state that has the lowest "p(X_{k+2}==j || X_{k+1}==j | X_{k} = current_state )",
 * i.e. the least likely state to be visited within two hops, knowing the 
 * current state. We do a marginalization over X_{k+1}
 */
int calculate_best_channel_two_hop(const MarkovChain& mrk, int current_state, int forbidden_state)
{
    int Nch = mrk.num_channels();
    
    vector<float> prob_visit(Nch,0);
    
    for(int i = 0; i < Nch; ++i)
    {
        // P(Xk+1!=i && Xk+2==i | Xk)
        for(int m = 0; m < Nch; ++m)
            prob_visit[i] += mrk.transition_probability(current_state, m) * mrk.transition_probability(m, i);

        // P(Xk+1==i && Xk+2!=i | Xk)        
        prob_visit[i] += mrk.transition_probability(current_state, i);
        //        for(int n = 0; n < Nch; ++n)
        //    prob_visit[i] += mrk.transition_probability(current_state, i) * mrk.transition_probability(i, n);
        
        // Subtract P(Xk+1==i && Xk+2==i | Xk), bc we counted it twice      
        prob_visit[i] -= mrk.transition_probability(current_state,i) * mrk.transition_probability(i,i);
    }
    
    float min_prob = 10000;
    int sel_idx = -1;
    for(int i = 0; i < Nch; ++i)
        if(min_prob > prob_visit[i] && i != forbidden_state)
        {
            min_prob = prob_visit[i];
            sel_idx = i;
        }
    
    return sel_idx;//+1;    
}
};