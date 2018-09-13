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
    account = INSTANCE.const['master_account']
    pubKey = INSTANCE.const['master_pubkey']
    a = cybex.Account(account)
    assert a['active']['key_auths'][0][0] == pubKey

def test_createAccount(INSTANCE, cleartxpool):
        ts = time.time()
        name = 'test' + str(int(ts))
        logging.info("account %s will be created", name)
        assert create_account(INSTANCE, name)
        logging.info("account %s created success",name)

def test_createAccountFee(INSTANCE, cleartxpool):
    ts = time.time()
    name = 'test' + str(int(ts))
    logging.info("The account %s will be created",name)
    acc = INSTANCE.const['master_account']
    before = cybex.Account(acc).balance('CYB')
    assert create_account(INSTANCE, name)
    after = cybex.Account(acc).balance('CYB')
    delta = (before - after).amount
    logging.info("Waiting for 15s ,tx need to send to chain")
    time.sleep(15)
    logging.info("The fee of creating account is %s",delta)
    history = get_latest_history(INSTANCE.const['master_account'])
    fee = history['op'][1]['fee']['amount']
    regName = history['op'][1]['name']
    assert name == regName
    assert delta*100000 == pytest.approx(fee, rel=0.1)

def test_updateActiveKey(INSTANCE, cleartxpool):
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    key = 'CYB7PUaLmvY1Ee6YidhFBpDQ5x8kwDvgRFW1okytwVe4P7AD5oYVF'
    logging.info("account %s will be created", name)
    INSTANCE.transfer(name, 30, 'CYB', '', 'nathan')
    assert cybex.Account(name)['active']['key_auths'][0][0] != key
    update_active_key(INSTANCE, key, account=name)
    assert cybex.Account(name)['active']['key_auths'][0][0] == key
    logging.info("update then compare active key test passed")

def test_updateMemoKey(INSTANCE, cleartxpool):
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    INSTANCE.transfer(name, 30, 'CYB', '', 'nathan')
    memo_key = 'CYB5YNK2Ujxk8k7Ysbp8Pk67KX47uxcnnML2BqKGbn1NE8hPEmZXV'
    assert cybex.Account(name)['options']['memo_key'] != memo_key
    INSTANCE.update_memo_key(memo_key, cybex.Account(name))
    assert cybex.Account(name)['options']['memo_key'] == memo_key
    logging.info("update then compare memo key test passed")

def test_LTM(INSTANCE, cleartxpool):
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    assert not cybex.Account(name).is_ltm
    # minimum fee to upgrade to LTM 
    INSTANCE.transfer(name, 10000, 'CYB', '', 'nathan')
    INSTANCE.upgrade_account(account=cybex.Account(name))
    assert cybex.Account(name).is_ltm

def test_LTM2(INSTANCE, cleartxpool):
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
    reset_wallet(INSTANCE)
    # create three new accounts, the first one is the multi-sig account
    # pdb.set_trace()
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
    
    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    
    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer 9 CYB to init0", name1)
    temp.transfer('init0', 9, "CYB", account=name1)
    fee = INSTANCE.fee[0]['fee']['fee']/100000
    left = amount - fee
    assert cybex.Account(name1).balance('CYB') == left
    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']
    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    INSTANCE.wallet.addPrivateKey(activeKey3)
        
    # approve propsal should cost fee
    logging.info("%s accept the propsal", name2)
    INSTANCE.approveproposal(id, appprover=name2, account=name2)
    assert cybex.Account(name2).balance('CYB') == left
    logging.info("%s accept the propsal", name3)
    INSTANCE.approveproposal(id, appprover=name3, account=name3)
    assert cybex.Account(name3).balance('CYB') == left
    # satisfy muti-sig, token transferred
    assert len(cybex.Account(name1).proposals) == 0
    leftover = amount - 2*fee - 9
    assert cybex.Account(name1).balance('CYB') == leftover

def test_MiltiSigNotEnoughSign(INSTANCE, cleartxpool):
    # fail for no enough signer, 3/3
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
    obj = {'weight_threshold': 3, 'account_auths': [[cybex.Account(name1)['id'], 1],[cybex.Account(name2)['id'],1],[cybex.Account(name3)['id'],1]], 'key_auths': [], 'address_auths': []}
    logging.info("update %s to multi-sig account with threshold 3/3", name1)
    update_active_keys(INSTANCE, obj, account=name1)
    assert cybex.Account(name1).balance('CYB') == 0
    assert cybex.Account(name1)['active']['weight_threshold'] == 3
    
    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    
    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer 9 CYB to init0", name1)
    temp.transfer('init0', 9, "CYB", account=name1)
    fee = INSTANCE.fee[0]['fee']['fee']/100000
    left = amount - fee
    assert cybex.Account(name1).balance('CYB') == left
    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']
    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    INSTANCE.wallet.addPrivateKey(activeKey3)
        
    # approve propsal should cost fee
    logging.info("%s accept the propsal", name2)
    INSTANCE.approveproposal(id, appprover=name2, account=name2)
    assert cybex.Account(name2).balance('CYB') == left
    logging.info("%s accept the propsal", name3)
    INSTANCE.approveproposal(id, appprover=name3, account=name3)
    assert cybex.Account(name3).balance('CYB') == left
    # satisfy muti-sig, token transferred
    assert len(cybex.Account(name1).proposals) == 1
    assert cybex.Account(name1).balance('CYB') == left

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
    
    amount = 100
    INSTANCE.transfer(name1, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name2, amount, 'CYB', '', account='nathan')
    INSTANCE.transfer(name3, amount, 'CYB', '', account='nathan')
    temp = cybex.Cybex(node = INSTANCE.const['node_url'], proposer=name1)
    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if temp.wallet.locked():
        temp.wallet.unlock(CFG['wallet']['test_wallet_pwd'])

    # need private key to fire a multi-sig transanction
    INSTANCE.wallet.addPrivateKey(ownerKey1)
    logging.info("%s try to transfer 9 CYB to init0", name1)
    temp.transfer('init0', 9, "CYB", account=name1)
    fee = INSTANCE.fee[0]['fee']['fee']/100000
    left = amount - fee
    assert cybex.Account(name1).balance('CYB') == left
    # to do, remove a proposals
    id = cybex.Account(name1).proposals[0]['id']

    # need active key to approve a multi-sig
    INSTANCE.wallet.addPrivateKey(activeKey2)
    # disapprove propsal should cost fee
    logging.info("%s approve propsal %s first", name2, id)
    assert cybex.Account(name2).balance('CYB') == amount
    INSTANCE.approveproposal(id, account=name2)
    assert cybex.Account(name2).balance('CYB') == left
    logging.info("%s remove previous approve propsal %s", name2, id)
    INSTANCE.disapproveproposal(id, account=name2)
    leftover = amount - 2*fee
    assert cybex.Account(name2).balance('CYB') == leftover

def test_createCommittee(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
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

    amount = 15000
    INSTANCE.transfer(name, amount, 'CYB', '', 'nathan')
    assert cybex.Account(name).balance('CYB') == amount
    INSTANCE.upgrade_account(account=cybex.Account(name))
    # fee to update an account to LTM
    fee = INSTANCE.fee[8]['fee']['membership_lifetime_fee']/100000
    left = amount - fee
    assert cybex.Account(name).balance('CYB') == left
    logging.info("upgrade %s to committee member", name)
    INSTANCE.create_committee_member(account=name)
    # fee to create a committee
    fee2 = INSTANCE.fee[29]['fee']['fee']/100000
    leftover = amount - fee - fee2
    assert cybex.Account(name).balance('CYB') == leftover
    info = INSTANCE.rpc.get_committee_member_by_account(account["id"])
    assert info != None      

def test_referrar(INSTANCE, cleartxpool):
    before = Vesting('1.13.0', bitshares_instance=INSTANCE).claimable
    reset_wallet(INSTANCE)
    createdAccount = create_accounts(INSTANCE)[0]
    if createdAccount == False:
        logging.info('create account error')
        assert 0
    name = createdAccount['account']
    logging.info("account %s has been created", name)
    activeKey = createdAccount['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    account = cybex.Account(name)

    amount = 20000
    INSTANCE.transfer(name, amount, 'CYB', '', 'nathan')
    INSTANCE.upgrade_account(account=account)
    # fee to update an account to LTM
    fee = INSTANCE.fee[8]['fee']['membership_lifetime_fee']/100000
    left = amount - fee
    assert cybex.Account(name).balance('CYB') == left
    time.sleep(20)
    after = Vesting('1.13.0', bitshares_instance=INSTANCE).claimable
    assert after>before
