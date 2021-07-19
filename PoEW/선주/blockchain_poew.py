import hashlib
import json
from time import time
#from A import a  A모듈에서 a함수만 import
from uuid import uuid4
from urllib.parse import urlparse
import requests
#UUID? : 어떤 개체를 고유하게 식별하는 데 사용되는 16바이트 길이의 숫자
#32개의 16진수 5개의 그룹 그룹은 하이픈으로 구분
#예시 )022db29c-d0e2-11e5-bb4c-60f81dca7676
class Blockchain(object):
    
    def __init__(self) :
        self.chain = []
        self.current_transactions = []
        self.nodes = set() #노드 정보 set타입 = 노드 url중복 허용 안함.
        #블록체인에서 가장 최조의 블록 genesis block
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc) 
    
#pass? 조건문에서 넣어줄 조건이 없을 때, class선언에서 초기에 넣어줄 값이 없을 떄
   
    def new_block(self, proof, difficulty, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'difficulty': difficulty,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    #sensing 은 원문에서 amount (화폐 개수)로 나타났지만 IoT를 고려해서 sensing한 데이터 라는 의미로 바꿈
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
#decorator 함수를 받아 명령을 추가한 뒤 다시 함수의 형태로 반환
#정적메서드 1)@staticmethod 2) @classmethod 둘 다 인스턴스를 만들지 않아도
#class의 메서드를 바로 실행 할 수 있다.
#classmethod 에서 메소드에 cls를 인수로 줄 수 있고
#이는 클래스를 가리켜 클래스의 어떤 속성에도 접근할 수 있다.
    @staticmethod
    def hash(block):
        #json.dumps() : 파이썬 object를 json 형식의 str로 직렬화
        #sort_keys가 참이면 딕셔너리의 출력이 키로 정렬된다.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

#property(getter, setter) 필드명을 사용하는 것처럼 getter setter호출   
    @property
    def last_block(self):
        return self.chain[-1] #리스트에서 [-1]은 리스트의 마지막 요솟값
    #=======================    PoW    =================================
    def proof_of_elapsed_work(self, last_proof,timeframe):
        time_s = time #작업증명 시작 시간
        proof = 0 #문제풀이 시도 횟수
        difficulty = 1 #풀린 문제의 난이도 기본값을 1로 해도 되나..?

        while(time - time_s)>= timeframe:
            while self.valid_proof(last_proof, proof, difficulty) is False:
                proof +=1
            difficulty +=1

        return proof,difficulty
    
    @staticmethod
    def valid_proof(last_proof, proof, difficulty):
        #challenge + answer => challenge * answer?
        #원본 :guess = str(last_proof * proof).encode()
        guess = str(last_proof + proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty
    #=======================    PoW    ================================