import hashlib

def proof_of_work(transaction):
    nonce = 0 # 0부터 시작
    difficulty = 4 # 난이도

    
    while True:
        input_data = (str(transaction) + str(nonce)).encode()
        computed_hash = hashlib.sha256(input_data).hexdigest()
        if computed_hash[:difficulty] == "0" * difficulty:
            break
        else:
            nonce += 1
    return computed_hash, nonce

print(proof_of_work("민철이가 경우에게 1btc를 전송했습니다."))