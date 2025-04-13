from web3 import Web3
from solcx import compile_standard
import json
import time
import solcx

# Connect to Sepolia testnet via Infura
infura_url = "https://sepolia.infura.io/v3/7cdbc5d83b9a4081bdd23b31288464b7"  # Replace with your Infura Project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

with open("HealthBudgetManager.bytecode", "r") as bytecode_file:
        bytecode = bytecode_file.read().strip() 
        
with open("HealthBudgetManager.abi.json") as f:
    abi = json.load(f)

contract = web3.eth.contract(abi=abi, bytecode=bytecode)
# Generate a new Ethereum account
    # account = web3.eth.account.create()
private_key = "c4245e2866f05311ae0ade73132bc299bbc81924207fe459734cf3b8d4d24403"  # Replace with your private key
account = web3.eth.account.from_key(private_key)
account_address = account.address
# # Install a specific version of solc
def created_contract():
    solcx.install_solc('0.8.0')  # You can specify any version that matches your contract's version

    # Check the installed solc versions
    installed_versions = solcx.get_installed_solc_versions()
    print("Installed solc versions:", installed_versions)

    # Check if connection is successful
    if web3.is_connected:
        print("Connected to Sepolia network!")
    else:
        print("Failed to connect to Sepolia network.")
        
    

    # # Get the private key (hex format)
    # private_key = account.key.hex()

    # # Get the public address (Ethereum address)
    # address = account.address

    # Print the private key and address
    print(f"Private Key: {private_key}")
    print(f"Address: {account_address}")


    # contract_bytecode = "0x346100305760206104ed5f395f518060a01c6100305760405260405160015561048361003461000039610483610000f35b5f80fd5f3560e01c60026003821660011b61047b01601e395f51565b631fe89e5e81186101075760a436103417610477576004358060a01c610477576101005260243560040180356103e8811161047757506020813501808261012037505060443560040180356103e8811161047757506020813501808261054037505060843560040180356103e881116104775750602081350180826109603750506100a16103f5565b6020610120510180610120610d805e5060206105405101806105406111a05e506064356115c05260206109605101806109606115e05e505f610100516020525f5260405f205f6064905b8060051b610d800151818401556001018181186100eb57505050005b635930806281186103f157602436103417610477576004358060a01c610477576040525f6040516020525f5260405f205f6064905b808301548160051b6060015260010181811861013c57505050608080610ce05280610ce001602060605101806060835e508051806020830101601f825f03163682375050601f19601f8251602001011690508101905080610d005280610ce0016020610480510180610480835e508051806020830101601f825f03163682375050601f19601f825160200101169050810190506108a051610d205280610d405280610ce00160206108c05101806108c0835e508051806020830101601f825f03163682375050601f19601f82516020010116905081019050610ce0f35b63158686b5811861024e57602436103417610477576004358060a01c61047757610100526102456103f5565b61010051600155005b63200a1b9181186103f157602436103417610477576004358060a01c610477576040526020806060525f6040516020525f5260405f2081606001608080825280820160208454015f81601f0160051c602181116104775780156102c357905b808701548160051b8501526001018181186102ad575b5050508051806020830101601f825f03163682375050601f19601f825160200101169050810190508060208301526021830181830160208254015f81601f0160051c6021811161047757801561032b57905b808501548160051b850152600101818118610315575b5050508051806020830101601f825f03163682375050601f19601f825160200101169050905081019050604283015460408301528060608301526043830181830160208254015f81601f0160051c6021811161047757801561039f57905b808501548160051b850152600101818118610389575b5050508051806020830101601f825f03163682375050601f19601f82516020010116905090508101905090509050810190506060f35b63f851a44081186103f157346104775760015460405260206040f35b5f5ffd5b6001543318156104755760208060a052601a6040527f4f6e6c792061646d696e2063616e20616464207265636f72647300000000000060605260408160a00160208251018083835e508051806020830101601f825f03163682375050601f19601f8251602001011690509050810190506308c379a060805280600401609cfd5b565b5f80fd03d50219001803f1855820a20a4ace216870966f8323c21867d042b9f92f87e4a2f147820f2e4f7884cb48190483810800a1657679706572830004010036"
    # with open("HealthBudgetManager.bytecode", "r") as bytecode_file:
    #     bytecode = bytecode_file.read().strip() 
        
    # with open("HealthBudgetManager.abi.json") as f:
    #     abi = json.load(f)

    pending_tx = web3.eth.get_transaction_count(account_address, 'pending')
    print("Pending TX count:", pending_tx)

    balance_wei = web3.eth.get_balance(account_address)
    balance_eth = web3.from_wei(balance_wei, 'ether')

    print(f"Balance of {account_address}: {balance_eth} ETH")

    # Contract setup
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    gas_estimate = contract.constructor(account_address).estimate_gas({'from': account_address})
    print("Gas Estimate :", gas_estimate)
    # Build the transaction
    tx = contract.constructor(account_address).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 300000,
        'gasPrice': web3.to_wei('30', 'gwei')
    })

    # Sign the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Send it
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Get tx receipt
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print("Contract deployed at:", tx_receipt.contractAddress)
    contractAddress = tx_receipt.contractAddress
    return contractAddress

def generate_patient_id(patient_email):
    try:
        # Create a web3 instance (already connected to your blockchain)
        web3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/7cdbc5d83b9a4081bdd23b31288464b7'))

        # # The patient's email address (make sure it's unique)
        # patient_email = "john.doe@example.com"

        # Hash the email address using keccak256 to get a unique hash
        hashed_email = web3.solidity_keccak(['string'], [patient_email])

        # Convert the hash to an Ethereum address (take the last 20 bytes)
        patient_eth_address = web3.to_checksum_address(hashed_email[-20:])  # Last 20 bytes are used for address

        # Print the generated patient Ethereum address
        print(f"Generated Patient Ethereum Address: {patient_eth_address}")
        
        return patient_eth_address
    except Exception as e:
        print("Error in Creating Patient Address", str(e))

def adding_records(transcription, prescription_details, appointment_date, summary, patient_address):
        # Call the function to add a record
    try: 
        tx = contract.functions.add_record(
            patient_address,
            transcription,
            prescription_details,
            appointment_date,  # Appointment date (as timestamp)
            summary
        ).build_transaction({
            'from': account_address,
            'to': contractaddress,
            'nonce': web3.eth.get_transaction_count(account_address),
            'gas': 300000,
            'gasPrice': web3.to_wei('30', 'gwei')
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction hash: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(str(e))
        return False

contractaddress = created_contract()

transcription = """Junior Doctor (Dr. Riya): Good afternoon, Miss Das. I saw your throat exam notes—still feeling soreness?

Miss Das: Yeah, swallowing is uncomfortable, especially when I wake up. It eases up a bit during the day.

Dr. Riya: That’s pretty common in mild infections. I’m prescribing Azithromycin 250mg—one tablet a day, after meals, for three days.

Miss Das: Okay, and is that an antibiotic?

Dr. Riya: Yes, a mild one. I’m also including a Vitamin C tablet—take one each day for a week to help your body recover faster.

Miss Das: Do I need to go to the pharmacy?

Dr. Riya: Nope, I’ll send it to the pharmacist now. You’ll just pick it up later today.

Miss Das: That’s easy—thanks a lot, Doctor."""
prescription_details = "Prescription: Miss Das, Date: [Insert Date], Doctor: Dr. Riya, Junior Doctor. 1. Azithromycin 250mg - 1 tablet daily after meals for 3 days for throat infection. 2. Vitamin C 500mg - 1 tablet daily for 7 days to aid recovery. Pick up at [Insert Pharmacy Name] after [Insert Time] today. Follow prescribed dosages. Contact the clinic if any side effects occur."
appointment_date = 1633046400
summary = """I saw Dr. Riya this afternoon. She asked about my throat soreness, and I told her it hurts when I swallow, especially in the morning, but it gets a bit better during the day. She said it’s common with mild infections and prescribed Azithromycin 250mg—one tablet a day after meals for three days. She also gave me a Vitamin C tablet to take once a day for a week to help me recover faster. I asked if I needed to go to the pharmacy, and she said no, she’d send the prescription there, so I can just pick it up later today. It’s all pretty easy."""
email_id = "tjmenezes@yahoo.in"

# patient_address = generate_patient_id(email_id)

# records_added = adding_records(transcription, prescription_details, appointment_date, summary, patient_address)

# if records_added:
#     record = contract.functions.get_record(patient_address).call()
#     print("Patient Record:", record)

