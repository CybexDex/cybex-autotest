# coding=utf-8
'''
Created on 2018-10-8
@author: holly
Project: test whitelist uia 
'''

from  modules import *

def create_and_prepare_issue_asset(symbol, precision, max_supply, core_exchange_rate, account, instance):
    # create asset 
    instance.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, account=account)
    account.refresh()
    assert cybex.Asset(symbol, cybex_instance=instance)['symbol'] == symbol
    assert cybex.Asset(symbol, cybex_instance=instance)['precision'] == precision
    assert cybex.Asset(symbol, cybex_instance=instance)['issuer'] == dict(account)['id']
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol, cybex_instance=instance)['options']['max_supply'] == max_supply * 10 ** precision


def test_asset_name(INSTANCE, cleartxpool):

    instance = INSTANCE
    reset_wallet(instance)

    # create two accounts
    logging.info('create two new accounts')
    accounts = create_accounts(instance, num=2)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get account accountName
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)

    # transfer 2 CYB to account1 and account2 from nathan
    acc = instance.const['master_account']
    valu = 2
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s and %s' % (valu, acc, account1, account2))
    account1.refresh()
    account2.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account2.balances[0]) == valu * 10 ** account2.balances[0].asset.precision
    logging.info("%s balances: %s" % (account1, account1.balances[0]))
    logging.info("%s balances: %s" % (account2, account2.balances[0]))

    # upgrade account1 and account2
    logging.info('upgrade %s and %s to lifetime number' % (account1, account2))
    instance.wallet.unlock('123456')
    instance.wallet.unlocked()
    instance.wallet.addPrivateKey(activeKey1)
    instance.wallet.addPrivateKey(activeKey2)
    instance.upgrade_account(account=account1)
    instance.upgrade_account(account=account2)
    account1.refresh()
    account2.refresh()
    ac1 = dict(account1)
    assert ac1['registrar'] == ac1['referrer'] == ac1['lifetime_referrer'] == ac1['id']
    ac2 = dict(account2)
    assert ac2['registrar'] == ac2['referrer'] == ac2['lifetime_referrer'] == ac2['id']

    # account1 create asset
    symbol = genSymbol()
    precision = 5
    max_supply = 10000
    core_exchange_rate = 200
    logging.info('%s create asset %s, max supply is %s' % (account1, symbol, max_supply))
    create_and_prepare_issue_asset(symbol, precision, max_supply, core_exchange_rate, account1, instance)

    # account1 issue 1000 asset to account2
    amount = 1000
    logging.info('issue %s  asset %s from %s to %s' % (amount, symbol, account1, account2))
    instance.issue_asset(account2, amount, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol)  == amount
    
    # account1 issue 2000 asset to account2
    amount2 = 2000
    logging.info('issue %s  asset %s from %s to %s second time' % (amount2, symbol, account1, account2))
    instance.issue_asset(account2, amount2, symbol, account=account1)
    account2.refresh()
    assert account2.balance(symbol)  == amount2 + amount

    # create same name asset by account1
    logging.info('create same name asset %s by %s' % (symbol, account1))
    try:
        create_and_prepare_issue_asset(symbol, precision, max_supply, core_exchange_rate, account1, instance)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass

    # create same name asset by account2
    logging.info('create same name asset %s by %s' % (symbol, account2))
    try:
        create_and_prepare_issue_asset(symbol, precision, max_supply, core_exchange_rate, account2, instance)
        assert 0
    except Exception as err:
        instance.clear()
        logging.info(err)
        pass
    
    # there is different between symbol and symbol.symbol
    symbol2 = symbol + '.ABCDEF' 
    logging.info('symbol.symbol is %s' % (symbol2))
    logging.info('create asset %s by %s' % (symbol2, account1))
    try:
        create_and_prepare_issue_asset(symbol2, precision, max_supply, core_exchange_rate, account1, instance)
    except Exception as err:
        logging.info(err)

    # account1 issue 1000 asset2 to account2
    amount = 1000
    logging.info('issue %s asset %s from %s to %s' % (amount, symbol2, account1, account2))
    instance.issue_asset(account2, amount, symbol2, account=account1)
    account2.refresh()
    assert account2.balance(symbol2)  == amount


