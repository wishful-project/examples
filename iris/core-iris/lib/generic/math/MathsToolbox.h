#ifndef MATHSTOOLBOX_H
#define	MATHSTOOLBOX_H

#include <vector>
#include <numeric>
#include <cassert>
#include <cstdint>
#include <cmath>
#include <string>
#include <iostream>
#include <sstream>
#include <limits>

class RunningStat
{
public:
    RunningStat()
    {
        clear();
    }
    inline void clear()
    {
        m_n = 0;
        m_M = 0.0;
        m_S = 0.0;
    }
    inline void push(double x)
    {
        m_n++;

        double m_newM = m_M + (x - m_M) / m_n;
        m_S += (x - m_M)*(x - m_newM);
        // if m_n == 1, x-m_newM==0 and m_S == 0, so the new m_S will still be zero
        
        // set up for next iteration
        m_M = m_newM;
    }

    inline int num() const
    {
        return m_n;
    }

    inline double mean() const
    {
        return m_M;
    }

    inline double var() const
    {
        return ( (m_n > 1) ? m_S / (m_n - 1) : 0.0);
    }

    inline double std_dev() const
    {
        return sqrt(var());
    }

private:
    int m_n;
    double m_M, m_S;
};

struct Averager 
{
    double val_sum;
    uint64_t val_count;
    Averager() {
        reset();
    }
    inline void push(double val) {
        val_sum += val;
        ++val_count;
    }
    inline float mean() const {
        return val_sum / val_count;
    }
    inline uint64_t num() const
    {
        return val_count;
    }
    inline void reset() 
    {
        val_sum = 0;
        val_count = 0;
    }
};

class ExpAverager
{
    double exp_mean;
    double alpha;
    int n_samples;
    int count_max;
public:
    ExpAverager(double _alpha = 0.01, int _count = 100) : alpha(_alpha), exp_mean(0), n_samples(0), count_max(_count)
    {
    }
    inline void push(double val)
    {
        ++n_samples;
        if(n_samples > count_max)
            exp_mean = (1-alpha) * exp_mean + alpha * val;
        else if(n_samples <= count_max)
        {
            exp_mean += val;
            if(n_samples == count_max)
                exp_mean = exp_mean / n_samples;
        }
    }
    inline float mean() const {
        return exp_mean;
    }
    inline uint64_t num() const
    {
        return n_samples;
    }
    inline void reset() 
    {
        n_samples = 0;
        exp_mean = 0;
    }
};

struct RateCalculator {
    uint64_t val_sum;
    uint64_t val_count;
    RateCalculator() {
        reset();
    }
    inline void reset() {
        val_sum = 0;
        val_count = 0;
    }
    inline void hit() {
        ++val_sum;
        ++val_count;
    }
    inline void hit(uint64_t times) {
        val_sum += times;
        val_count += times;
    }
    inline void miss(uint64_t times) {
        val_count += times;
    }
    inline float get_rate() {
        return ((double)val_sum) / val_count;
    }
};

template <typename T>
class CircularBuffer {
    std::vector<T> buf;
    uint32_t idx;

public:
    CircularBuffer() : idx(0) {}
    CircularBuffer(uint32_t size) {resize(size);}
    inline void resize(uint32_t size, T val = 0) 
    {
        buf.resize(size, val); 
        idx = 0;
    }
    inline uint32_t size() {return buf.size();}
    inline T push(const T &val) {
        T lost_val = buf[idx];
        buf[idx++] = val;
        if(idx >= size()) idx = 0;
        return lost_val;    // NRVO
    }
    inline T& operator[](const uint32_t f_idx) {    // f_idx = 0 is the last added sample
        return buf[(idx <= f_idx) ? (buf.size() + idx) - f_idx - 1 : idx - f_idx - 1]; //be careful with the unsignedness
    }
    inline T& at(const uint32_t f_idx) {    // f_idx = 0 is the last added sample
        assert(f_idx < buf.size());
        return buf[(idx <= f_idx) ? (buf.size() + idx) - f_idx - 1 : idx - f_idx - 1]; //be careful with the unsignedness
    }
    inline T sum() {
        return std::accumulate(buf.begin(), buf.end(), 0.0);
    }
};

template <typename T>
class MovingAverage {
    CircularBuffer<T> cbuf;
    T pwr_sum;
    uint16_t counts;

public:
    MovingAverage() : counts(0), pwr_sum(0) {}
    MovingAverage(uint32_t size) { resize(size);}
    inline void resize(uint32_t size) {cbuf.resize(size); pwr_sum = 0; counts = 0;}
    inline uint32_t size() {return cbuf.size();}
    inline void push(const T &val) {
        if(counts++ > size()) {
            cbuf.push(val);
            pwr_sum = 0;
            //for(uint16_t i = 0; i < cbuf.size(); ++i)
            //    pwr_sum += cbuf[i];
            pwr_sum = cbuf.sum();   // refresh
            counts = 0;
        }
        else {
            pwr_sum += val - cbuf.push(val);
        }
    }
    inline T out() { return pwr_sum / (float)size(); }
};

template <typename T>
class MovingMaximum
{
    CircularBuffer<T> cbuf;
    T* max_val;

public:
    MovingMaximum() {}
    MovingMaximum(uint32_t size) { resize(size);}
    inline void resize(uint32_t size) 
    {
        cbuf.resize(size, -std::numeric_limits<T>::max());
        max_val = &cbuf[0];
    }
    inline uint32_t size() {return cbuf.size();}
    inline void push(const T &val) 
    {
        cbuf.push(val);
        if(*max_val <= cbuf[0])  // cbuf[0] is the last added value (val)
            max_val = &cbuf[0];
    }
    inline T max() { return *max_val; }
};

template<typename Iterator> std::string print(Iterator it_begin, Iterator it_end) {
    std::ostringstream os;
    Iterator it = it_begin;
    os << "[";
    if(it_begin != it_end) {
        os << *it_begin;
        for(++it; it != it_end; it++)
            os << ", " << *it;
    }
    os << "]";
    return os.str(); // URVO?
}

template<typename T> std::string print(const std::vector<T> &vec) {
    std::ostringstream os;
    os << "[";
    for(int i = 0; i < vec.size()-1; i++)
        os << vec[i] << ", ";
    if(vec.size() > 0) os << vec[vec.size()-1];
    os << "]";
    return os.str();
}

#endif	/* MATHSTOOLBOX_H */

