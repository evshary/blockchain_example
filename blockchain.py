#!/usr/bin/python3

import time
import rsa

class Transaction:
    def __init__(self, sender, receiver, amounts, fee, message):
        self.sender = sender
        self.receiver = receiver
        self.amounts = amounts
        self.fee = fee
        self.message = message

class Block:
    def __init__(self, previous_hash, difficulty, miner, miner_rewards):
        self.previous_hash = previous_hash
        self.hash = ''
        self.difficulty = difficulty
        self.nounce = 0
        self.timestamp = int(time.time())
        self.transactions = []
        self.miner = miner
        self.miner_rewards = miner_rewards

class BlockChain:
    def __init__(self, key):
        # Will adjust difficulty after specific blocks number
        self.adjust_difficulty_blocks = 10
        # The current difficulty of the chain
        self.difficulty = 1
        # How long can generate one block
        self.block_time = 30
        # How much rewards miners will get
        self.mining_rewards = 10
        # The max num. of transactions in one block
        self.block_limitation = 32
        # All the blocks in current chain
        self.chain = []
        # Waiting for putting into block
        self.pending_tansactions = []
        # My own key
        self.key = key

    def create_genesis_block(self):
        print("God creates genesis block!")
        genesis_block = Block("First Block here!", self.difficulty, 'evshary', self.miner_rewards)
        genesis_block.hash = self.get_hash(genesis_bock, 0)
        self.chain.append(genesis_block)

    def get_transactions_string(self, block):
        transactions_str = ""
        for transaction in block.tanactions:
            transaction_dict = {
                'sender': str(transaction.sender),
                'receiver': str(transaction.receiver),
                'amounts': transaction.amounts,
                'fee': transaction.fee,
                'message': transaction.message
            }
            transactions_str += str(transaction_dict)
        return transaction_str

    def get_hash(self, block, nonce):
        s = hashlib.sha1()
        s.update(
            (
                block.previous_hash +
                str(block.timestamp) +
                self.get_transactions_string(block) +
                str(nonce)
            ).encode("utf-8")
        )
        h = s.hexdigest()
        return h

    def do_minig(self):
        while True:
            self.mine_block(self.key.get_publickey())

    def mine_block(self, miner):
        print("Minig....")
        time.sleep(1)

class Key:
    def __init__(self):
        public, private = rsa.newkeys(512)
        self.public_key = self.extract_keystring(public.save_pkcs1())
        self.private_key = self.extract_keystring(private.save_pkcs1())

    def extract_keystring(self, key):
        keystring = str(key).replace('\\n','')
        # If the key is public key
        keystring = keystring.replace("b'-----BEGIN RSA PUBLIC KEY-----", '')
        keystring = keystring.replace("-----END RSA PUBLIC KEY-----'", '')
        # If the key is private key
        keystring = keystring.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
        keystring = keystring.replace("-----END RSA PRIVATE KEY-----'", '')
        keystring = keystring.replace(' ', '')
        return keystring
        
    def get_publickey(self):
        return self.public_key

    def get_privatekey(self):
        return self.private_key

    def show_key(self):
        print("Public key: %s" % self.public_key)
        print("Private key: %s" % self.private_key)

if __name__ == '__main__':
    mykey = Key()
    mykey.show_key()
    blockchain = BlockChain(mykey)
    blockchain.do_minig()

