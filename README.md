//TODO
//to run run main.py
//to change port # edit runApp method param
##CRISTIAN PLEASE:

//make front end
refresh button method:
  calls:
    connectNode- pass in list of all working nodes in this format: {
        "nodes": ["http://127.0.0.1:5001",
                  "http://127.0.0.1:5002",
                  "http://127.0.0.1:5000"
                ]
    }
    replaceChain - nothing passed
    isValid - nothing passed
    getChain -nothing passed - pull data to be displayed from the list returned by this if isValid passes

text box inputs:
  takes in text data, convert to json format like so:
  {
    "comment": string,
    "score": int,
    "link": string
  }

mine block method:
  calls mineBlock request

display:
  all messages that have been queued before mining using getPendingComments (returns list of json objects)
  the current block using getChain

eventually add like button for each comment calling a request to like, I havent done that route yet
