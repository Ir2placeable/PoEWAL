import hashlib
import json
from time import time
from speedtest import Speedtest
from datetime import datetime
#from A import a  A모듈에서 a함수만 import
from uuid import uuid4
#UUID? : 어떤 개체를 고유하게 식별하는 데 사용되는 16바이트 길이의 숫자
#32개의 16진수 5개의 그룹 그룹은 하이픈으로 구분
#예시 )022db29c-d0e2-11e5-bb4c-60f81dca7676
class Blockchain(object):
    
    def __init__(self) :
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        #블록체인에서 가장 최조의 블록 genesis block
        self.new_block(previous_hash=1, proof=100) 
    
#pass? 조건문에서 넣어줄 조건이 없을 때, class선언에서 초기에 넣어줄 값이 없을 떄
   
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
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
    def proof_of_elapsed_work(self, last_proof):
        proof = 0
        # TODO : 타임프레임을 어떤 기준으로 할당할 것인가?
        # 일단 요청 클라이언트의 인터넷 업로드 속도로 구현했음.
        # 10분 - 업로드 속도 -> 업로드 속도가 빠를 수록 적은 시간을 할당받는 구조
        speed = Speedtest()
        upload_time = speed.upload()
        time_frame = 600 - (int(upload_time) // 1000000)
        time_end = time.time() + time_frame
        is_solved = False
        hash_output = ''
        zero_count = 0


        while time.time() < time_end: # 주어진 타임 프레임동안만 실행됨
            is_solved, hash_output = self.valid_proof(last_proof, proof)
            if is_solved: # 문제를 푼 case
                return proof, is_solved, zero_count
            proof +=1
        
        # 문제를 못풀었는데 주어진 시간이 끝난 case
        #TODO : 어떻게 처리하지?
        # 만약 문제를 먼저 풀면 그 사람이 채굴하는거고, 문제를 못풀었는데 시간이 끝났다면 채굴자들 중에서 앞에 0의 개수가
        # 가장 많은 사람이 채굴을 해야하니까 이건 서버에서 처리해야할 문제라고 생각함.
        # 서버로 각 해시결과 값에서 앞에 0이 얼마나 있는지를 count해서 보내주고 그 중 max값 찾으면 되지 않을까?
        
        for i in hash_output:
            if i == '0':
                zero_count += 1
            else:
                break
        return proof, is_solved, zero_count
        
    
    @staticmethod
    def valid_proof(last_proof, proof):
        #challenge + answer => challenge * answer?
        #원본 :guess = str(last_proof * proof).encode()
        guess = str(last_proof + proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000", guess_hash
    #=======================    PoEW    ================================
