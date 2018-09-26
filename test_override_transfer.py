# coding=utf-8
'''
Created on 2018-09-19
@author: holly
Project: test override transfer 
'''

from modules import *

@pytest.mark.skip(reason="skip to save money in nathan")
def test_override_transfer(INSTANCE, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)
#    instance.wallet.removeAccount("nathan")
    
    # create three account
    logging.info("create new accounts")
    accounts = create_accounts(instance, num=3)
    if accounts == False:
       logging.info('create account error')
       assert 0

    # get account accountName and id
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    accountId1 = dict(account1)['id']
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)
    
    # unlock wallet and add private key
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    instance.wallet.unlock("123456")
    assert instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)

    # transfer 5 CYB to account1 from nathan
    acc = instance.const['master_account']
    valu = 5 
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    logging.info("transfer %s CYB from %s to %s" % (valu, acc, account1))
    account1.refresh() 
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision

    # upgrade account1 to lifetime number
    logging.info("upgrade %s to lifetime number" % (account1))
    instance.upgrade_account(account=account1)
    account1.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']

    # create asset
    symbol = genSymbol() 
    logging.info(" %s create asset %s" % (account1, symbol))
    precision = 5
    max_supply = 1000
    core_exchange_rate = 200
    ass = instance.create_asset(symbol,  precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, override_authority=True, account=account1)
#    logging.info(ass)
    account1.refresh()
    logging.info(account1.balances)
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == accountId1
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision 

    # issue asset
    logging.info("issue all asset from %s to %s" % (account1, account2))
    instance.issue_asset(account2, max_supply, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol) == max_supply

    # override transfer  
    over_amount = 100
    flags = {"override_authority":0x04}
    ast = cybex.Asset(symbol, cybex_instance=instance)
    ast.setoptions(flags)

    logging.info("override transfer %s asset from %s to %s" % (over_amount, account2, account3))
    try: 
        instance.override_transfer(account2, account3, over_amount, symbol)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    logging.info("override transfer %s asset from %s to %s by %s" % (over_amount, account2, account3, account2)) 
    instance.wallet.removeAccount(accountName1)
    instance.wallet.addPrivateKey(activeKey2)
    try:
        instance.override_transfer(account2, account3, over_amount, symbol, account=account2)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    logging.info("override transfer %s asset from %s to %s by %s" % (over_amount, account2, account3, account1))
    instance.wallet.removeAccount(accountName2)
    instance.wallet.addPrivateKey(activeKey1)
    instance.override_transfer(account2, account3, over_amount, symbol, account=account1)

    # check the balances in account2 and account3
    logging.info("check balances in %s and %s" % (account2, account3))
    account2.refresh()
    account3.refresh()
    assert int(account2.balances[0].amount) == (max_supply - over_amount)
    assert int(account3.balances[0].amount) == over_amount



@pytest.mark.skip(reason="skip to save money in nathan")
def test_override_transfer_test2(INSTANCE, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)
#    instance.wallet.removeAccount("nathan")
    
    # create three account
    logging.info("create new accounts")
    accounts = create_accounts(instance, num=3)
    if accounts == False:
       logging.info('create account error')
       assert 0

    # get account accountName and id
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    accountId1 = dict(account1)['id']
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)
    
    # unlock wallet and add private key
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    instance.wallet.unlock("123456")
    assert instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)

    # transfer 5 CYB to account1 from nathan
    acc = instance.const['master_account']
    valu = 5 
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    logging.info("transfer %s CYB from %s to %s" % (valu, acc, account1))
    account1.refresh() 
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision

    # upgrade account1 to lifetime number
    logging.info("upgrade %s to lifetime number" % (account1))
    instance.upgrade_account(account=account1)
    account1.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']

    # create asset
    symbol = genSymbol() 
    logging.info(" %s create asset %s" % (account1, symbol))
    precision = 5
    max_supply = 1000
    core_exchange_rate = 200
    ass = instance.create_asset(symbol,  precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, override_authority=True, account=account1)
#    logging.info(ass)
    account1.refresh()
    logging.info(account1.balances)
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == accountId1
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision 

    # issue asset
    logging.info("issue all asset from %s to %s" % (account1, account2))
    instance.issue_asset(account2, max_supply, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol) == max_supply

    # override transfer  
    over_amount = 100

    logging.info("override transfer %s asset from %s to %s" % (over_amount, account2, account3))
    try: 
        instance.override_transfer(account2, account3, over_amount, symbol)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    logging.info("override transfer %s asset from %s to %s by %s" % (over_amount, account2, account3, account2)) 
    instance.wallet.removeAccount(accountName1)
    instance.wallet.addPrivateKey(activeKey2)
    try:
        instance.override_transfer(account2, account3, over_amount, symbol, account=account2)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    logging.info("override transfer %s asset from %s to %s by %s" % (over_amount, account2, account3, account1))
    instance.wallet.removeAccount(accountName2)
    instance.wallet.addPrivateKey(activeKey1)
    try:
        instance.override_transfer(account2, account3, over_amount, symbol, account=account1)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass 

    # check the balances in account2 
    logging.info("check balances in %s" % (account2))
    account2.refresh()
    assert int(account2.balances[0].amount) == max_supply


