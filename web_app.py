from brownie import *
p = project.load('brownie-dir')
p.load_config()


from brownie.project.BrownieDirProject import *

abi = TextStorage.abi
bytecode = TextStorage.bytecode

#contract address created after deploying contract
contract_address = '0x046dc538608FAa4D978FCFcfd3479e9FaE77aE42'

#connect to blockchain server using web3 library
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

def getTextByContractAddress(ctx_addr):
    targetContract = w3.eth.contract(address=ctx_addr, abi=abi)
    currentStoredText = targetContract.functions.getText().call() #getText function from contract

    print(currentStoredText)
    return currentStoredText


from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def index():
    
    stored_text = getTextByContractAddress(contract_address)   
    return stored_text


@app.route("/get_text_by_ctx_addr", methods=['GET'])
def getTextByCtxAddr():
    
    returned_text = ''
    if request.method == 'GET':  
        ctx_addr = request.args['ctx_addr']
        returned_text = getTextByContractAddress(ctx_addr) 
    else:
        returned_text = 'Wrong Request Method'
          
    return returned_text