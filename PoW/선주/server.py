from flask import Flask, jsonify, request
import json
from textwrap import dedent
from uuid import uuid4

from werkzeug.wrappers import response

from blockchain import Blockchain

app = Flask(__name__)
#노드 식별을 하기 위한 uuid
node_identiffier = str(uuid4()).replace('-', '')
#블록체인 객체 선언
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']

    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(
        sender=0,
        recipient=node_identiffier,
        sensing=1
    )
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'new block forged',
        'index' : block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
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

if __name__ == '__main__':
    app.run(host='192.168.0.38', port=5000)