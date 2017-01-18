#ifndef SERIALIZATIONUTILITIES_H
#define	SERIALIZATIONUTILITIES_H

#include <boost/any.hpp>
#include <cstring>
#include <string>
#include <sstream>
#include <vector>
#include <list>
#include <boost/cstdint.hpp>
#include <netinet/in.h>
#include <iostream>

using namespace std;

typedef std::vector<uint8_t> ByteVec;

/**
 * Converts a vector of type T to a vector of bytes
 */
template<typename T>
inline std::vector<uint8_t> convert_to_bytes(const std::vector<T> &vec) {
    std::vector<uint8_t> byte_vec(vec.size() * sizeof(T));
    std::memcpy((void*)&byte_vec[0], (void*)&vec[0], vec.size() * sizeof(T));
    
    return byte_vec; // copy elision
}

/**
 * Converts a variable of type T to a vector of bytes
 */
// TODO: Test if a vector will never be sent to this
template<typename T>
inline std::vector<uint8_t> convert_to_bytes(const T &var) {
    std::vector<uint8_t> byte_vec(sizeof(T));
    std::memcpy((void*)&byte_vec[0], (void*)&var, sizeof(T));
    
    return byte_vec; // copy elision
}

inline std::vector<uint8_t> convert_to_bytes(const std::string &str) {
    std::vector<uint8_t> byte_vec(str.size());
    std::memcpy((void*)&byte_vec[0], (void*)&str[0], str.size());
    
    return byte_vec; // copy elision
}

inline std::vector<uint8_t> convert_to_bytes(const std::vector<boost::any> &vec) {
    std::vector<uint8_t> byte_vec(vec.size());
    //try {
    for (int i = 0; i < vec.size(); ++i) {
        byte_vec[i] = boost::any_cast<uint8_t>(vec[i]);
    }
    return byte_vec; // copy elision
}

/**
 * Appends a variable to a pre-existing vector
 */
template<typename T>
inline void append_bytes(std::vector<uint8_t> &out_vec, const vector<T>& vec) {
    const uint8_t* begin = reinterpret_cast<const uint8_t*> (&vec[0]); //0
    out_vec.insert(out_vec.end(), begin, begin + vec.size() * sizeof(T));
}

/**
 * Appends a variable to a pre-existing vector
 */
template<typename T>
inline void append_bytes(std::vector<uint8_t> &out_vec, const T& value) {
    const uint8_t * begin = reinterpret_cast<const uint8_t*> (&value); //0
    out_vec.insert(out_vec.end(), begin, begin + (sizeof(T) / sizeof(uint8_t)));
}

template<typename T>
inline void append_bytes(std::vector<uint8_t> &out_vec, const std::string& str) {
    const uint8_t * begin = reinterpret_cast<const uint8_t*> (str.data()); //0
    out_vec.insert(out_vec.end(), begin, begin + str.length());
}

/**
 * Class used to read an array of bytes
 */
class ByteArrayReader {
public:
    ByteArrayReader(const std::vector<uint8_t> &in_vec) : idx_ptr(0), begin_ptr(&in_vec[0]) {}
    template<typename T>
    void read_data(T &var, size_t siz) {
        memcpy(&var, &begin_ptr[idx_ptr], siz);
        idx_ptr += sizeof(T);
    }
    void read_data(std::string &str, size_t siz) {
        str.resize(siz);
        std::copy(&begin_ptr[idx_ptr], &begin_ptr[idx_ptr + siz], str.begin());
        idx_ptr += siz;
    }
    void read_data(ByteVec &vec, size_t siz) {
        vec.resize(siz);
        std::copy(&begin_ptr[idx_ptr], &begin_ptr[idx_ptr + siz], vec.begin());
        idx_ptr += siz;
    }
    inline void set_ptr(int val = 0) {
        idx_ptr = val;
    }
    inline void advance_ptr(int val) {
        idx_ptr += val;
    }
private:
    int idx_ptr;
    const uint8_t *begin_ptr;
};

inline std::string convert_to_string(const std::vector<boost::any> &vec) {
    std::string str;
    str.resize(vec.size());
    for(int i = 0; i < vec.size(); ++i) {
        str[i] = (char)boost::any_cast<uint8_t>(vec[i]);
    }
    return str; // copy elision
}

template<typename T>
inline std::string convert_to_string(const T &var) {
    std::stringstream ss;
    ss << var;
    return ss.str(); // Q: copy elision?
}

template<typename T>
inline std::string convert_to_string(const std::vector<T> &vec) {
    std::stringstream ss;
    for(int i = 0; i < vec.size(); i++) {
        ss << vec[i];
    }
    return ss.str(); // Q: copy elision?
}

/**
 * Separates a string into small strings/tokens, based on the characters provided in "delimiters"
 * @param main_string original string
 * @param delimiters characters used to delimit each token
 * @return list of tokens
 */
inline std::list<std::string> string_delimiter(std::string main_string, std::string delimiters)
{
    std::list<std::string> string_list;
    
    char *char_ptr = strtok(&main_string[0], &delimiters[0]);
    while(char_ptr != NULL)
    {
        string_list.push_back(std::string(char_ptr));
        char_ptr = strtok(NULL, &delimiters[0]);
    }
    
    return string_list; // copy elision
}


/* Serializer Helpers */

/*template <typename T> std::string serialize_num(T& num) {

    union {
        T a;
        char bytes[sizeof (num)];
    } chunk_mem;
    chunk_mem.a = num;
    string bytes;
    bytes.assign(chunk_mem.bytes, sizeof (num));
    return bytes;
}*/

/*template <typename T> void serialize_num(std::string &bytes, T& num) {

    union {
        T a;
        char bytes[sizeof (num)];
    } chunk_mem;
    chunk_mem.a = num;
    bytes.assign(chunk_mem.bytes, sizeof (num));
}*/

/*template <typename T> void numToString(std::string &bytes, T& num, bool little_endian = false) {
    bytes.assign(sizeof (num), '\0');
    if (little_endian)
        for (int n = bytes.size() - 1; n >= 0; n--)
            bytes[n] = (num << (8 * n)) & 0x000000ff;
    else
        for (unsigned int n = 0; n < bytes.size(); n++) {
            bytes[n] = (num << (8 * n)) & 0x000000ff;
        }
}*/

/*template <typename IntegerType> IntegerType bytesToInt(IntegerType& result, char *bytes, bool little_endian = false) {
    result = 0;
    if (!little_endian)
        for (int n = sizeof ( result) - 1; n >= 0; n--) {
            result = (result << 8) + bytes[ n ];
        } else
        for (unsigned n = 0; n < sizeof ( result); n++) {
            result = (result << 8) + bytes[ n ];
        }
    return result;
}*/

inline ByteVec serialize_with_prefix(const ByteVec &data)
{
    ByteVec out_vec;
    out_vec.reserve(data.size() + sizeof(uint32_t));
    append_bytes(out_vec, (uint32_t)data.size());
    append_bytes(out_vec, data);
    return out_vec;
}

inline void serialize_with_prefix(ByteVec &out_vec, const ByteVec &data)
{
    append_bytes(out_vec, (uint32_t)data.size());
    append_bytes(out_vec, data);
}

class TaggedValue
{
public:
    std::string tag;
    ByteVec value;
    
    TaggedValue(const std::string &_tag, const ByteVec &_value) : tag(_tag), value(_value)
    {
    }
    TaggedValue(const ByteVec &data)
    {
        ByteArrayReader array_reader(data);
        uint32_t size_data;
        array_reader.read_data(size_data, sizeof(size_data));
        array_reader.read_data(tag, size_data);
        array_reader.read_data(size_data, sizeof(size_data));
        array_reader.read_data(value, size_data);
    }
    ByteVec serialize()
    {
        ByteVec out_vec;
        out_vec.reserve(tag.length() + value.size() + 2*sizeof(uint32_t));
        serialize_with_prefix(out_vec, convert_to_bytes(tag));
        serialize_with_prefix(out_vec, convert_to_bytes(value));
        return out_vec;
    }
    template<typename T> T get_value()
    {
        ByteArrayReader array_reader(value);
        T val;
        array_reader.read_data(val, sizeof(val));
        return val;
    }
};

#endif	/* SERIALIZATIONUTILITIES_H */

