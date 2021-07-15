import os, sys, time, random
import threading
import hashlib
from queue import Queue

answer = '00000'

class block():
    def __init__(self, blockIndex, prevHash):
        self.blockIndex = blockIndex
        self.prevHash = prevHash

def generateNode(newBlock, q):
    stage = 'ready'

    while True:
        if stage == 'ready':
            nextHash = solveQuiz(newBlock)
            stage = 'solved'
            q.put(newBlock.blockIndex)
            q.put(nextHash)
            #
            break
        elif stage == 'solved':
            checkResult()
            stage = 'ready'
        time.sleep(1)


def checkResult():
    print("nothing")


def solveQuiz(block):

    nonce = 1
    while True:
        challenge = str(block.blockIndex) + str(block.prevHash) + str(nonce)
        attempt = hashlib.sha256(challenge.encode())
        result = attempt.hexdigest()

        if result[0:len(answer)] == answer:
            return result
        nonce += 1


if __name__ == "__main__" :

    threadList = []
    q = Queue()

    blockIndex = 0
    firstHash = 'Kookmin University'

    newBlock = block(blockIndex, firstHash)
    blockIndex += 1

    newThread = threading.Thread(target=generateNode, args=(newBlock, q))
    newThread.start()
    newThread.join()

    winner = q.get()
    nextHash = q.get()
    print(winner, nextHash)

    while blockIndex < 10:
        newBlock = block(blockIndex, nextHash)
        blockIndex += 1
        newThread = threading.Thread(target=generateNode, args=(newBlock, q))
        newThread.start()
        newThread.join()

        winner = q.get()
        nextHash = q.get()
        print(winner, nextHash)


    #print(nextHash)

    # threadList = []
    # threadIndex = 0
    #
    # while threadIndex < 5:
    #     print("stage : " + str(threadIndex) + "\n")
    #     flag = [False, ]
    #
    #     newThread = threading.Thread(target=work, args=(threadIndex, flag))
    #     threadList.append(newThread)
    #     threadIndex += 1
    #
    #     newThread.start()
    #
    #     while flag[0] == False:
    #         time.sleep(1)
    #
    #     flag[0] = True
