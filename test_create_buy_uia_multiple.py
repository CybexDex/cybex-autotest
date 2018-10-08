# coding=utf-8
'''
Created on 2018-09-27
@author: holly
Project: test whitelist uia 
'''

from modules import *

def test_create_buy_uia_multiple_reverse(INSTANCE, market, data4market, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])

    m = cybex.Market(base=asset1, quote=asset2, cybex_instance=instance)

    alice = cybex.Account(data4market['alice']['account'], cybex_instance=instance)
    bob = cybex.Account(data4market['bob']['account'], cybex_instance=instance)

    instance.wallet.addPrivateKey(data4market['alice']['active']['wif_priv_key'])
    instance.wallet.addPrivateKey(data4market['bob']['active']['wif_priv_key'])

    m.buy(3, 150, 3600, killfill=False, account=alice)
    time.sleep(10)
    logging.info('alice openorders %s' % alice.openorders)

    m.sell(1, 100, 3600, killfill=False, account=bob)
    time.sleep(10)
#    m.sell(2, 50, 3600, killfill=False, account=bob)
    m.sell(2, 100, 3600, killfill=False, account=bob)
    time.sleep(10)
    m.sell(3, 100, 3600, killfill=False, account=bob)

    logging.info('alice openorders %s' % len(alice.openorders))
    logging.info('bob openorders %s' % len(bob.openorders))
    logging.info('bob openorders %s' % bob.openorders)

    for bal in alice.balances:
        if bal.symbol == asset1.symbol:
            logging.info("check alice's assert %s balance %s" % (asset1.symbol, bal.amount))
            assert bal.amount == 9999550
        if bal.symbol == asset2.symbol:
            logging.info("check alice's assert %s balance %s" % (asset2.symbol, bal.amount))
            assert bal.amount == 150

    for bal in bob.balances:
        if bal.symbol == asset1.symbol:
            logging.info("check bob's assert %s balance %s" % (asset1.symbol, bal.amount))
            assert bal.amount == 450
        if bal.symbol == asset2.symbol:
            logging.info("check bob's assert %s balance %s" % (asset2.symbol, bal.amount))
            assert bal.amount == 9999700



def test_create_buy_uia_multiple_reverse_fract(INSTANCE, market, data4market, cleartxpool):
    
    instance = INSTANCE
    reset_wallet(instance)
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])

    m = cybex.Market(base=asset1, quote=asset2, cybex_instance=instance)

    alice = cybex.Account(data4market['alice']['account'], cybex_instance=instance)
    bob = cybex.Account(data4market['bob']['account'], cybex_instance=instance)

    alice_asset1 = 0
    alice_asset2 = 0
    bob_asset1 = 0
    bob_asset2 = 0
    
    logging.info('function2 ....')
    for bal in alice.balances:
        if bal.symbol == asset1.symbol:
            alice_asset1 = bal.amount
            logging.info('alice asset1 %s' % alice_asset1)
        if bal.symbol == asset2.symbol:
            alice_asset2 = bal.amount
            logging.info('alice asset2 %s' % alice_asset2)
    for bal in bob.balances:
        if bal.symbol == asset1.symbol:
            bob_asset1 = bal.amount
            logging.info('bob asset1 %s' % bob_asset1)
        if bal.symbol == asset2.symbol:
            bob_asset2 = bal.amount
            logging.info('bob asset2 %s' % bob_asset2)

    instance.wallet.addPrivateKey(data4market['alice']['active']['wif_priv_key'])
    instance.wallet.addPrivateKey(data4market['bob']['active']['wif_priv_key'])

    m.buy(10, 10, 3600, killfill=False, account=alice)
    time.sleep(10)
    m.buy(5, 20, 3600, killfill=False, account=alice)
    time.sleep(10)
    m.buy(3, 30, 3600, killfill=False, account=alice)
    time.sleep(10)

    m.sell(5, 30, 3600, killfill=False, account=bob)

    logging.info('alice openorders %s' % len(alice.openorders))
    logging.info('alice openorders %s' % alice.openorders)
    logging.info('bob openorders %s' % len(bob.openorders))

    for bal in alice.balances:
        if bal.symbol == asset1.symbol:
            logging.info("check alice's assert %s balance %s" % (asset1.symbol, bal.amount))
            assert alice_asset1 - bal.amount == 290
        if bal.symbol == asset2.symbol:
            logging.info("check alice's assert %s balance %s" % (asset2.symbol, bal.amount))
            assert bal.amount - alice_asset2 == 30

    for bal in bob.balances:
        if bal.symbol == asset1.symbol:
            logging.info("check bob's assert %s balance %s" % (asset1.symbol, bal.amount))
            assert bal.amount - bob_asset1 == 200
        if bal.symbol == asset2.symbol:
            logging.info("check bob's assert %s balance %s" % (asset2.symbol, bal.amount))
            assert bob_asset2 - bal.amount == 30




