#!/usr/bin/python3

import sys
import blockchain
import server

if __name__ == '__main__':
    mykey = blockchain.Key()
    mykey.show_key()
    myblockchain = blockchain.BlockChain(mykey)
    myserver = server.Server(int(sys.argv[1]), myblockchain)
    myblockchain.create_genesis_block()
    myblockchain.do_minig()