/* 
 * File:   ProtobufSerializationUtilities.h
 * Author: Francisco
 *
 * Created on September 3, 2015, 1:59 PM
 */

#ifndef PROTOBUFSERIALIZATIONUTILITIES_H
#define	PROTOBUFSERIALIZATIONUTILITIES_H

#include "SerializationUtilities.h"
#include "irisapi/StackComponent.h"
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl_lite.h>

/**
 * Converts a protobuf struct to an array of bytes
 * @param message
 * @return 
 */
template<typename T> std::vector<uint8_t> protobuf_to_array(const T &message) {
    vector<uint8_t> byte_vec(message.ByteSize());
    message.SerializeToArray(&byte_vec[0], message.ByteSize());
    return byte_vec;
}

/**
 * Read from an iris command
 */
template<typename T> void get_command(T &message, const iris::Command &com) {
    uint8_t byte_array[com.data.size()];

    for(uint32_t i = 0; i < com.data.size(); i++)
        byte_array[i] = boost::any_cast<uint8_t>(com.data[i]);

    message.ParseFromArray(byte_array, com.data.size());
}

/**
 * Converts a Protobuf object to an array of bytes and adds a prefix with the size of the object
 */
template<typename T> void serialize_with_prefix(vector<google::protobuf::uint8> &buffer, const T &proto_message) {//const google::protobuf::Message &proto_message) {
    google::protobuf::uint32 message_length = proto_message.ByteSize();
    int buffer_length = sizeof (message_length) + message_length;
    buffer.resize(buffer_length);

    google::protobuf::io::ArrayOutputStream array_output(&buffer[0], buffer_length);
    google::protobuf::io::CodedOutputStream coded_output(&array_output);
    coded_output.WriteLittleEndian32(message_length);
    //coded_output.WriteVarint32(message_length); //WriteLittleEndian32
    proto_message.SerializeToCodedStream(&coded_output);
}

#endif	/* PROTOBUFSERIALIZATIONUTILITIES_H */

