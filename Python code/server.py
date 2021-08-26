from flask import Flask, jsonify, request
import json
from textwrap import dedent
from uuid import uuid4

from blockchain_poew import Blockchain


######## This is a executable code ######
######## We used Postman for check ######


app = Flask(__name__)
#노드 식별을 하기 위한 uuid
node_identiffier = str(uuid4()).replace('-', '')
#블록체인 객체 선언
blockchain = Blockchain()



@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof, difficulty = blockchain.proof_of_work(last_proof,60)
    #the second variable is the timeframe that considering the performance device
    #Please change it for smooth test. /The unit is seconds

    blockchain.new_transaction(
        sender=0,
        recipient=node_identiffier,
        sensing=1
    )
    #############################################

    #In here, will come a code that passes the result of its own solution
    #to each node to pick a winner in mining.
    #using Gossip protocol https://github.com/thomai/gossip-python
    #for then, we need to node discovery.
    #So we trying let each node broadcast while receiving broadcast
    #I think a method that if receive a broadcast message, send own Ip address.
    #and get Ip, write a file config that is used in the Gossip protocol source.

    ##############################################
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof,difficulty, previous_hash)
   # block = blockchain.new_block(proof, previous_hash)
   #I think it will be changed to excepting difficulty!

    response = {
        'message': 'new block forged',
        'index' : block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'difficulty':block['difficulty'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'sensing']

    if not all(k in values for k in required):
        return 'missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['sensing'])
    response = {'message': 'Transaction will be added to Block {0}'.format(index)}

    return jsonify(response), 201



@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = { 'message': 'Our chain was replaced',
                    'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)