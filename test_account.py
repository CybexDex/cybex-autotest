# coding=utf-8
'''
Created on 2018-09-05
@author: andy
Project: 
'''
from modules import *
from bitshares.committee import Committee
from bitshares.vesting import Vesting

def test_get_public_key(INSTANCE, cleartxpool):
    ''' cybex_rte_026 #1 '''
    account = INSTANCE.const['master_account']
    pubKey = INSTANCE.const['master_pubkey']
    a = cybex.Account(account)
    assert a['active']['key_auths'][0][0] == pubKey

def test_createAccount(INSTANCE, cleartxpool):
    ''' cybex_rte_001 '''
    ts = time.time()
    name = 'test' + str(int(ts))
    logging.info("account %s will be created", name)
    assert create_account(INSTANCE, name)
    logging.info("account %s created success",name)
@pytest.mark.skip(reason="account history is not stable for rte")
def test_createAccountFee(INSTANCE, cleartxpool):
    ''' cybex_rte_001 '''
    ts = time.time()
    name = 'test' + str(int(ts))
    logging.info("The account %s will be created",name)
    acc = INSTANCE.const['master_account']
    before = cybex.Account(acc).balance('CYB')
    assert create_account(INSTANCE, name)
    after = cybex.Account(acc).balance('CYB')
    delta = (before - after).amount
    logging.info("The fee of creating account is %s",delta)
    time.sleep(60)
    history = get_latest_history(INSTANCE.const['master_account'])
    fee = history['op'][1]['fee']['amount']
    regName = history['op'][1]['name']
    assert name == regName
    assert delta*100000 == pytest.approx(fee, rel=0.1)

def test_updateActiveKey(INSTANCE, cleartxpool):
    ''' cybex_rte_002 '''
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    # key-pri pair
    pri = '5KiPyXzwfxdDXMb4Kchsb65hAsrshWEnbEuvQYK1QraZbhXfKWP'
    key = 'CYB8HuafNGYMaC1PTJypyEGKyo8Nf5z7XSYzspL68aRVMeof3rJNx'
    logging.info("account %s have been created", name)
    INSTANCE.transfer(name, 5, 'CYB', '', 'nathan')
    assert cybex.Account(name)['active']['key_auths'][0][0] != key
    before = cybex.Account(name).balance('CYB')
    update_active_key(INSTANCE, key, account=name)
    after = cybex.Account(name).balance('CYB')
    delta = before-after
    updateAccFee = INSTANCE.fee[6]['fee']['fee']/100000
    assert updateAccFee == pytest.approx(delta.amount, abs=1e-3)
    logging.info("update then compare active key test passed")
    assert cybex.Account(name)['active']['key_auths'][0][0] == key
    INSTANCE.wallet.addPrivateKey('5KiPyXzwfxdDXMb4Kchsb65hAsrshWEnbEuvQYK1QraZbhXfKWP')
    INSTANCE.transfer('nathan', 0.00001, 'CYB', '', name)

def test_updateMemoKey(INSTANCE, cleartxpool):
    ''' cybex_rte_002 '''
    reset_wallet(INSTANCE)
    account = create_accounts(INSTANCE)[0]
    # key-pri pair
    pri = '5JjUFX7LRgXmRKtnEjvZxv23yKMotQnXveKxF6TAX5nR59DPxmn'
    key = 'CYB8dpukfgAQRVPrADALovRnA6dj2b4izYnrHz4WCF1mK2aDr7aZv'
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    INSTANCE.transfer(name, 5, 'CYB', '', 'nathan')
    memo_key = key
    assert cybex.Account(name)['options']['memo_key'] != memo_key
    before = cybex.Account(name).balance('CYB')
    INSTANCE.update_memo_key(memo_key, cybex.Account(name))
    after = cybex.Account(name).balance('CYB')
    delta = before-after
    updateAccFee = INSTANCE.fee[6]['fee']['fee']/100000
    assert updateAccFee == pytest.approx(delta.amount, abs=1e-3)
    assert cybex.Account(name)['options']['memo_key'] == memo_key
    logging.info('transfer without memo pri key should work if user not input a memo')
    INSTANCE.transfer(INSTANCE.const['master_account'], 0.00001, 'CYB', '', name)
    try:
        logging.info('transfer with memo pri key should fail since there is no pri key in wallet')
        INSTANCE.transfer(INSTANCE.const['master_account'], 0.00001, 'CYB', 'a', name)
        assert 0
    except Exception as err:
        assert 'No private key' in str(err)
    INSTANCE.wallet.addPrivateKey(pri)
    INSTANCE.transfer(INSTANCE.const['master_account'], 0.00001, 'CYB', 'a', name)

def test_updateOwnerKey(INSTANCE, cleartxpool):
    ''' cybex_rte_002 '''
    reset_wallet(INSTANCE)
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    ownerKey = account['owner']['wif_priv_key']
    # need owner key to update an account's owner key
    INSTANCE.wallet.addPrivateKey(ownerKey)
    # key-pri pair
    pri = '5KiPyXzwfxdDXMb4Kchsb65hAsrshWEnbEuvQYK1QraZbhXfKWP'
    key = 'CYB8HuafNGYMaC1PTJypyEGKyo8Nf5z7XSYzspL68aRVMeof3rJNx'
    logging.info("account %s have been created", name)
    INSTANCE.transfer(name, 5, 'CYB', '', 'nathan')
    assert cybex.Account(name)['owner']['key_auths'][0][0] != key
    before = cybex.Account(name).balance('CYB')
    update_owner_keys(INSTANCE, key, account=name)
    after = cybex.Account(name).balance('CYB')
    delta = before-after
    updateAccFee = INSTANCE.fee[6]['fee']['fee']/100000
    assert updateAccFee == pytest.approx(delta.amount, abs=1e-3)
    logging.info("update then compare owner key test passed")
    assert cybex.Account(name)['owner']['key_auths'][0][0] == key
    reset_wallet(INSTANCE)
    INSTANCE.wallet.addPrivateKey(pri)
    INSTANCE.transfer(INSTANCE.const['master_account'], 0.00001, 'CYB', '', name)
    
def test_LTM(INSTANCE, cleartxpool):
    ''' cybex_rte_003 '''
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    assert not cybex.Account(name).is_ltm
    # minimum fee to upgrade to LTM 
    ltm_fee = INSTANCE.fee[8]['fee']['membership_lifetime_fee']/100000
    INSTANCE.transfer(name, ltm_fee, 'CYB', '', 'nathan')
    before = cybex.Account(name).balance('CYB')
    INSTANCE.upgrade_account(account=cybex.Account(name))
    after = cybex.Account(name).balance('CYB')
    delta = before-after
    assert cybex.Account(name).is_ltm
    assert ltm_fee == pytest.approx(delta.amount, abs=1e-3)

def test_LTM2(INSTANCE, cleartxpool):
    ''' cybex_rte_028 '''
    # account does not have enough CYB to upgrade to LTM
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    assert not cybex.Account(name).is_ltm
    try:
        INSTANCE.upgrade_account(account=cybex.Account(name))
    except Exception as err:
        assert 'Insufficient Balance' in str(err)
        INSTANCE.clear()
        
def test_MiltiSig(INSTANCE, cleartxpool):
    ''' cybex_rte_029 '''
    # create three new accounts, the first one is the multi-sig account
    accounts = create_accounts(INSTANCE, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0
    name1 = accounts[0]['account']
    name2 = accounts[1]['account']
    name3 = accounts[2]['account']
    logging.info("%s, %s, %s, three accounts has been created", name1, name2, name3)
    activeKey1 = accounts[0]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey1)
    obj = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],1]], 'key_auths': [], 'address_auths': []}
    logging.info("update %s to multi-sig account with threshold 2/3", name1)
    update_active_keys(INSTANCE, obj, account=name1)
    assert cybex.Account(name1).balance('CYB') == 0
    assert cybex.Account(name1)['active']['weight_threshold'] == 2
    
    amount = 10
    to_amount = 1
    create_proposal_fee = INSTANCE.fee[22]['fee']['fee']/100000
    update_proposal_fee = INSTANCE.fee[23]['fee']['fee']/100000
    transfer_fee = INSTANCE.fee[0]['fee']['fee']/100000

    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    
    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer %f CYB to init0", name1, to_amount)
    temp.transfer(INSTANCE.const['master_account'], to_amount, "CYB", account=name1)
    logging.info("create proposal fee %f", create_proposal_fee)
    assert cybex.Account(name1).balance('CYB').amount == pytest.approx(amount - create_proposal_fee, abs=0.1)
    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']
    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    INSTANCE.wallet.addPrivateKey(activeKey3)
        
    # approve propsal should cost fee
    logging.info("%s accept the propsal", name2)
    INSTANCE.approveproposal(id, appprover=name2, account=name2)
    assert cybex.Account(name2).balance('CYB').amount == pytest.approx(amount-update_proposal_fee, abs=0.1)
    logging.info("%s accept the propsal", name3)
    INSTANCE.approveproposal(id, appprover=name3, account=name3)
    assert cybex.Account(name3).balance('CYB').amount == pytest.approx(amount-update_proposal_fee, abs=0.1)
    # satisfy muti-sig, token transferred
    assert len(cybex.Account(name1).proposals) == 0
    assert cybex.Account(name1).balance('CYB').amount == pytest.approx(amount-create_proposal_fee-transfer_fee-9, abs=0.1)

def test_MiltiSigNotEnoughSign(INSTANCE, cleartxpool):
    # fail for no enough signer, 3/3
    # create three new accounts, the first one is the multi-sig account
    accounts = create_accounts(INSTANCE, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0
    name1 = accounts[0]['account']
    name2 = accounts[1]['account']
    name3 = accounts[2]['account']
    logging.info("%s, %s, %s, three accounts has been created", name1, name2, name3)
    activeKey1 = accounts[0]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey1)
    obj = {'weight_threshold': 3, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],1]], 'key_auths': [], 'address_auths': []}
    logging.info("update %s to multi-sig account with threshold 3/3", name1)
    update_active_keys(INSTANCE, obj, account=name1)
    assert cybex.Account(name1).balance('CYB') == 0
    assert cybex.Account(name1)['active']['weight_threshold'] == 3
    
    amount = 10
    to_amount = 1
    create_proposal_fee = INSTANCE.fee[22]['fee']['fee']/100000
    update_proposal_fee = INSTANCE.fee[23]['fee']['fee']/100000

    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.chain['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    
    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer %f CYB to %s", name1, to_amount, INSTANCE.chain['master_account'])
    temp.transfer(INSTANCE.chain['master_account'], to_amount, "CYB", account=name1)
    assert cybex.Account(name1).balance('CYB').amount == pytest.approx(amount - create_proposal_fee, abs=0.1)

    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']
    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    INSTANCE.wallet.addPrivateKey(activeKey3)
        
    # approve propsal should cost fee
    logging.info("%s accept the propsal", name2)
    INSTANCE.approveproposal(id, appprover=name2, account=name2)
    assert cybex.Account(name2).balance('CYB').amount == pytest.approx(amount-update_proposal_fee, abs=0.1)
    logging.info("%s accept the propsal", name3)
    INSTANCE.approveproposal(id, appprover=name3, account=name3)
    assert cybex.Account(name3).balance('CYB').amount == pytest.approx(amount-update_proposal_fee, abs=0.1)
    # satisfy muti-sig, token transferred
    assert len(cybex.Account(name1).proposals) == 1
    assert cybex.Account(name1).balance('CYB').amount == pytest.approx(amount-create_proposal_fee, abs=0.1)

def test_MultiSigDisApprove(INSTANCE, cleartxpool):
    # disapprove a multi-sig
    reset_wallet(INSTANCE)
    # create three new accounts, the first one is the multi-sig account
    accounts = create_accounts(INSTANCE, num=3)
    if accounts == False:
        logging.info('create account error')
        assert 0
    name1 = accounts[0]['account']
    name2 = accounts[1]['account']
    name3 = accounts[2]['account']
    logging.info("%s, %s, %s, three accounts has been created", name1, name2, name3)
    activeKey1 = accounts[0]['active']['wif_priv_key']
    ownerKey1 = accounts[0]['owner']['wif_priv_key']
    activeKey2 = accounts[1]['active']['wif_priv_key']
    activeKey3 = accounts[2]['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey1)
    obj = {'weight_threshold': 2, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],1]], 'key_auths': [], 'address_auths': []}
    logging.info("update %s to multi-sig account with threshold 2/3", name1)
    update_active_keys(INSTANCE, obj, account=name1)
    assert cybex.Account(name1).balance('CYB') == 0
    assert cybex.Account(name1)['active']['weight_threshold'] == 2
    
    amount = 10
    to_amount = 1
    create_proposal_fee = INSTANCE.fee[22]['fee']['fee']/100000
    update_proposal_fee = INSTANCE.fee[23]['fee']['fee']/100000
    delete_proposal_fee = INSTANCE.fee[24]['fee']['fee']/100000
    transfer_fee = INSTANCE.fee[0]['fee']['fee']/100000

    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])

    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer %f CYB to %s", name1, to_amount, INSTANCE.chain['master_account'])
    temp.transfer(INSTANCE.chain['master_account'], to_amount, "CYB", account=name1)
    assert cybex.Account(name1).balance('CYB').amount == pytest.approx(amount - create_proposal_fee, abs=0.1)
    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']

    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    # disapprove propsal should cost fee
    logging.info("%s approve propsal %s first", name2, id)
    assert cybex.Account(name2).balance('CYB').amount == amount
    INSTANCE.approveproposal(id, account=name2)
    assert cybex.Account(name2).balance('CYB').amount  == pytest.approx(amount - update_proposal_fee, abs=0.1)
    logging.info("%s remove previous approve propsal %s", name2, id)
    INSTANCE.disapproveproposal(id, account=name2)
    assert cybex.Account(name3).balance('CYB').amount == pytest.approx(amount-2*update_proposal_fee, abs=0.1)

def test_createCommittee(INSTANCE, cleartxpool):
    createdAccount = create_accounts(INSTANCE)[0]
    if createdAccount == False:
        logging.info('create account error')
        assert 0
    name = createdAccount['account']
    logging.info("account %s has been created", name)
    activeKey = createdAccount['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    account = cybex.Account(name)
    info = INSTANCE.rpc.get_committee_member_by_account(account["id"])
    logging.info("%s is not a committee member at first", name)
    assert info == None

    # fee to update an account to LTM
    ltm_fee = INSTANCE.fee[8]['fee']['membership_lifetime_fee']/100000
    # fee to create a committee
    committee_fee = INSTANCE.fee[29]['fee']['fee']/100000
    amount = ltm_fee+committee_fee

    INSTANCE.transfer(name, amount, 'CYB', '', 'nathan')
    assert cybex.Account(name).balance('CYB').amount == amount
    INSTANCE.upgrade_account(account=cybex.Account(name))
    assert cybex.Account(name).balance('CYB').amount == amount-ltm_fee
    logging.info("upgrade %s to committee member", name)
    INSTANCE.create_committee_member(account=name)
    assert cybex.Account(name).balance('CYB').amount == amount-ltm_fee-committee_fee
    info = INSTANCE.rpc.get_committee_member_by_account(account["id"])
    assert info != None      

def test_referrar(INSTANCE, cleartxpool):
    logging.info('referrar test start')
    reset_wallet(INSTANCE)
    acc = cybex.Account('nathan')
    before = INSTANCE.rpc.get_objects([cybex.Account('nathan')['cashback_vb']])[0]['balance']['amount']
    vesting_before = INSTANCE.rpc.get_objects([dict(acc)['statistics']])[0]['pending_vested_fees']

    createdAccount = create_accounts(INSTANCE)[0]
    if createdAccount == False:
        logging.info('create account error')
        assert 0
    name = createdAccount['account']
    logging.info("account %s has been created", name)
    activeKey = createdAccount['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    account = cybex.Account(name)
    # fee to update account to LTM
    amount = INSTANCE.fee[8]['fee']['membership_lifetime_fee']/100000
    INSTANCE.transfer(name, amount, 'CYB', '', 'nathan')
    INSTANCE.upgrade_account(account=account)

    after =INSTANCE.rpc.get_objects([cybex.Account('nathan')['cashback_vb']])[0]['balance']['amount']
    vesting_after = INSTANCE.rpc.get_objects([dict(acc)['statistics']])[0]['pending_vested_fees']
    logging.info('balance before %s - after %s, vesting before %s - after %s', before, after, vesting_before, vesting_after)
    assert int(after) > int(before) or int(vesting_after) > int(vesting_before)