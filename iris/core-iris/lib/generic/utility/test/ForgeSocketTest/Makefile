all:
	g++ -c -o ForgeUtilities.o ../../ForgeUtilities.cpp -g -std=c++0x
	#g++ -c -o test_anvil_rx.o test_anvil_rx.cpp -g
	#g++ -c -o test_anvil_tx.o test_anvil_tx.cpp -g
	#g++ -c -o test_anvil_prototx.o test_anvil_prototx.cpp -g
	g++ -c -o test_command_tx.o test_command_tx.cpp -g -std=c++0x
	g++ -c -o anvil_pkt.pb.o ../../../../../build/lib/generic/utility/anvil_pkt.pb.cc
	
	#g++ -o test_anvil_tx test_anvil_tx.o ForgeUtilities.o anvil_pkt.pb.o -lboost_system -lboost_filesystem -lboost_iostreams -lpthread -L/usr/local/lib -lprotobuf
	#g++ -o test_anvil_prototx ForgeUtilities.o anvil_pkt.pb.o test_anvil_prototx.o -lboost_system -lboost_filesystem -lboost_iostreams -lpthread -L/usr/local/lib -lprotobuf
	#g++ -o test_anvil_rx test_anvil_rx.o ForgeUtilities.o anvil_pkt.pb.o -lboost_system -lboost_filesystem -lboost_iostreams -lpthread -L/usr/local/lib -lprotobuf
	g++ -o test_command_tx test_command_tx.o ForgeUtilities.o anvil_pkt.pb.o -lboost_system -lboost_filesystem -lboost_iostreams -lpthread -L/usr/local/lib -lprotobuf
	protoc -I=../../ --python_out=./ ../../anvil_pkt.proto
