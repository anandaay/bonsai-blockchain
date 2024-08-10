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

sender_address = constants.sender_account_address
sender_pk = constants.sender_account_pk


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
        else:
            returned_text = 'An error occurred: Transaction Receipt Not Found'                                                    
        
    except Exception as e:
        print(f"An error occurred: {e}") 
        returned_text = str(f"An error occurred: {e}")       
        
    return returned_text

def getTextByContractAddress(ctx_addr):
   
    returned_text = ''
    try:
        targetContract = w3.eth.contract(address=ctx_addr, abi=abi)
        returned_text = targetContract.functions.getText().call() #getText function from contract
    except Exception as e:
        print(f"An error occurred: {e}") 
        returned_text = str(f"An error occurred: {e}")  
    
    return returned_text

def setTextInCtx(ctx_addr, sndr_addr, sndr_pk, value):
    hashResult = ''
    try:
        contract = w3.eth.contract(address=ctx_addr, abi=abi)
        tx = contract.functions.setText(value).build_transaction({
            'from' : sndr_addr,
            'nonce' : w3.eth.get_transaction_count(sndr_addr),
            'gasPrice': 1000000
        })

        signed_tx = w3.eth.account.sign_transaction(tx, sndr_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(tx_receipt)      
        hashResult = tx_receipt['transactionHash'].hex()
        
    except Exception as e:
        print(f"An error occurred: {e}") 
        hashResult = str(f"An error occurred: {e}")    
     
    
    return hashResult


from flask import Flask, request, render_template, jsonify
import csv
import base64
import io
from PIL import Image

app = Flask(__name__)

@app.route("/")
def index():  
    return render_template('index.html')

@app.route("/blockchain_test")
def blockchainTest():
    return render_template('blockchain_test.html')

@app.route("/get_text_by_ctx_addr", methods=['GET'])
def getTextByCtxAddr():
    success = False    
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
             returned_text = 'An error occurred: Wrong Parameter Input'
    else:
        returned_text = 'An error occurred: Wrong Request Method'
    
    error_code = returned_text.find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True          
    
    return jsonify({'success': success, 'data' : returned_text, 'error_code' : error_code })

@app.route("/get_text_by_hash", methods=['GET'])
def getTextByHash():
    success = False
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
            returned_text = 'An error occurred: Wrong Parameter Input'
    else:
        returned_text = 'An error occurred: Wrong Request Method'
    
    error_code = returned_text.find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True  
             
    return jsonify({'success': success, 'data' : returned_text})

@app.route("/set_text_in_ctx_addr", methods=['GET'])
def setTextInContract():
    success = False
    returned_text = ''
    ctx_addr = ''
    sender_address = ''
    sender_pk = ''
    value = ''

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
            returned_text = 'An error occurred: Wrong Parameter Input'
                
    else:
        returned_text = 'An error occurred: Wrong Request Method'
    
    error_code = returned_text.find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True  
    
    return jsonify({'success': success, 'data' : returned_text })

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    plant_id = request.form['plant_id']
    uploaded_file = request.files['csv_file']
    returned_text = ''
    success = False

    if uploaded_file.filename.endswith('.csv'):
        # Process CSV file
        data = []
        stream = io.StringIO(uploaded_file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        for row in reader:
            data.append(row)
        
        storing_data = str({'plant_id': plant_id, 'data': data, 'type' : 'csv'})
        returned_text = setTextInCtx(contract_address, sender_address, sender_pk, storing_data)
        
    else:
        returned_text = "An error occurred: File is not a CSV"

    error_code = str(returned_text).find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True 
    
    return jsonify({'success': success, 'data' : returned_text })
    
    
@app.route('/upload_jpg', methods=['POST'])
def upload_jpg():
    plant_id = request.form['plant_id']
    uploaded_file = request.files['jpg_file']
    returned_text = ''
    success = False

    if uploaded_file.filename.endswith('.jpg') or uploaded_file.filename.endswith('.jpeg'):
        # Process JPG file
        img = Image.open(uploaded_file)
        
        # Ubah ukuran gambar, misalnya menjadi 200x200 pixel (atau sesuai kebutuhan)
        img = img.resize((100, 100))
        
        # Konversi gambar menjadi base64
        img_stream = io.BytesIO()
        img.save(img_stream, format="JPEG")
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        
        storing_data = str({'plant_id': plant_id, 'image': img_base64, 'type' : 'image'})
        returned_text = setTextInCtx(contract_address, sender_address, sender_pk, storing_data)
    else:
        returned_text = "An error occurred: File is not a JPG"

    error_code = str(returned_text).find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True 
    
    return jsonify({'success': success, 'data' : returned_text })


@app.route('/check_hash', methods=['POST'])
def check_hash():    
    success = False
    returned_text = ''
    hash = ''
                
    if request.method == 'POST': 
        
        try:                           
            hash = request.form.get('hash') or request.args.get('hash')
            
            if hash != '':
                returned_text = getTextByTxHash(hash)            
                                                                
            else:
                returned_text = 'An error occurred: Wrong Parameter Input'
                
        except Exception as e:
            print(f"An error occurred: {e}") 
            returned_text = str(f"An error occurred: {e}")  
            
    else:
        returned_text = 'An error occurred: Wrong Request Method'
    
    error_code = returned_text.find('An error occurred') 
    if returned_text != '' and error_code == -1:
        success = True  
             
    return jsonify({'success': success, 'data' : returned_text})
        
