from modules import *
# import pytest
from pytest_steps import test_steps, StepsDataHolder, depends_on

accounts = []
symbol = []

def createAccounts(steps_data, INSTANCE, cleartxpool):
    global accounts
    logging.info("create a couple of accounts")
    reset_wallet(INSTANCE)
    accounts = create_accounts(INSTANCE, num=2)
    assert accounts != False
    steps_data.accounts = accounts
    
def createAssets(steps_data, INSTANCE, cleartxpool):
    global symbol
    logging.info("create a couple of assets")
    symbol1 = create_asset(INSTANCE)
    assert symbol1 != False
    symbol2 = create_asset(INSTANCE)
    assert symbol2 != False
    steps_data.symbol = [symbol1, symbol2]
    symbol = [symbol1, symbol2]

def initMarket(steps_data, INSTANCE, cleartxpool):
    global accounts, symbol
    logging.info("create a couple of accounts and assets")
    reset_wallet(INSTANCE)
    accounts = create_accounts(INSTANCE, num=2)
    assert accounts != False
    steps_data.accounts = accounts

    symbol1 = create_asset(INSTANCE)
    assert symbol1 != False
    symbol2 = create_asset(INSTANCE)
    assert symbol2 != False
    steps_data.symbol = [symbol1, symbol2]
    symbol = [symbol1, symbol2]

@test_steps(initMarket)
def test_market(test_step, steps_data: StepsDataHolder, INSTANCE, cleartxpool):
    logging.info('test asset market')
    test_step(steps_data, INSTANCE, cleartxpool)

    accounts = steps_data.accounts
    symbol1 = steps_data.symbol[0]
    symbol2 = steps_data.symbol[1]

    asset1 = cybex.Asset(symbol1)
    asset2 = cybex.Asset(symbol2)
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)

    alice = cybex.Account(accounts[0]['account'])
    bob = cybex.Account(accounts[1]['account'])

    alice_asset1_balance_ahead = alice.balance(asset1)
    alice_asset2_balance_ahead = alice.balance(asset2)

    assert alice_asset1_balance_ahead.amount == 0
    assert alice_asset2_balance_ahead.amount == 0

    assert len(alice.openorders) == 0
    assert len(bob.openorders) == 0
