from brownie import *
p = project.load('brownie-dir')
p.load_config()


from brownie.project.BrownieDirProject import *

abi = TextStorage.abi
bytecode = TextStorage.bytecode

#contract address created after deploying contract
contract_address = '0x2A7D046d26A4B5816356599cB30D85a22131AF99'

#connect to blockchain server using web3 library
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

def getTextByContractAddress(ctx_addr):
    targetContract = w3.eth.contract(address=ctx_addr, abi=abi)
    currentStoredText = targetContract.functions.getText().call() #getText function from contract

    print(currentStoredText)
    return currentStoredText

def setTextInCtx(ctx_addr, sndr_addr, sndr_pk, value):
    contract = w3.eth.contract(address=ctx_addr, abi=abi)
    tx = contract.functions.setText(value).build_transaction({
        'from' : sndr_addr,
        'nonce' : w3.eth.get_transaction_count(sndr_addr),
        'gasPrice': 200000
    })

    signed_tx = w3.eth.account.sign_transaction(tx, sndr_pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(tx_receipt)       
    
    return tx_receipt['transactionHash'].hex()


from flask import Flask, request, render_template
app = Flask(__name__)

@app.route("/")
def index():
    
    stored_text = getTextByContractAddress(contract_address)   
    return stored_text


@app.route("/blockchain_test")
def blockchainTest():
    return render_template('blockchain_test.html')

@app.route("/get_text_by_ctx_addr", methods=['GET'])
def getTextByCtxAddr():
    
    returned_text = ''
    ctx_addr = ''
    if request.method == 'GET':  
        
        if request.args['ctx_addr']:
            ctx_addr = request.args['ctx_addr']
            
        elif request.form['ctx_addr']:
            ctx_addr = request.form['ctx_addr']
        
        if ctx_addr is not '':            
            returned_text = getTextByContractAddress(ctx_addr)
            
        else:
             returned_text = 'Wrong Parameter Input'
    else:
        returned_text = 'Wrong Request Method'
          
    return returned_text

@app.route("/get_text_by_hash", methods=['GET'])
def getTextByHash():
             
    returned_text = ''
    hash = ''
    if request.method == 'GET':
        
        if request.args['hash']:
            hash = request.args['hash']
            
        elif request.form['hash']:
            hash = request.form['hash']
        
        if hash is not '':
            
            tx_receipt = w3.eth.get_transaction_receipt(hash)
            print(tx_receipt)
            #ctx_addr = tx_receipt['contractAddress']
            ctx_addr = tx_receipt['to']     
            returned_text = getTextByContractAddress(ctx_addr) 
            
        else:
            returned_text = 'Wrong Parameter Input'
    else:
        returned_text = 'Wrong Request Method'
          
    return returned_text

@app.route("/set_text_in_ctx_addr", methods=['GET'])
def setTextInContract():
    returned_text = ''
    ctx_addr = ''
    sender_address = ''
    sender_pk = ''
    value = ''
    hash = ''
    # print(request.method)
    if request.method == 'GET':
        if request.args['ctx_addr']:
            sender_address = request.args['sender_address']
            ctx_addr = request.args['ctx_addr']
            sender_pk = request.args['sender_pk']    
            value = request.args['value']
            
        elif request.form['ctx_addr']:
            sender_address = request.form['sender_address']
            ctx_addr = request.form['ctx_addr']
            sender_pk = request.form['sender_pk']    
            value = request.form['value']  
        
        if ctx_addr is not '':                                 
            returned_text = setTextInCtx(ctx_addr, sender_address, sender_pk, value)
            
        else:
            returned_text = 'Wrong Parameter Input'
                
    else:
        returned_text = 'error'

    print(returned_text)
    return returned_text
    