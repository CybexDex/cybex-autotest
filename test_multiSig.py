# coding=utf-8
'''
Created on 2018-09-05
@author: sarcy
Project: 
'''
from modules import *
import logging

def test_multiSig1(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    # create three new accounts A B C, C is the multi-sig account
    # parents A B, child C
    accounts = create_accounts(INSTANCE, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0
    name1 = accounts[0]['account']
    name2 = accounts[1]['account']
    name3 = accounts[2]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    ownerKey2 = accounts[1]['owner']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    ownerKey3 = accounts[2]['owner']['wif_priv_key']

    logging.info(accounts)
    INSTANCE.wallet.addPrivateKey(activeKey3)
    
    obj = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1]], 'key_auths': [], 'address_auths': []}
    update_active_keys(INSTANCE, obj, account=name3)
    
    obj2 = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1]], 'key_auths': [], 'address_auths': []}
    # 需要owner key才能改owner key 为多签
    INSTANCE.wallet.addPrivateKey(ownerKey3)
    update_owner_keys(INSTANCE, obj2, account=name3)

    assert cybex.Account(name3).balance('CYB') == 0
    assert cybex.Account(name3)['active']['weight_threshold'] == 2
    assert cybex.Account(name3)['owner']['weight_threshold'] == 2

    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')

    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name3)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(INSTANCE.const['test_wallet_pwd'])

    # # need A, B active key to fire a multi-sig transanction
    reset_wallet(INSTANCE)
    INSTANCE.wallet.addPrivateKey(activeKey1)
    INSTANCE.wallet.addPrivateKey(activeKey2)
    logging.debug("%s try to transfer 1 CYB to init0", name3)
    temp.transfer('init0', 1, "CYB", account=name3)

    fee = INSTANCE.fee[0]['fee']['fee']/100000
    assert cybex.Account(name3).balance('CYB') == amount-fee
    id = cybex.Account(name3).proposals[0]['id']
    logging.info('%s proposal id %s', name3, id)
    
    # approve propsal should cost fee
    logging.info("%s accept the propsal", name1)
    # account A approve proposal
    INSTANCE.approveproposal(id, appprover=name1, account=name1)
    assert cybex.Account(name1).balance('CYB') == amount-fee
    # account A remove previous proposal
    logging.info("%s remove previous propsal", name1)
    INSTANCE.disapproveproposal(id, account=name1)
    assert cybex.Account(name1).balance('CYB') == amount-2*fee

    # account B approve proposal
    logging.info("%s accept the propsal", name2)
    INSTANCE.approveproposal(id, appprover=name2, account=name2)
    assert cybex.Account(name2).balance('CYB') == amount-fee

    # account A approve proposal again
    INSTANCE.approveproposal(id, appprover=name1, account=name1)
    assert cybex.Account(name1).balance('CYB') == amount-3*fee
    assert len(cybex.Account(name3).proposals) == 0
    assert cybex.Account(name3).balance('CYB') == amount-2*fee-1
