import time
import hashlib
import random
import rsa

class Transaction:
    def __init__(self, sender, receiver, amounts, fee, message):
        self.sender = sender
        self.receiver = receiver
        self.amounts = amounts
        self.fee = fee
        self.message = message

    def to_string(self):
        transaction_dict = {
            'sender': str(self.sender),
            'receiver': str(self.receiver),
            'amounts': self.amounts,
            'fee': self.fee,
            'message': self.message
        }
        return str(transaction_dict)


class Block:
    def __init__(self, previous_hash, difficulty, miner, miner_rewards):
        self.previous_hash = previous_hash
        self.hash = ''
        self.difficulty = difficulty
        self.nonce = 0
        self.timestamp = int(time.time())
        self.transactions = []
        self.miner = miner
        self.miner_rewards = miner_rewards

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
 
class BlockChain:
    def __init__(self, key):
        # Will adjust difficulty after specific blocks number
        self.adjust_difficulty_blocks = 10
        # The current difficulty of the chain
        self.difficulty = 1
        # How long can generate one block
        self.block_time = 30
        # How much rewards miners will get
        self.miner_rewards = 10
        # The max num. of transactions in one block
        self.block_limitation = 32
        # All the blocks in current chain
        self.chain = []
        # Waiting for putting into block
        self.pending_transactions = []
        # My own key
        self.key = key

    def create_genesis_block(self):
        print("God creates genesis block!")
        genesis_block = Block("First Block here!", self.difficulty, 'evshary', self.miner_rewards)
        genesis_block.hash = self.get_hash(genesis_block, 0)
        self.chain.append(genesis_block)

    def get_transactions_string(self, block):
        transactions_str = ""
        for transaction in block.transactions:
            transaction_dict = {
                'sender': str(transaction.sender),
                'receiver': str(transaction.receiver),
                'amounts': transaction.amounts,
                'fee': transaction.fee,
                'message': transaction.message
            }
            transactions_str += str(transaction_dict)
        return transactions_str

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
            self.adjust_difficulty()

    def add_transaction_to_block(self, block):
        # Higer priority for the higher fee
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
        if len(self.pending_transactions) > self.block_limitation:
            transaction_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transaction_accepted = self.pending_transactions
            self.pending_transactions = []
        block.transactions = transaction_accepted

    def mine_block(self, miner):
        last_block = self.chain[-1]
        new_block = Block(last_block.hash, self.difficulty, miner, self.miner_rewards)

        self.add_transaction_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.difficulty = self.difficulty
        new_block.nonce = random.getrandbits(32)
        new_block.hash = self.get_hash(new_block, new_block.nonce)

        while new_block.hash[0:self.difficulty] != "0" * self.difficulty:
            new_block.nonce += 1
            new_block.hash = self.get_hash(new_block, new_block.nonce)
            # TODO: While receiving others' verified result, go to next block
        
        # TODO: Broadcast your result to others
        print("I've mined the coin! hash number: %s in difficulty %s" % (new_block.hash, self.difficulty))
        self.chain.append(new_block)
 
    def adjust_difficulty(self):
        # Only adjust difficulty after the numbers of blocks "self.adjust_difficulty_blocks"
        if len(self.chain) < self.adjust_difficulty_blocks or len(self.chain) % self.adjust_difficulty_blocks != 1:
            return self.difficulty
 
        first_block_ts = self.chain[-1*self.adjust_difficulty_blocks-1].timestamp
        last_block_ts = self.chain[-1].timestamp
        average_time_consumed = round((last_block_ts - first_block_ts) / self.adjust_difficulty_blocks, 2)
        print(f"Average time: {average_time_consumed}s.")
        if average_time_consumed > self.block_time:
            print("Lower difficulty")
            self.difficulty -= 1
        else:
            print("Higher difficulty")
            self.difficulty += 1
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_balace(self, account):
        balance = 0
        for block in self.chain:
            miner = False
            if block.miner == account:
                miner = True
                balance += block.miner_rewards
            for transaction in block.transactions:
                if miner:
                    balance += transaction.fee
                if transaction.sender == account:
                    balance -= transaction.amounts
                    balance -= transaction.fee
                elif transaction.receiver == account:
                    balance += transaction.amounts
        return balance
 
    def add_transaction(self, transaction, signature):
        public_key = '-----BEGIN RSA PUBLIC KEY-----\n'
        public_key += transaction.sender
        public_key += '\n-----END RSA PUBLIC KEY-----\n'
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode('utf-8'))
        transaction_str = transaction.to_string()
        if transaction.fee + transaction.amounts > self.get_balance(transaction.sender):
            return False, "Balance not enough!"
        try:
            rsa.verify(transaction_str.encode('utf-8'), signature, public_key_pkcs)
            self.pending_transactions.append(transaction)
            return True, "Authorized successfully!"
        except Exception:
            return False, "RSA Verified wrong!"
    
    def receive_broadcast_block(self, block_data):
        last_block = self.chain[-1]
        if block_data.previous_hash != last_block.hash:
            print("Error received block: unmatched hash")
            return False
        elif block_data.hash[0: self.difficulty] == '0' * self.difficulty:
            print("Error received block: unmatched difficulty")
            return False
        elif block_data.hash != self.get_hash(block_data, block_data.nonce):
            print(block_data.hash)
            print("Error received block: wrong hash calculation")
            return False
        else:
            for transaction in block_data.transactions:
                    self.pending_transaction.remove(transaction)
            self.receive_verified_block = True
            self.chain.append(block_data)
            return True
