from brownie import TextStorage, accounts

def main():

    admin = accounts[0]  #first index account in ganache as admin

    #deploy contract using the admin account
    contractDeploy = TextStorage.deploy({
        "from" : admin
    })

    print(contractDeploy)