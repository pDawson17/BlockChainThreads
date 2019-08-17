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
# 1) write route that shares comments with all nodes following the connectNode and clearNode call
#possibly implement one vote per server per block - unsure how imma do that bbut ill figure it out
# 2) viewBlock - just return a single blocks
# 3) nextBlock, sideBlock implementation
# 4) should switchChain take you to top, bottom, or closest timestamp in next chain

class Blockchain:

    def __init__(self, name):
        #self.chain = [] #list containing blocks - moved inside of set
        self.name = name #name of current block that you're on
        self.comments = {name: []} #list pulled from comments API or somethin,
        self.links = {name: []} #self.links[self.name] is now Chain
        #each comment needs comment, timestamp and score
        self.createBlock(proof = 1, prevHash = '0', name = name) #using sha256 for hash
        self.nodes = set()

    def createSubChain(self, proof, prevHash, name):
        block = {"index": len(self.links[name])+1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "prevHash": prevHash,
                 "comments": self.comments[name],
                 "name": name,
                 "link": "init"}
        self.links[name].append(block)
        return block

    def createBlock(self, proof, prevHash, name):
        #name is name of current block
        block = {"index": len(self.links[name])+1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "prevHash": prevHash,
                 'comments': self.comments[name],
                 "name": name}
        if len(self.comments[name]) > 0:
            if not (self.comments[name][0]['link'] in self.links):
                curIndex = len(self.links[name])-1
                self.links[self.comments[name][0]['link']] = []
                self.comments[self.comments[name][0]['link']] = [
                {"comment": f"First block in {self.comments[name][0]['link']}", "score": 69,"link":None}
                ]
                #self.links[(self.comments[0]['link'])] not sure what i meant that to do lol
                curHash = self.hash(self.links[name][curIndex])
                newBlock = self.createSubChain(len(self.links), curHash, self.comments[name][0]['link'])#inital proof coming from length of links
        self.links[name].append(block)
        #clear commments that were appended here
        return block
        #block contains index, time, proof, prevhash in dict

    def addComment(self, comment, score, link, origin):
        newComment = {"comment": comment,
                              "timestamp": str(datetime.datetime.now()),
                              "score": score,
                              "link": link}
        self.comments[self.name].append(newComment)
        network = self.nodes
        prevBlock = self.getPrevBlock()
        data = {
            "comment": comment,
            "score": score,
            "link": link,
            "origin": "False"
        }
        #commentData = jsonify(data)
        #add origin field, should eventually change to where origin has node id
        if(origin == "True"):
            for node in network:
                response1 = requests.post(f"http://{node}/addCommentReq", json=data)
                if(response1.status_code != 201):
                    print(f"{node} failed")
        return prevBlock['index'] +1 #not sure why +1

    def getPrevBlock(self):
        return self.links[self.name][-1]

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

    def replaceChain(self): #replaceChain works chain by chain
        network = self.nodes
        longestChain = None
        max_length = len(self.links[self.name])
        for node in network:
            response = requests.get(f"http://{node}/getChain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.isChainValid(chain):
                    max_length = length
                    longestChain = chain
        if longestChain:
            self.links[self.name] = longestChain
            return True
        return False

    def upvoteComment(self, index, origin):
        network = self.nodes
        self.comments[self.name][index]['score']+=1
        while index != 0 and self.comments[self.name][index]['score'] > self.comments[self.name][index-1]['score']:
            self.comments[self.name][index-1], self.comments[self.name][index] = self.comments[self.name][index], self.comments[self.name][index-1]
            index-=1
            #will work for now, will need realish sorting later
        if(origin == "True"):
            for node in network: #updates all comments in network - will eventually need to make a function to match everything up better
                response1 = requests.post(f"http://{node}/upvoteComment", json={"index":index, "origin": "False"})

    def clearComments(self): #ideally called only after new block created
        self.comments[self.name].clear()

#    def mergeComments(self): #works on each name level
#        betwork = self.nodes
#        for node in network:
#            response = requests.get(f"http://{node}/getPendingComments")
#            if response[self.name] != self.comments[self.name]:
#                for comment in response[self.name]:
#                    if comment not in self.comments: #rudimentary check if comment exists, something better hopefully later
#                        self.comments.append(comment)
