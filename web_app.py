from brownie import *
p = project.load('brownie-dir')
p.load_config()


from brownie.project.BrownieDirProject import *

abi = TextStorage.abi
bytecode = TextStorage.bytecode

contract_address = '0x046dc538608FAa4D978FCFcfd3479e9FaE77aE42'

#connect to blockchain server using web3 library
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

#contract address created after deploying contract
targetContract = w3.eth.contract(address=contract_address, abi=abi)
currentStoredText = targetContract.functions.getText().call() #getText function from contract

print(currentStoredText)


from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    debugStr = "<p>Abi: " + str(abi) + "<br>Bytecode: " + str(bytecode) + "</p>"
    return debugStr