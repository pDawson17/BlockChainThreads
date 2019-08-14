#creating blockchain

import datetime
import hashlib #inlcudes sha256
import json
from flask import Flask, jsonify, request
#pip install requests==2.18.4
import requests
from uuid import uuid4
from urllib.parse import urlparse
#building a block!
## TODO:
# 1) figure out how comments are shared on chain: make a public queue
# 2) create function allowing upvotes
# 3)
class Blockchain:

    def __init__(self):
        self.chain = [] #list containing blocks
        self.comments = [] #list pulled from comments API or somethin,
        #each comment needs comment, timestamp and score
        self.createBlock(proof = 1, prevHash = '0', data="start") #using sha256 for hash
        self.nodes = set()

    def createBlock(self, proof, prevHash, data):
        block = {"index": len(self.chain)+1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "prevHash": prevHash,
                 'comments': self.comments}
        self.comments = []
        self.chain.append(block)
        return block
        #block contains index, time, proof, prevhash in dict

    def addComment(self, comment):
        self.comments.append({"comment": comment,
                              "timestamp": str(datetime.datetime.now())})
        prevBlock = self.getPrevBlock()
        return prevBlock['index'] +1 #not sure why +1

    def getPrevBlock(self):
        return self.chain[-1]

    def proofOfWork(self, prevProof):
        #proofOfWork = easy to find, hard to verify
        newProof = 1
        checkProof = False
        while checkProof is False:
            #.encode is for formatting for sha256
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if(hashOperation[:4] == '0000'):
                checkProof = True
            else:
                newProof+=1
        return newProof

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def isChainValid(self, chain):
        index = 1
        prevBlock = chain[0]
        while(index < len(chain)):
            block = chain[index]
            if(block['prevHash'] != self.hash(prevBlock)):
                return false
            prevProof = prevBlock['proof']
            curProof = block['proof']
            hashOperation = hashlib.sha256(str(curProof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            prevBlock = block
            index+=1
        return True

    def addNode(self, address):
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)

    def replaceChain(self):
        network = self.nodes
        longestChain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/getChain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.isChainValid(chain):
                    max_length = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False
#mining a block