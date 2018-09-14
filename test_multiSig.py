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
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])

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

def test_multiSig2(INSTANCE, cleartxpool):
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
    
    obj = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],2]], 'key_auths': [], 'address_auths': []}
    update_active_keys(INSTANCE, obj, account=name3)
    
    # obj2 = {'weight_threshold': 1, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],2]], 'key_auths': [], 'address_auths': []}
    # 需要owner key才能改name3的owner key为多签
    # INSTANCE.wallet.addPrivateKey(ownerKey3)
    # update_owner_keys(INSTANCE, obj2, account=name3)

    assert cybex.Account(name3).balance('CYB') == 0
    assert cybex.Account(name3)['active']['weight_threshold'] == 2
    assert len(cybex.Account(name3)['active']['account_auths']) == 3

    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')

    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name3)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])

    # need A, B active key to fire a multi-sig transanction
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

    # account A approve proposal again, now op should be sent
    INSTANCE.approveproposal(id, appprover=name1, account=name1)
    assert cybex.Account(name1).balance('CYB') == amount-3*fee
    assert len(cybex.Account(name3).proposals) == 0
    assert cybex.Account(name3).balance('CYB') == amount-2*fee-1
    
    reset_wallet(INSTANCE)
    INSTANCE.wallet.addPrivateKey(activeKey3)
    temp2 = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name3)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp2.wallet.locked():
        temp2.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    # need A, B active key to fire multi-sig op
    INSTANCE.wallet.addPrivateKey(activeKey1)
    INSTANCE.wallet.addPrivateKey(activeKey2)
    temp2.transfer('init1', 2, "CYB", account=name3)
    id2 = cybex.Account(name3).proposals[0]['id']

    logging.info('%s new proposal id %s', name3, id2)
    reset_wallet(INSTANCE)
    # unsure why it failed if import activeKey3 here
    # INSTANCE.wallet.addPrivateKey(activeKey3)
    INSTANCE.wallet.addPrivateKey(ownerKey3)
    INSTANCE.approveproposal(id2, appprover=name3, account=name3)
    assert len(cybex.Account(name3).proposals) == 0
    assert cybex.Account(name3).balance('CYB') - (amount-2*fee-1-3*fee-2) < 1e-6

def test_multiSig3(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    # create three new accounts A B C D, D is the multi-sig account
    # parents A B, child C
    accounts = create_accounts(INSTANCE, num=4)
    if accounts == False:
        logging.info('create account error')
        assert 0
    name1 = accounts[0]['account'] # grandparent
    name2 = accounts[1]['account'] # parent1, active和owner权限仅受grandparent控制
    name3 = accounts[2]['account'] # parent2
    name4 = accounts[3]['account'] # child
    activeKey1 = accounts[0]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    ownerKey2 = accounts[1]['owner']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    ownerKey3 = accounts[2]['owner']['wif_priv_key']
    activeKey4 = accounts[3]['active']['wif_priv_key']
    ownerKey4 = accounts[3]['owner']['wif_priv_key']

    logging.info(accounts)
    INSTANCE.wallet.addPrivateKey(activeKey2)
    
    obj1 = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 2],[cybex.Account(name2)['id'],1]], 'key_auths': [], 'address_auths': []}
    update_active_keys(INSTANCE, obj1, account=name2)
    
    obj2 = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 2],[cybex.Account(name2)['id'],1]], 'key_auths': [], 'address_auths': []}
    # 需要owner key才能改name3的owner key为多签
    INSTANCE.wallet.addPrivateKey(ownerKey2)
    update_owner_keys(INSTANCE, obj2, account=name2)

    assert cybex.Account(name2).balance('CYB') == 0
    assert cybex.Account(name2)['active']['weight_threshold'] == 2
    assert cybex.Account(name2)['owner']['weight_threshold'] == 2
    assert len(cybex.Account(name2)['active']['account_auths']) == 2
    assert len(cybex.Account(name2)['owner']['account_auths']) == 2

    INSTANCE.wallet.addPrivateKey(activeKey4)
    obj3 = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name2)['id'], 1],[cybex.Account(name3)['id'],1]], 'key_auths': [], 'address_auths': []}
    update_active_keys(INSTANCE, obj3, account=name4)

    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name4, amount, 'CYB', '', account='nathan')

    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name4)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])

    # need parenet1, parent2 active key to fire a multi-sig transanction
    reset_wallet(INSTANCE)
    INSTANCE.wallet.addPrivateKey(activeKey2)
    INSTANCE.wallet.addPrivateKey(activeKey3)
    logging.debug("%s try to transfer 1 CYB to init0", name4)
    try:
        temp.transfer('init0', 1, "CYB", account=name4)
    except Exception as err:
        assert 'Missing Active Authority' in str(err)

    reset_wallet(INSTANCE)
    INSTANCE.wallet.addPrivateKey(activeKey1)
    INSTANCE.wallet.addPrivateKey(activeKey3)
    temp.transfer('init0', 1, "CYB", account=name4)

    fee = INSTANCE.fee[0]['fee']['fee']/100000
    assert cybex.Account(name4).balance('CYB') == amount-fee
    id = cybex.Account(name4).proposals[0]['id']
    logging.info('%s proposal id %s', name4, id)
    # grandparent and parent2 approve proposal
    logging.info("%s and %s accept the propsal", name1, name3)
    INSTANCE.approveproposal(id, appprover=name1, account=name1)
    INSTANCE.approveproposal(id, appprover=name3, account=name3)

    assert cybex.Account(name4).balance('CYB') -(amount-2-3*fee) < 1e-6
