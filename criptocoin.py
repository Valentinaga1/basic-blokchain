import datetime
import hashlib
import json
import requests
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse
from flask_ngrok import run_with_ngrok

class Blockchain:
    def __init__(self):
        """ Constructor de la clase. """
        self.chain = []
        # Las transacciones se agregarán a la blockchain en cuanto los mineros creen los bloques
        self.transactions = []  # mempool
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        """ Creación de un nuevo bloque.

        Arguments:
          - proof: Nounce of the current block.
          - previous_hash: Hash of the previous block.

        Returns:
          - block: New Block created.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []  # Clean the transactions list to add new transactions to this new block
        self.chain.append(block)
        return block

    def get_previous_block(self):
        """Get the previous block in the blockchain.

        Returns:
          - Get the previous block in the blockchain
        """
        return self.chain[-1]  # Getting the last block in the list

    def proof_of_work(self, previous_proof):
        """ Concensus protocol (PoW):

        Arguments:
          - previous_proof: Previous block nonce. ( it is really the nonce)

        Returns:
          - new_proof: New hash obtained with PoW
        """
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        """ Calculate the hash of a block

        Arguments:
          - block: a block in a blockchain

        Returns:
          - hash_block: returns the hash of a block
        """
        encoded_block = json.dumps(
            block, sort_keys=True).encode()  # Create a JSON format of that block
        hash_block = hashlib.sha256(encoded_block).hexdigest()
        return hash_block

    def is_chain_valid(self, chain):
        """ Determines if a chain is valid

        Arguments:
          - chain: the blockchain with all the transactions

        Returns:
          - true/false: Boolean in case of the validation
        """
        previous_block = chain[0]  # Genesis block
        block_index = 1
        while block_index < len(chain):  # Loop through all the blockchain from the genesis block
            block = chain[block_index]
            # Block200(hash, previous_hash) -> Block201(hash, previous_hash)
            if block["previous_hash"] != self.hash(previous_block):
                # We are basically comparing if the previous block has the same hash the current block has as the previous hash
                return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != "0000":
                # Checking if all the hashes of each block are a valid hash
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        """ Make a transaction.

        Arguments:
          - sender: Who sends the transaction
          - receiver: Who receives the transaction
          - amount: Sent amount

        Returns:
          - Superior index of the last block
        """
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        """ New node in the blockchain.

        Arguments:
          - address: Address of the new node ( url )
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        """ Replace the chain of the blockchain for the longest chain if is a valid chain"""
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
