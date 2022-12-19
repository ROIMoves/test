from web3 import Web3
from termcolor import cprint
import time
import json
import random
from tqdm import tqdm
import decimal
import requests
from tabulate import tabulate
from decimal import Decimal

#roi moves
currency_price = []
def prices():
    response = requests.get(url=f'https://api.gateio.ws/api/v4/spot/tickers')
    currency_price.append(response.json())

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty / int("".join((["1"]+ ["0"]*decimal)))


def check_balance(privatekey, rpc_chain, symbol):
    try:
            
        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        balance = web3.eth.get_balance(web3.toChecksumAddress(account.address))

        humanReadable = web3.fromWei(balance,'ether')

        # pidesz
        for currency in currency_price[0]:
            if currency['currency_pair'] == f'{symbol}_USDT':
                price_ = Decimal(currency['last'])
                price = price_ + price_ * Decimal(0.2)

        gas = web3.eth.gas_price
        gasPrice = decimalToInt(gas, 18)

        return round(Decimal(humanReadable) - Decimal(Decimal(gasPrice)*Decimal(price)) - Decimal(0.001), 7)


    except Exception as error:
        # pizda
        None

def check_token_balance(privatekey, rpc_chain, address_contract, ERC20_ABI):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        wallet = account.address
        token_contract = web3.eth.contract(address=web3.toChecksumAddress(address_contract), abi=ERC20_ABI) 
        token_balance = token_contract.functions.balanceOf(web3.toChecksumAddress(wallet)).call()

        symbol = token_contract.functions.symbol().call()
        token_decimal = token_contract.functions.decimals().call()

        humanReadable = decimalToInt(token_balance, token_decimal) 

        cprint(f'\nbalance : {round(humanReadable, 5)} {symbol}', 'white')

        return humanReadable

    except Exception as error:
        # cprint(f'error : {error}', 'yellow')
        None

table = []
def transfer_token(privatekey, amount_to_transfer, to_address, chain_id, scan, rpc_chain, address_contract, ERC20_ABI):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))

        token_contract = web3.eth.contract(address=Web3.toChecksumAddress(address_contract), abi=ERC20_ABI)
        account = web3.eth.account.privateKeyToAccount(privatekey)
        address = account.address
        nonce = web3.eth.getTransactionCount(address)

        symbol = token_contract.functions.symbol().call()
        token_decimal = token_contract.functions.decimals().call()

        amount = intToDecimal(amount_to_transfer, token_decimal) 
        gasLimit = web3.eth.estimate_gas({'to': Web3.toChecksumAddress(to_address), 'from': Web3.toChecksumAddress(address),'value': web3.toWei(0.0001, 'ether')}) + random.randint(70000, 200000)
        
        tx_built = token_contract.functions.transfer(
            Web3.toChecksumAddress(to_address),
            int(amount)
            ).buildTransaction({
                'chainId': chain_id,
                'gas': gasLimit,
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
            })

        tx_signed = web3.eth.account.signTransaction(tx_built, privatekey)
        tx_hash = web3.eth.sendRawTransaction(tx_signed.rawTransaction)


