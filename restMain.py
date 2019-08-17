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
#figure out how to clear comments and still do switchChain
nodeAddress = str(uuid4()).replace('-', '') #is node address on

blockchain = Blockchain('init')

##*****************GET BELOW
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
    #need to recieve index of currBlocc
    json = request.get_json(force = True)
    index = json['index']
    blockchain.name = blockchain.links[blockchain.name][index]['comments'][0]['link']
    response = {"message": f"switching to {blockchain.name}"}
    return jsonify(response), 200

##*************POSTS BELOW
@app.route("/addCommentReq", methods = ["POST"])
def addCommentReq():
      json = request.get_json(force = True)
      commentKeys = ["comment", "score","link","origin"]
      if not all (key in json for key in commentKeys): #a lil confused
          return "som elements of the transaction are missing", 400
      index = blockchain.addComment(json['comment'], json['score'], json['link'],json['origin'])
      response = {'message': f'comment added to block {index}'}
      return jsonify(response), 201

@app.route("/connectNode", methods=["POST"])
def connectNode():
    json = request.get_json(force = True)
    nodes = json['nodes']
    if nodes is None:
        return "no nodes", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {"message": "nodes added",
                "totalNodes": list(blockchain.nodes)}
    return jsonify(response), 200

@app.route("/upvoteComment", methods=["POST"])
def upvoteComment():
    json = request.get_json(force = True) #receive json input of index of voting
    #format: {'index': 0}
    blockchain.upvoteComment(json['index'],json['origin'])
    response = {"message": f"incremented {json['index']}"}
    return jsonify(response), 200
##**************PATCH BELOW
@app.route("/updateNodes", methods=["PATCH"])
def updateNodes(): #only called after connectNode has been called
    updateList = []
    for chain in blockchain.links:
        blockchain.name = chain
        updatedChain = blockchain.replaceChain()
        if updatedChain:
            updateList.append(chain)
    response = {"message": f"updated: {updateList}"}
    return jsonify(response), 200

def runApp(portNum):
    app.run(host = '0.0.0.0', port = portNum)
