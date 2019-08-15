from flask import Flask, jsonify, request
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse

from blockChain import Blockchain

app = Flask(__name__)

##TODO
#add sorting function and put it with one of the update nodes
#add route to increment a comment, figure out how to get index from button
#add function to allow poeple to see others' comments

nodeAddress = str(uuid4()).replace('-', '') #is node address on

blockchain = Blockchain('init')

@app.route('/mineBlock', methods=["GET"]) #mineblock for blocks along same chain
def mineBlock():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    proof = blockchain.proofOfWork(prevProof)
    prevHash = blockchain.hash(prevBlock)
    #blockchain.addComment(comment = "s", score = 0, link = "ok")
    block = blockchain.createBlock(proof, prevHash, name = prevBlock['name'])
    response = {"message": "you mined a blocc",
                "index": block["index"],
                "timestamp": block["timestamp"],
                "prevHash": block["prevHash"],
                "proof": proof,
                "comments": block['comments']}
    return jsonify(response), 200

@app.route("/getChain", methods = ["GET"])
def getChain():
    response = {"chain": blockchain.links[blockchain.name],
                "length": len(blockchain.links[blockchain.name]),
                }
    return jsonify(response), 200

@app.route("/getPendingComments", methods = ["GET"])
def getPendingComments():
    response = {"comments": blockchain.comments}
    return jsonify(response), 200

@app.route("/isValid", methods=["GET"])
def isValid():
    isValid = blockchain.isChainValid(blockchain.links[blockchain.name])
    if(isValid):
        response = {"message": "valid"}
    else:
        response = {"message": "invalid"}
    return jsonify(response), 200

@app.route("/replaceChain", methods=["GET"])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {"message": "updating chain",
                    "newChain": blockchain.links[blockchain.name]}
    else:
        response = {"message": "chain is longest, no update",
                    "newChain": blockchain.links[blockchain.name]}
    return jsonify(response), 200

@app.route("/switchChain", methods=["GET"])
def switchChain():
    blockchain.name = blockchain.comments[0]['link']
    response = {"message": f"switching to {blockchain.comments[0]['link']}"}
    return jsonify(response), 200

##*************POSTS BELOW
@app.route("/addCommentReq", methods = ["POST"])
def addCommentReq():
      json = request.get_json(force = True)
      commentKeys = ["comment", "score","link"]
      if not all (key in json for key in commentKeys): #a lil confused
          return "som elements of the transaction are missing", 400
      index = blockchain.addComment(json['comment'], json['score'], json['link'])
      response = {'message': f'comment added to block {index}'}
      return jsonify(response), 201

@app.route("/connectNode", methods=["POST"])
def connectNode():
    json = request.get_json(force = True)
    print(json)
    nodes = json['nodes']
    if nodes is None:
        return "no nodes", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {"message": "nodes added",
                "totalNodes": list(blockchain.nodes)}
    return jsonify(response), 200

def runApp(portNum):
    app.run(host = '0.0.0.0', port = portNum)
