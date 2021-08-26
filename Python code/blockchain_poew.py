import hashlib
import json
import time

from uuid import uuid4
from urllib.parse import urlparse
import requests

# We take code from https://blog.naver.com/pjt3591oo/221181592127 which referenced https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
# And we edited for PoEWAL
class Blockchain(object):
    
    def __init__(self) :
        self.chain = []
        self.current_transactions = []
        self.nodes = set() #노드 정보 set타입 = 노드 url중복 허용 안함.
        #블록체인에서 가장 최조의 블록 genesis block
        self.new_block(previous_hash=1,difficulty =1, proof=100)

    def register_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc) 
    
   
    def new_block(self, proof, difficulty, previous_hash=None):
    #def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            #Now I'm thinking the block doesn't need difficulty info!
            #because we only use difficulty in PoW.
            # I mean, After the winner selected.
            'difficulty': difficulty,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, sensing):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'sensing':sensing,
        })
        return self.last_block['index'] + 1

    #각 블록과 증명의 유효성 검사
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            #블럭의 해시가 맞는지 확인
            if block['previous_hash'] != self.hash(last_block):
                return False
            #PoW가 해결했는지 확인
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        return True
    
    #다른 네트워크에 있는 노드 검사하여 길이가 긴 체인으로 교체
    def resolve_conflicts(self):
        
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get('http://{%s}/chain'%(node))
            if response.status_code == 200:
                length = response.json()['length'] 
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

    @staticmethod
    def hash(block):
        #json.dumps() : 파이썬 object를 json 형식의 str로 직렬화
        #sort_keys가 참이면 딕셔너리의 출력이 키로 정렬된다.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
    #=======================    PoW    =================================
    def proof_of_work(self, last_proof,timeframe): #timeframe is coming from server
        time_s = time.time()
        proof = 0
        difficulty = 1 
        while True:
            if(time.time() - time_s) > (timeframe):
                break
            if(self.valid_proof(last_proof, proof, difficulty)):
                difficulty +=1
                #if sove a problem, and still in timeframe, up difficult of the problem
                continue
            
        return proof , difficulty
    
    @staticmethod
    def valid_proof(last_proof, proof, difficulty):
        guess = str(last_proof + proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty
    #=======================    PoW    ================================