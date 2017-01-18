/* 
 * File:   MarkovChain.h
 * Author: Francisco Paisana
 *
 */

#ifndef MARKOVCHAIN_H
#define MARKOVCHAIN_H

#include <vector>

using std::vector;

class MarkovChain 
{
public:
    MarkovChain(int Nch_ = 4);
    void update_chain(int previous, int next);
    void set_markov_chain(const vector<vector<float> >& mat);
    //int next_channel(int, int);
    inline int num_channels() const { return Nch;};
    inline long num_transitions(int previous, int next) const {return transition_matrix[previous][next];};
    inline float transition_probability(int previous, int next) const { return (float)transition_matrix[previous][next]/total_transitions; };
    inline long num_total_transitions() const { return total_transitions;};
    
private:
    int Nch;                                            ///< Number of channels
    long total_transitions = 0;
    vector<vector<long> > transition_matrix;           ///< Matrix of transitions
};

namespace MarkovUtils
{
    std::vector<float> prior_probability(const MarkovChain& mrk);
    float prior_probability(const MarkovChain& mrk, int state);
    float conditional_probability(const MarkovChain& mrk, int previous, int next);
    
    void print_markov_matrix(const MarkovChain& mrk);
    vector<float> calculate_next_probabilities(const MarkovChain& mrk, int current_state);
    std::vector<int> calculate_best_channel_one_hop(const MarkovChain& mrk);
    std::vector<int> calculate_best_channel_two_hop(const MarkovChain& mrk);
    int calculate_best_channel_two_hop(const MarkovChain& mrk, int current_state, int forbidden_state = -1);
};

#endif /* MARKOVCHAIN_H */

