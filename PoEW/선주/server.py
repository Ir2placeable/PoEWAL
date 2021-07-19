from flask import Flask, jsonify, request
import json
from textwrap import dedent
from uuid import uuid4
import requests

from werkzeug.wrappers import response

from blockchain_poew import Blockchain

app = Flask(__name__)
#노드 식별을 하기 위한 uuid
node_identiffier = str(uuid4()).replace('-', '')
#블록체인 객체 선언
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    difficulty_max =0
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof, difficulty = blockchain.proof_of_work(last_proof)
    #??????????????????????????????????????????
    if(difficulty_max<difficulty):
        difficulty_max = difficulty

        if(difficulty_max<=difficulty):
            blockchain.new_transaction(
                sender=0,
                recipient=node_identiffier,
                sensing=1
            )
            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(proof,difficulty, previous_hash)

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
    app.run(host='192.168.0.38', port=5000)