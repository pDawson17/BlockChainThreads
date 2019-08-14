from flask import Flask, jsonify, request
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse

from blockChain import Blockchain

app = Flask(__name__)

#create address for node on Port 5000
nodeAddress = str(uuid4()).replace('-', '') #is node address on

blockchain = Blockchain()

@app.route('/mineBlock', methods=["GET"])
def mineBlock():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    proof = blockchain.proofOfWork(prevProof)
    prevHash = blockchain.hash(prevBlock)
    blockchain.addComment(comment = "Adding")
    block = blockchain.createBlock(proof, prevHash, data="figure out later")
    response = {"message": "you mined a blocc",
                "index": block["index"],
                "timestamp": block["timestamp"],
                "prevHash": block["prevHash"],
                "proof": proof,
                "comments": block['comments']}
    return jsonify(response), 200

@app.route("/getChain", methods = ["GET"])
def getChain():
    response = {"chain": blockchain.chain,
                "length": len(blockchain.chain)}
    return jsonify(response), 200

@app.route("/isValid", methods=["GET"])
def isValid():
    isValid = blockchain.isChainValid(blockchain.chain)
    if(isValid):
        response = {"message": "valid"}
    else:
        response = {"message": "invalid"}
    return jsonify(response), 200

@app.route("/addCommentReq", methods = ["POST"])
def addCommentReq():
      json = request.get_json(force = True)
      transactionKeys = ["comment"]
      if not all (key in json for key in transactionKeys): #a lil confused
          return "som elements of the transaction are missing", 400
      index = blockchain.addComment(json['comment'])
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

@app.route("/replaceChain", methods=["GET"])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {"message": "updating chain",
                    "newChain": blockchain.chain}
    else:
        response = {"message": "chain is longest, no update",
                    "newChain": blockchain.chain}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)
