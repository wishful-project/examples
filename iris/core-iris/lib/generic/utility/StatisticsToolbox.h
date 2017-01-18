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


namespace iris
{

class SampleStatistics {
    double A;
    double Q;
    unsigned int k;

public:
    SampleStatistics() {A = 0; Q = 0; k = 0;}
    inline void addSample(double samp) {
        k++;
        double tmp = A;
        A += (samp - A) / k;
        Q += (samp - A) * (samp - tmp);
    }
    inline double variance() { // sample variance unbiased
        return Q / (k - 1);
    }
    inline double mean() {
        return A;
    }
    inline double std_deviation() { // sample std deviation (very little biased)
        return sqrt(variance());
    }
};

class RateStatistics {
    unsigned long int k;
    unsigned long int hits;

public:    
    RateStatistics() { k = 0; hits = 0;}
    inline void hit() {
        k++;
        hits++;
    }
    inline void miss() {
        k++;
    }
    inline float rate() {
        return ((float)hits)/k;
    }
    inline long int get_hits() { return hits; }
    inline long int get_tries() { return k; }
};

class ExpRateStatistics {
    float alpha;
    float rate_;

public:
    ExpRateStatistics(float _alpha = 0.005) { alpha = _alpha; rate_ = 0;}
    inline void hit() {
        rate_ = (1-alpha)*rate_ + alpha;
    }
    inline void miss() {
        rate_ = (1-alpha)*rate_;
    }
    inline float rate() {
        return rate_;
    }
};

class MovingAverageRateStatistics {
    short int *buffer;
    unsigned int size;
    unsigned int cur_idx;
    unsigned int n_filled;
    float rate_sum;

public:
    MovingAverageRateStatistics(int _size) {
        size = _size;
        buffer = new short int[size];
        reset();
    }
    inline bool push(short int val) {
        short int dropped = buffer[cur_idx];
        buffer[cur_idx++] = val;
        if(n_filled < size)
            n_filled++;
        if(cur_idx == size)
            cur_idx = 0;
        rate_sum += (val - dropped);
    }
    inline void hit() {
        push(1);
    }
    inline void miss() {
        push(0);
    }
    inline float rate() {
        return (n_filled > 0) ? rate_sum / n_filled : 0;
    }
    inline void reset() {
        for(unsigned int i = 0; i < size; i++)
            buffer[i] = 0;
        rate_sum = 0;
        cur_idx = 0;
        n_filled = 0;
    }
};

} // end of iris namespace


