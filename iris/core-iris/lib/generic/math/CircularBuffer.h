/* 
 * File:   CircularBuffer.h
 * Author: nodeuser
 *
 * Created on 20 June 2015, 20:22
 */
#include <vector>

#ifndef CIRCULARBUFFER_H
#define	CIRCULARBUFFER_H

template <typename T>
class CircularBuffer {
    unsigned int cur_pos;
    T sum_value;
public:
    std::vector<T> buffer;  // Had to put it as public bc of stupid core that can't receive const vectors...
    CircularBuffer() {
        sum_value = 0;
        cur_pos = 0;
    }
    CircularBuffer(int _size, T fill = 0) {
        assign(_size, fill);
    }
    void assign(int _size, T fill = 0) {
        buffer.assign(_size, fill);
        cur_pos = 0;
        sum_value = 0;
        for(register int i = 0; i < buffer.size(); i++)
            sum_value += buffer[i];
    }
    inline void push(T samp) {
        sum_value += samp - buffer[cur_pos];
        buffer[cur_pos] = samp;
        cur_pos = (cur_pos == (buffer.size() - 1)) ? 0 : cur_pos + 1;
    }
    inline T get_sum() {
        return sum_value;
    }
    inline T get_val(unsigned int idx) {
        return buffer[idx];
    }
    inline unsigned int size() {
        return buffer.size();
    }
};

#endif	/* CIRCULARBUFFER_H */

