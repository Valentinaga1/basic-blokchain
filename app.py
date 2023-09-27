# Mining a block in the chain
from criptocoin import Blockchain
from flask        import Flask, jsonify, request
from uuid import uuid4
# Create a wb app
app = Flask(__name__)
# run_with_ngrok(app)  

# Si se obtiene un error 500, actualizar flask, reiniciar spyder y ejecutar la siguiente línea
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create the address of the node in the port 5000
node_address = str(uuid4()).replace('-', '')

# Create a blockchain
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
  """ Mining a new block """ 

  previous_block = blockchain.get_previous_block()
  previous_proof = previous_block['proof']
  proof = blockchain.proof_of_work(previous_proof)
  previous_hash = blockchain.hash(previous_block)
  # añadimos una nueva transacción
  blockchain.add_transaction(sender = node_address, receiver = "Valentina Gómez", amount = 10)
  block = blockchain.create_block(proof, previous_hash)
  response = {'message'       : '¡New mined block!', 
              'index'         : block['index'],
              'timestamp'     : block['timestamp'],
              'proof'         : block['proof'],
              'previous_hash' : block['previous_hash'],
              'transactions'  : block['transactions']}
  return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
  """ Getting the blockchain """

  response = {'chain'   : blockchain.chain, 
              'length'  : len(blockchain.chain)}
  return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
  """ Proof if the chain is valid or not """

  is_valid = blockchain.is_chain_valid(blockchain.chain)
  if is_valid:
      response = {'message' : 'The blockchain is valid'}
  else:
      response = {'message' : 'UPS. The blockchain is Not valid'}
  return jsonify(response), 200  

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
  """ Add a new transaction to the blockchain"""

  json = request.get_json()
  transaction_keys = ['sender', 'receiver', 'amount']
  if not all(key in json for key in transaction_keys):
      return 'There is missing parameters', 400
  index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
  response = {'message': f'The transaction would be added to the block {index}'}
  return jsonify(response), 201
    
# Blockchain Decentralization

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
  json = request.get_json()
  nodes = json.get('nodes')
  if nodes is None: 
      return 'There is no nodes to add', 400
  for node in nodes:
      blockchain.add_node(node)
  response = {'message'     : 'TNodes connected: ',
              'total_nodes' : list(blockchain.nodes)}
  return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
  """ Replace the chain for the longest chain"""

  is_chain_replaced = blockchain.replace_chain()
  if is_chain_replaced:
      response = {'message' : 'Replaced',
                  'new_chain': blockchain.chain}
  else:
      response = {'message'       : 'The chain is already the longgest',
                  'actual_chain'  : blockchain.chain}
  return jsonify(response), 200  

  
if __name__ == "__main__":
    app.run()