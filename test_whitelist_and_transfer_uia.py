# coding=utf-8
'''
Created on 2018-09-19
@author: holly
Project: test whitelist uia 
'''

from modules import *


def test_issue_whitelist_uia(INSTANCE, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)

    # create three accounts 
    logging.info('create three new accounts')
    accounts = create_accounts(instance, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get account accountName
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)

    # transfer 5 CYB to account1 from nathan
    acc = instance.const['master_account']
    valu = 5 
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account1))
    account1.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    logging.info("%s balances: %s" % (account1, account1.balances[0]))

    # upgrade account1
    logging.info('upgrade %s to lifetime number' % (account1))
    instance.wallet.unlock('123456')
    instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)
    instance.upgrade_account(account=account1)
    account1.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']
 
    # account1 create asset
    symbol = genSymbol()
    precision = 5
    max_supply = 10000
    core_exchange_rate = 200
    logging.info('%s create asset, max supply is %s' % (account1, max_supply))
    instance.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, account=account1)
    account1.refresh()
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == dict(account1)['id']
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision

    # set asset flags
    flags = {"white_list":0x02}
    ast = cybex.Asset(symbol, cybex_instance=instance)
    ast.setoptions(flags)

    # account1 issue 1000 asset to account2         success  check  account2 balances 1000
    amount = 1000
    logging.info('issue %s asset from %s to %s' % (amount, account1, account2))
    instance.issue_asset(account2, amount, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol) == amount

    # add account1 to asset whitelist_authorities
    logging.info('add %s to asset %s whitelist' % (account1, symbol))
    ret = ast.add_authorities('whitelist', authorities=[account1])
#    logging.info(ret)

    # account1 issue 1000 asset to account2         failed
    logging.info('issue %s asset from %s to %s after add %s to asset whitelist_authorities' % (amount, account1, account2, account1))
    try:
        instance.issue_asset(account2, amount, symbol, account=account1)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    # add account3 to account1's whitelisting_accounts     
    logging.info("add %s to %s whitelisting_accounts" % (account3, account1))
    instance.account_whitelist(accountName3, lists=['white'], account=accountName1)

    # account1 issue 1000 asset to account2           failed
    logging.info('issue %s asset from %s to %s after add %s to %s whitelisting_accounts' % (amount, account1, account2, account3, account1))
    try:
        instance.issue_asset(account2, amount, symbol, account=account1)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    # add account2 to account1's whitelisting_accounts  
    logging.info('add %s to %s whitelisting_accounts' % (account2, account1))
    instance.account_whitelist(accountName2, lists=['white'], account=accountName1)   

    # account1 issue 1000 asset to account2      success
    logging.info('issue %s asset from %s to %s after add %s to %s whitelist_accounts' % (amount, account1, account2, account2, account1))
    instance.issue_asset(account2, amount, symbol, account=account1)

    # check account2 balances 
    account2.refresh()
    assert account2.balance(symbol) == amount * 2 




def test_transfer_whitelist_blacklist_uia(INSTANCE, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)

    # create three accounts 
    logging.info('create three new accounts')
    accounts = create_accounts(instance, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get account accountName
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)

    # transfer 5 CYB to account1 and account3 from nathan
    acc = instance.const['master_account']
    valu =  5 
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account1))
    instance.transfer(accountName3, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account3))
    account1.refresh()
    account3.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account3.balances[0]) == valu * 10 ** account3.balances[0].asset.precision
    logging.info("%s balances: %s" % (account1, account1.balances[0]))
    logging.info("%s balances: %s" % (account3, account3.balances[0]))

    # upgrade account1
    logging.info('upgrade %s to lifetime number' % (account1))
    instance.wallet.unlock('123456')
    instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)
    instance.upgrade_account(account=account1)
    account1.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']
    
    # upgrade account3
    logging.info('upgrade %s to lifetime number' % (account3))
    instance.wallet.addPrivateKey(activeKey3)
    instance.upgrade_account(account=account3)
    account3.refresh()
    ac3 = dict(account3)
    assert ac3['registrar'] == ac3['referrer'] == ac3['lifetime_referrer'] == ac3['id']
    instance.wallet.removeAccount(accountName3)
 
    # account1 create asset
    symbol = genSymbol()
    precision = 5
    max_supply = 10000
    core_exchange_rate = 200
    logging.info('%s create asset, max supply is %s' % (account1, max_supply))
    instance.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, account=account1)
    account1.refresh()
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == dict(account1)['id']
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision

    # set asset flags
    flags = {"white_list":0x02}
    ast = cybex.Asset(symbol, cybex_instance=instance)
    ast.setoptions(flags)

    # account1 issue 1000 asset to account2         success  check  account2 balances 1000
    amount = 1000
    logging.info('issue %s asset from %s to %s' % (amount, account1, account2))
    instance.issue_asset(account2, amount, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol) == amount

    # add account1 to asset whitelist_authorities
    logging.info('add %s to asset %s whitelist' % (account1, symbol))
    ret = ast.add_authorities('whitelist', authorities=[account1])
#    logging.info(ret)

    # add account2 to account1's whitelisting_accounts  
    logging.info('add %s to %s whitelisting_accounts' % (account2, account1))
    instance.account_whitelist(accountName2, lists=['white'], account=accountName1)   

    # account1 issue 1000 asset to account2      success
    logging.info('issue %s asset from %s to %s after add %s to %s whitelisting_accounts' % (amount, account1, account2, account2, account1))
    instance.issue_asset(account2, amount, symbol, account=account1)

    # check account2 balances 
    account2.refresh()
    assert account2.balance(symbol) == amount * 2

    # transfer CYB to account3 from account2, failed
    trf_valu = 500
    instance.wallet.addPrivateKey(activeKey2)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account2))
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    logging.info('transfer %s from %s to %s' % (symbol, account2, account3))
    try:
        instance.transfer(accountName3, trf_valu, symbol, '', accountName2)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    # add account3 to account1's whitelisting_accounts
    logging.info('add %s to %s whitelisting_accounts' % (account3, account1))
    instance.account_whitelist(accountName3, lists=['white'], account=accountName1)   

    # transfer CYB to account3 from account2, success
    logging.info('transfer %s from %s to %s after adding %s to %s whitelist' % (symbol, account2, account3, account3, account1))
    instance.transfer(accountName3, trf_valu, symbol, '', accountName2)
    account3.refresh()
    assert account3.balance(symbol) == trf_valu 

    # add account3 to account1's blacklist
    logging.info('add %s to %s blacklisting_accounts' % (account3, account1))
    instance.account_whitelist(accountName3, lists=['black'], account=accountName1)   
 
    # transfer CYB to account3 from account2, failed 
    logging.info('transfer %s from %s to %s after adding %s to %s blacklist' % (symbol, account2, account3, account3, account1))
    try:
        instance.transfer(accountName3, trf_valu, symbol, '', accountName2)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass




def test_transfer_restricted(INSTANCE, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)

    # create three accounts 
    logging.info('create three new accounts')
    accounts = create_accounts(instance, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get account accountName
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)

    # transfer 5 CYB to account1 and account2 from nathan
    acc = instance.const['master_account']
    valu = 5 
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account1))
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s' % (valu, acc, account2))
    account1.refresh()
    account2.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account2.balances[0]) == valu * 10 ** account2.balances[0].asset.precision
    logging.info("%s balances: %s" % (account1, account1.balances[0]))
    logging.info("%s balances: %s" % (account2, account2.balances[0]))

    # upgrade account1
    logging.info('upgrade %s to lifetime number' % (account1))
    instance.wallet.unlock('123456')
    instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)
    instance.upgrade_account(account=account1)
    account1.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']
 
    # account1 create asset
    symbol = genSymbol()
    precision = 5
    max_supply = 10000
    core_exchange_rate = 200
    logging.info('%s create asset, max supply is %s' % (account1, max_supply))
    instance.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, account=account1)
    account1.refresh()
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == dict(account1)['id']
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision

    # account1 issue 1000 asset to account2         success  check  account3 balances 1000
    amount = 1000
    logging.info('issue %s asset from %s to %s' % (amount, account1, account2))
    instance.issue_asset(account2, amount, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol) == amount

    # transfer asset from account2 to account3
    logging.info('transfer asset %s from %s to %s' % (symbol, account2, account3))
    instance.wallet.addPrivateKey(activeKey2)
    trf_valu = 100
    instance.transfer(accountName3, trf_valu, symbol, '', accountName2)
    account3.refresh()
    assert account3.balance(symbol) == trf_valu

    # set asset flags
    flags = {"transfer_restricted":0x08}
    ast = cybex.Asset(symbol, cybex_instance=instance)
    ast.setoptions(flags)
    
    # transfer asset from account2 to account3
    logging.info('transfer asset %s from %s to %s after set transfer_restricted flags' % (symbol, account2, account3))
    try:
        instance.transfer(accountName3, trf_valu, symbol, '', accountName2)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass
    
    # transfer asset from account2 to account3
    logging.info('transfer asset %s from %s to %s after set transfer_restricted flags' % (symbol, account2, account1))
    instance.transfer(accountName1, trf_valu, symbol, '', accountName2)
    account1.refresh()
    assert account1.balance(symbol) == trf_valu
    
   

 
