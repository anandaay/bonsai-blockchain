from brownie import *
p = project.load('brownie-dir')
p.load_config()


from brownie.project.BrownieDirProject import *
import constants

abi = TextStorage.abi
bytecode = TextStorage.bytecode

#contract address created after deploying contract
contract_address = constants.created_contract_address

#connect to blockchain server using web3 library
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))


def getTextByTxHash(tx_hash):
    returned_text = ''
    try :      
        tx = w3.eth.get_transaction(tx_hash)
        ctx_addr = tx['to']    
        contract = w3.eth.contract(address=ctx_addr, abi=abi)

        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)                
                
        if tx_receipt.status == 1:
        # Proses log acara dari transaksi tersebut
            for log in tx_receipt.logs:
                # Periksa apakah log acara terkait dengan event TextChanged
                if log.address == ctx_addr:                
                    # Dekode data dari log acara
                    decoded_log = contract.events.TextChanged().process_log(log)                
                    returned_text = decoded_log['args']['newText']
                    break                                                    
                                            
        print(returned_text)
        
    except Exception as e:
        print(f"An error occurred: {e}")         
        
    return returned_text

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


from flask import Flask, request, render_template, jsonify
import csv
import base64
import io

app = Flask(__name__)

@app.route("/")
def index():
    
    # stored_text = getTextByContractAddress(contract_address)   
    return render_template('index.html')


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
        
        if ctx_addr != '':            
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
        
        if hash != '':
            returned_text = getTextByTxHash(hash)
                                                              
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
        
        if ctx_addr != '':                                 
            returned_text = setTextInCtx(ctx_addr, sender_address, sender_pk, value)
            
        else:
            returned_text = 'Wrong Parameter Input'
                
    else:
        returned_text = 'error'

    print(returned_text)
    return returned_text

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    uploaded_file = request.files['csv_file']

    if uploaded_file.filename.endswith('.csv'):
        # Process CSV file
        data = []
        stream = io.StringIO(uploaded_file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        for row in reader:
            data.append(row)
        return jsonify(data)
    else:
        return jsonify({"error": "File is not a CSV"}), 400

@app.route('/upload_jpg', methods=['POST'])
def upload_jpg():
    uploaded_file = request.files['jpg_file']

    if uploaded_file.filename.endswith('.jpg') or uploaded_file.filename.endswith('.jpeg'):
        # Process JPG file
        img_stream = io.BytesIO(uploaded_file.read())
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return jsonify({'image': img_base64})
    else:
        return jsonify({"error": "File is not a JPG"}), 400
