# coding=utf-8
'''
Created on 2018-10-10
@author: holly
Project: test proposal with one operation and two operations 
'''

from modules import *
import bitsharesbase.operations as  btsops


def test_proposal_one_operation_with_multisign(INSTANCE, cleartxpool):

    instance = INSTANCE
    reset_wallet(instance)

    # create two accounts
    logging.info('create new accounts')
    accounts = create_accounts(instance, num=4)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get accounts information
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    accountName3 = accounts[2]['account']
    accountName4 = accounts[3]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    activeKey4 = accounts[3]['active']['wif_priv_key']
    activePub1 = accounts[0]['active']['pub_key']
    activePub2 = accounts[1]['active']['pub_key']
    activePub3 = accounts[2]['active']['pub_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account3 = cybex.Account(accountName3, cybex_instance=instance)
    account4 = cybex.Account(accountName4, cybex_instance=instance)

    # add active key
    instance.wallet.addPrivateKey(activeKey1)
    instance.wallet.addPrivateKey(activeKey2)

    # transfer 3 CYB to account1 and account2 from nathan
    acc = instance.const['master_account'] 
    valu = 3
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    instance.transfer(accountName3, valu, 'CYB', '', acc)
    instance.transfer(accountName4, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s, %s, %s and %s' % (valu, acc, account1, cybex.Account(accountName2, cybex_instance=instance), account3, account4))
    account1.refresh()
    account3.refresh()
    account4.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account3.balances[0]) == valu * 10 ** account3.balances[0].asset.precision
    assert int(account4.balances[0]) == valu * 10 ** account4.balances[0].asset.precision
   
    # make account2 a multisign account, controled by account3 and account4
    obj = {'weight_threshold':2, 'account_auths':[[account3['id'], 1], [account4['id'], 1]], 'key_auths':[[activePub2, 1]], 'address_auths':[]}
    update_active_keys(instance, obj,  account=accountName2)
    account2 = cybex.Account(accountName2, cybex_instance=instance)
    account2.refresh()
    assert account2['active']['weight_threshold'] == 2

    # proposal with one transaction
    instance.proposer = accountName1
    instance.proposal_expiration = int(60*60*24)

    fee = instance.fee[0]['fee']['fee']/100000
    logging.info('fee: %s' % fee)
    amount = 200000

    transfer = btsops.Transfer(**{
        "fee": {"amount": fee, "asset_id":"1.3.0"},
        "from": dict(account2)["id"],
        "to": dict(account1)["id"],
        "amount": {"amount": amount, "asset_id": "1.3.0"},
        "extensions": [],
    })

    instance.finalizeOp([transfer], account1, "active")
    logging.info('%s create a proposal' % account1)
    account2.refresh()
#    logging.info(dict(account2.proposals[0]))
    p_id = dict(account2.proposals[0])['id']
    logging.info('proposal id: %s' % p_id)
    logging.info('proposal: %s transfer %s CYB to %s' % (account2, amount/100000, account1))
    
    instance.proposer = None 
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account2, account2.balance('CYB')))
    logging.info('after %s proposal, %s balance cyb: %s' % (account3, account3, account3.balance('CYB')))
    logging.info('after %s proposal, %s balance cyb: %s' % (account3, account4, account4.balance('CYB')))

    # check proposal
    assert len(dict(account2.proposals[0])['required_active_approvals']) == 1 
    assert len(dict(account2.proposals[0])['available_active_approvals']) == 0 
    assert account1.balance('CYB') == valu - fee
    assert account2.balance('CYB') == valu
    logging.info('this proposal has not been executed')
#    time.sleep(60)
    # add account3 sign
#    instance.wallet.removePrivateKeyFromPublicKey(activePub1)
#    instance.wallet.removePrivateKeyFromPublicKey(activePub2)
    instance.wallet.addPrivateKey(activeKey3)
    logging.info('%s accept the proposal' % (account3))
    instance.approveproposal(p_id, account=accountName3, approver=accountName3)
    account1.refresh()
    account2.refresh()
    account3.refresh()
    account4.refresh()
    logging.info('after %s sign, %s balance cyb: %s' % (account3, account1, account1.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account3, account2, account2.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account3, account3, account3.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account3, account4, account4.balance('CYB')))
    assert len(dict(account2.proposals[0])['required_active_approvals']) == 1 
    assert len(dict(account2.proposals[0])['available_active_approvals']) == 1 
    assert account1.balance('CYB') == valu - fee
    assert account2.balance('CYB') == valu 
    assert account3.balance('CYB') == valu - fee
    assert account4.balance('CYB') == valu 
    logging.info('this proposal has not been executed')
    
#    time.sleep(60)
    # add account4 sign
#    instance.wallet.removePrivateKeyFromPublicKey(activePub3)
    instance.wallet.addPrivateKey(activeKey4)
    logging.info('%s accept the proposal' % (account4))
    instance.approveproposal(p_id, account=accountName4, approver=accountName4)
    account1.refresh()
    account2.refresh()
    account3.refresh()
    account4.refresh()
    logging.info('after %s sign, %s balance cyb: %s' % (account4, account1, account1.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account4, account2, account2.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account4, account3, account3.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account4, account4, account4.balance('CYB')))
    assert account1.balance('CYB') == valu - fee + amount/100000
    assert account2.balance('CYB') == valu - fee - amount/100000
    assert account3.balance('CYB') == valu - fee
    assert account4.balance('CYB') == valu - fee 
    logging.info('this proposal has been executed successfully')


def test_proposal_two_accounts(INSTANCE, cleartxpool):

    instance = INSTANCE
    reset_wallet(instance)

    # create two accounts
    logging.info('create new accounts')
    accounts = create_accounts(instance, num=2)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get accounts information
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    ownerKey2 = accounts[1]['owner']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)

    # add active key
    instance.wallet.addPrivateKey(activeKey1)
    instance.wallet.addPrivateKey(activeKey2)

    # transfer 3 CYB to account1 and account2 from nathan
    acc = instance.const['master_account'] 
    valu = 3
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s and %s' % (valu, acc, account1, account2))
    account1.refresh()
    account2.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account2.balances[0]) == valu * 10 ** account2.balances[0].asset.precision
    
    # proposal with two transaction
    instance.proposer = accountName1
    instance.proposal_expiration = int(60*60*24)

    fee = instance.fee[0]['fee']['fee']/100000
    logging.info('fee: %s' % fee)
    amount1 = 100000
    amount2 = 200000
    transfer1 = btsops.Transfer(**{
        "fee": {"amount": fee, "asset_id":"1.3.0"},
        "from": dict(account1)["id"],
        "to": dict(account2)["id"],
        "amount": {"amount": amount1, "asset_id": "1.3.0"},
        "extensions": [],
    })

    transfer2 = btsops.Transfer(**{
        "fee": {"amount": fee, "asset_id":"1.3.0"},
        "from": dict(account2)["id"],
        "to": dict(account1)["id"],
        "amount": {"amount": amount2, "asset_id": "1.3.0"},
        "extensions": [],
    })

    instance.finalizeOp([transfer1, transfer2], account1, "active")
    logging.info('%s create a proposal' % account1)
    account1.refresh()
    p_id = dict(account1.proposals[0])['id']
#    logging.info(dict(account1.proposals[0]))
    logging.info('proposal id: %s' % p_id)
    logging.info('proposal: %s transfer %s CYB to %s, %s transfer %s CYB to %s' % (account1, amount1/100000, account2, account2, amount2/100000, account1))
    
    instance.proposer = None 
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account2, account2.balance('CYB')))

    # check proposal
    assert len(dict(account1.proposals[0])['required_active_approvals']) == 2
    assert len(dict(account1.proposals[0])['available_active_approvals']) == 0 
    assert account1.balance('CYB') == valu - fee
    assert account2.balance('CYB') == valu
    logging.info('this proposal has not been executed')

    # add account1 sign
    logging.info('%s accept the proposal' % (account1))
    instance.approveproposal([p_id], account=accountName1, approver=accountName1)
    account1.refresh()
    account2.refresh()
    assert len(dict(account1.proposals[0])['required_active_approvals']) == 2
    assert len(dict(account1.proposals[0])['available_active_approvals']) == 1 
    assert account1.balance('CYB') == valu - 2*fee
    assert account2.balance('CYB') == valu
    logging.info('after %s sign, %s balance cyb: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account1, account2, account2.balance('CYB')))
    logging.info('this proposal is not executed yet')

    # add account2 sign
    logging.info('%s accept the proposal' % (account2))
    instance.approveproposal(p_id, account=accountName2, approver=accountName2)
    account1.refresh()
    account2.refresh()
    logging.info('after %s sign, %s balance cyb: %s' % (account2, account1, account1.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account2, account2, account2.balance('CYB')))
    assert account1.balance('CYB') == valu - 3*fee - amount1/100000 + amount2/100000
    assert account2.balance('CYB') == valu - 2*fee - amount2/100000 + amount1/100000
    logging.info('this proposal has been executed successfully')


def test_proposal_delete_operation(INSTANCE, cleartxpool):

    instance = INSTANCE
    reset_wallet(instance)

    # create two accounts
    logging.info('create new accounts')
    accounts = create_accounts(instance, num=2)
    if accounts == False:
        logging.info('create account error')
        assert 0

    # get accounts information
    accountName1 = accounts[0]['account']
    accountName2 = accounts[1]['account']
    activeKey1 = accounts[0]['active']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    account1 = cybex.Account(accountName1, cybex_instance=instance)
    account2 = cybex.Account(accountName2, cybex_instance=instance)

    # add active key
    instance.wallet.addPrivateKey(activeKey1)
    instance.wallet.addPrivateKey(activeKey2)

    # transfer 3 CYB to account1 and account2 from nathan
    acc = instance.const['master_account'] 
    valu = 3
    instance.transfer(accountName1, valu, 'CYB', '', acc)
    instance.transfer(accountName2, valu, 'CYB', '', acc)
    logging.info('transfer %s CYB from %s to %s and %s' % (valu, acc, account1, account2))
    account1.refresh()
    account2.refresh()
    assert int(account1.balances[0]) == valu * 10 ** account1.balances[0].asset.precision
    assert int(account2.balances[0]) == valu * 10 ** account2.balances[0].asset.precision
    
    # proposal with two transaction
    instance.proposer = accountName1
    instance.proposal_expiration = int(60*60*24)

    fee = instance.fee[0]['fee']['fee']/100000
    logging.info('fee: %s' % fee)
    amount1 = 100000
    amount2 = 200000
    transfer1 = btsops.Transfer(**{
        "fee": {"amount": fee, "asset_id":"1.3.0"},
        "from": dict(account1)["id"],
        "to": dict(account2)["id"],
        "amount": {"amount": amount1, "asset_id": "1.3.0"},
        "extensions": [],
    })

    transfer2 = btsops.Transfer(**{
        "fee": {"amount": fee, "asset_id":"1.3.0"},
        "from": dict(account2)["id"],
        "to": dict(account1)["id"],
        "amount": {"amount": amount2, "asset_id": "1.3.0"},
        "extensions": [],
    })

    instance.finalizeOp([transfer1, transfer2], account1, "active")
    logging.info('%s create a proposal' % account1)
    account1.refresh()
    p_id = dict(account1.proposals[0])['id']
#    logging.info(dict(account1.proposals[0]))
    logging.info('proposal id: %s' % p_id)
    logging.info('proposal: %s transfer %s CYB to %s, %s transfer %s CYB to %s' % (account1, amount1/100000, account2, account2, amount2/100000, account1))
    
    instance.proposer = None 
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s proposal, %s balance cyb: %s' % (account1, account2, account2.balance('CYB')))

    # check proposal
    assert len(dict(account1.proposals[0])['required_active_approvals']) == 2
    assert len(dict(account1.proposals[0])['available_active_approvals']) == 0 
    assert account1.balance('CYB') == valu - fee
    assert account2.balance('CYB') == valu
    logging.info('this proposal has not been executed')

    # add account1 sign
    logging.info('%s accept the proposal' % (account1))
    instance.approveproposal([p_id], account=accountName1, approver=accountName1)
    account1.refresh()
    account2.refresh()
    assert len(dict(account1.proposals[0])['required_active_approvals']) == 2
    assert len(dict(account1.proposals[0])['available_active_approvals']) == 1 
    assert account1.balance('CYB') == valu - 2*fee
    assert account2.balance('CYB') == valu
    logging.info('after %s sign, %s balance cyb: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s sign, %s balance cyb: %s' % (account1, account2, account2.balance('CYB')))
    logging.info('this proposal is not executed yet')
    
    logging.info('%s dissapprove proposal' % (account1))
    instance.disapproveproposal([p_id], account=accountName1, approver=accountName1)
    account1.refresh()
    account2.refresh()
    logging.info('after %s disapprove proposal, %s balance: %s' % (account1, account1, account1.balance('CYB')))
    logging.info('after %s disapprove proposal, %s balance: %s' % (account1, account2, account2.balance('CYB')))
    
    logging.info('%s delete this proposal' % (account1))
    instance.proposal_delete(proposal_id=p_id, account=accountName1)

    # check account1 balance
    account1.refresh()
    account2.refresh()
    logging.info('%s balance: %s' % (account1, account1.balance('CYB')))
    logging.info('%s balance: %s' % (account2, account2.balance('CYB')))
    assert account2.balance('CYB') == valu 
    assert account1.balance('CYB') == valu -3*fee - 0.001

