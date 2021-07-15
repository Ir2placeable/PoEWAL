import hashlib
from typing import Tuple

blockChain = []
difficulty = 4

def genesis_block():
    data = 'Genesis'
    prev_hash = ''
    nonce, current_hash = hash(data, prev_hash, difficulty)
    add_block(data, prev_hash, difficulty, nonce, current_hash)

def normal_block(data: str):
    prev_hash = blockChain[-1][-1]
    nonce, current_hash = hash(data, prev_hash, difficulty)
    add_block(data, prev_hash, difficulty, nonce, current_hash)

def add_block(data: str, prev_hash: str, difficulty: int, nonce: int, current_hash: str):
    blockChain.append((data, prev_hash, difficulty, nonce, current_hash))

def hash(data : str, prev_hash: str, difficulty: int) -> Tuple(int, str):
    nonce = 0
    while True:
        input_data = (data + prev_hash + str(nonce)).encode()
        computed_hash = hashlib.sha256(input_data).hexdigest()
        if computed_hash[:difficulty] == "0" * difficulty:
            break
        else:
            nonce += 1
    return nonce, computed_hash




