import hashlib
import time, random, os, sys
import threading

collision_threshold = 10

# 주어진 time frame 동안 연산을 수행함
# difficulty level 이상으로 제일 어려운 문제를 푼다.
# 이때, 난이도 3을 풀면, 난이도 4를 풀어야하고, 난이도 5를 풀어야 한다.
# ex) level=3 이면 3자리 이상의 '0'을 가진 결과를 제출함.
def proof_of_elapsed_work(time_frame, challenge, difficulty_level):
    proof = []
    nonce = 0

    time0 = time.time()
    while (time.time() - time0) < time_frame:
        MSB = '0' * difficulty_level
        attempt = str(challenge * nonce).encode()
        attempt = hashlib.sha256(attempt).hexdigest()

        # 비교
        if attempt[0:difficulty_level] == MSB:
            proof = [challenge, nonce, attempt]
            difficulty_level += 1
        nonce += 1
    return proof

def set_time_frame(computational_capacity, residual_energy, number_of_collisions, difficulty_level):
    # 이전 마이닝에서 충돌이 기준치(10회) 이상 발생한 경우, 난이도를 1 올림
    if number_of_collisions > collision_threshold :
        difficulty_level += 1

    # !미완 : time frame의 공식을 만들어야함
    time_frame = computational_capacity + residual_energy + number_of_collisions + difficulty_level
    return time_frame, difficulty_level

# 다른 마이너의 결과값이 맞는지 확인하고
# 최대 개수의 '0'을 찾아낸 마이너의 번호(max_
def check_others_result(results):
    miner_index = 0
    winner = 0
    max_count = 0

    # results가 맞는 연산을 했는지 확인
    for result in results:
        attempt = str(result[0] * result[1]).encode()
        attempt = hashlib.sha256(attempt).hexdigest()

        # 결과가 맞는지 검사
        if attempt == result[2]:
            # 해당 결과값의 '0' 개수를 센다.
            count = 0
            for word in attempt:
                if word == '0':
                    count += 1
                else:
                    break

            # max count를 골라낸다.
            if count > max_count :
                max_count = count
                winner = miner_index
        miner_index += 1

    return winner, max_count

time_frame, difficulty_level = set_time_frame(1,1,1,1)
print("time frame : " , time_frame)
print("level : ", difficulty_level)

results = []
results.append(proof_of_elapsed_work(time_frame, 'abcd', difficulty_level))
print(results)

winner, zeros = check_others_result(results)
print("winner is :", winner, " with" ,zeros , "zeros")
