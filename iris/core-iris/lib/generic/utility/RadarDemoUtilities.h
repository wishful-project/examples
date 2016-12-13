#ifndef RADARDEMOUTILITIES_H
#define	RADARDEMOUTILITIES_H

/**
 * For a sequence of tstamps with one of tstamps equal to tstamp1, 
 * and period equal to period1, finds the closest tstamp to tstamp2
 * @param tstamp1   one of the tstamps of the sequence 1
 * @param period1   period of the sequence 1
 * @param tstamp2   the tstamp for comparison
 * @return          a pair with the closest tstamp of sequence 1 and how many periods
 */
template<typename T>
inline std::pair<T, int> closest_tstamp(T tstamp1, T period1, T tstamp2)
{
    T tstamp_diff = tstamp2 - tstamp1;
    int k = round(tstamp_diff / period1);
    return std::pair<T, int>(period1 * k + tstamp1, k);
}

inline double pri_diff_harmonic(double PRI, double PRI2)
{
    return (PRI < PRI2) ? abs(PRI2 - PRI*(round(PRI2/PRI))) : abs(PRI - PRI2*(round(PRI / PRI2)));
}

inline double pri_rel_diff_harmonic(double PRI, double PRI2) {
    return (PRI < PRI2) ? abs(PRI2 / round(PRI2 / PRI) - PRI) / PRI : abs(PRI / round(PRI / PRI2) - PRI2) / PRI2;
}

template<class ValueType, class ValueType2>
typename std::map<ValueType, ValueType2>::const_iterator closest_tstamp_it(const std::map<ValueType, ValueType2> &cont, const ValueType& val)
{
    auto result = cont.upper_bound(val);
    
    if(result != cont.begin())
    {
        auto lower_result = result;
        --lower_result;
        if(result == cont.end() || (val - lower_result->first) < (result->first - val))
            result = lower_result;
    }
    
    return result;
}

#endif	/* RADARDEMOUTILITIES_H */

