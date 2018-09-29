import logging
import pytest
import cybex
import sys
import shutil
from configparser import ConfigParser
import os
import time
import graphenebase
from bitsharesbase import operations
import random
import bitsharesbase.account as btsAccount
from datetime import datetime, timedelta
import json
import random
import warnings
import pdb

# name = time.strftime("%Y%m%d-%H%M%S",time.localtime(time.time()))
# LOG=logging.getLogger(name)

CFG = ConfigParser()
CFG.read("config.ini")




def suggest_brain_key():
    key = btsAccount.BrainKey()
    return {'brain_priv_key': key.get_brainkey(),
            'wif_priv_key': format(key.get_private_key(), 'WIF'),
            'pub_key': format(key.get_public_key(), 'CYB')
           } 

def gen_priv_key_wif(seed):
    passwd_key = btsAccount.PasswordKey(account = '', password = seed, role = '')
    return format(passwd_key.get_private(), 'WIF')

def wif_to_pub(wif):
    private_key = btsAccount.PrivateKey(wif, prefix = 'CYB')
    return format(private_key.pubkey, 'CYB')

def gen_key_pair(seed):
    wif = gen_priv_key_wif(seed)
    pub = wif_to_pub(wif)
    return (wif, pub)

def add_private_key(inst,accouts):
    inst.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    for k in accouts:
        try:
            inst.wallet.addPrivateKey(k)
            logging.info("add the private key:%s",k)
        except:
            pass

def remove_private_key(inst):
    for u in [TEST_ACCOUNT, TEST_ACCOUNT2]:
        try:
            inst.wallet.removeAccount(u)
        except:
            pass

def gen_private_key():
    pri = graphenebase.PrivateKey(prefix = 'CYB')
    pub = format(pri, 'CYB')
    return {'owner': str(pri), 'active': pub}

def create_account(inst, name, 
                    owner='CYB8fEEQ19N4LTVpg4wqX6B97ouDaNDDFK5fWbuaoNy4HPF9qnq4K',
                    active='CYB8fEEQ19N4LTVpg4wqX6B97ouDaNDDFK5fWbuaoNy4HPF9qnq4K'):
    '''
    create account using below keys:
    name - name
    owner - CYB8fEEQ19N4LTVpg4wqX6B97ouDaNDDFK5fWbuaoNy4HPF9qnq4K
    active - CYB8fEEQ19N4LTVpg4wqX6B97ouDaNDDFK5fWbuaoNy4HPF9qnq4K
    pri - 5HsGZoidEURBx8gYzwZMeM2eF8P3F9KC3nVAib2mdGSdj6FqS7h
    '''
    if inst.wallet.locked():
        inst.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    try:
        ## private key of nathan, which is the referrer
        inst.wallet.addPrivateKey(inst.const['master_privkey'])
    except Exception as e:
        pass
    
    toRegister = {
        'name': name,
        'owner': owner,
        'active': active
    }
    account = cybex.Account('nathan')
    owner_key_authority = [[toRegister["owner"], 1]]
    active_key_authority = [[toRegister["active"], 1]]
    owner_accounts_authority = []
    active_accounts_authority = []    
    kwargs = {
        'fee':{"amount": 100, "asset_id": "1.3.0"},
        'registrar':account["id"],
        'referrer':account["id"],
        'referrer_percent':1,
        'name':toRegister["name"],
        'owner': {'account_auths': owner_accounts_authority,
                    'key_auths': owner_key_authority,
                    "address_auths": [],
                    'weight_threshold': 1},
        'active': {'account_auths': active_accounts_authority,
                    'key_auths': active_key_authority,
                    "address_auths": [],
                    'weight_threshold': 1},
        "options": {"memo_key": toRegister["active"],
                    "voting_account": account["id"],
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": []
                    },
        "extensions": {},
        "prefix": "CYB"
    }
    op = operations.Account_create(**kwargs)
    ops=[]
    ops.append(op)
    inst.finalizeOp(ops, account, "active")
    return True

def create_buyback_account(name, asset, buyback_markets):
    """
    Only asset issuer can create a buyback account on that asset
    name: like 'abc-def'
    asset: like '1.3.2'
    buyback_markets: like ['1.3.3', '1.3.4']
    """
    if inst.wallet.locked():
        inst.wallet.unlock(TEST_WALLET_PWD)
    try:
        ## private key of nathan, which is the referrer
        inst.wallet.addPrivateKey(private)
    except Exception as e:
        pass
    
    account = cybex.Account('nathan')

    kwargs = {
        'fee':{"amount": 100, "asset_id": "1.3.0"},
        'registrar':account["id"],
        'referrer':account["id"],
        'referrer_percent':1,
        'name':name,
        'owner': {'account_auths': [['1.2.3', 1]],
                    'key_auths': [],
                    "address_auths": [],
                    'weight_threshold': 1},
        'active': {'account_auths': [['1.2.3', 1]],
                    'key_auths': [],
                    "address_auths": [],
                    'weight_threshold': 1},
        "options": {"memo_key": 'CYB8fEEQ19N4LTVpg4wqX6B97ouDaNDDFK5fWbuaoNy4HPF9qnq4K',
                    "voting_account": account["id"],
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": []
                    },
        "extensions": {'buyback_options': {'asset_to_buy': asset_id, 'asset_to_buy_issuer': account['id'], 'markets': buyback_markets}},
        "prefix": "CYB"
    }

    op = operations.Account_create(**kwargs)
    ops=[]
    ops.append(op)
    inst.finalizeOp(ops, account, "active")
    return True
    
def get_latest_history(acc):
    return next(cybex.Account(acc).history(limit=1))

def update_active_key(inst, key, account=None, **kwargs):
    btsAccount.PublicKey(key, prefix='CYB')
    account = cybex.Account(account)
    account["active"] = {'weight_threshold': 1, 'account_auths': [], 'key_auths': [[key, 1]], 'address_auths': []}
    op = operations.Account_update(**{
        "fee": {"amount": 0, "asset_id": "1.3.0"},
        "account": account["id"],
        "active": account["active"],
        "extensions": {}
    })
    return inst.finalizeOp(op, account["name"], "active", **kwargs)

def update_owner_key(inst, key, account=None, **kwargs):
    btsAccount.PublicKey(key, prefix='CYB')
    account = cybex.Account(account)
    account["owner"] = {'weight_threshold': 1, 'account_auths': [], 'key_auths': [[key, 1]], 'address_auths': []}
    op = operations.Account_update(**{
        "fee": {"amount": 0, "asset_id": "1.3.0"},
        "account": account["id"],
        "owner": account["owner"],
        "extensions": {}
    })
    return inst.finalizeOp(op, account["name"], "active", **kwargs)

def update_owner_keys(inst, obj, account=None, **kwargs):
    # for testing multi-Sig
    # need fee to update active keys
    fee = inst.fee[6]['fee']['fee']/100000
    inst.transfer(account, fee, 'CYB', '', 'nathan')
    account = cybex.Account(account)
    account["active"] = obj
    op = operations.Account_update(**{
        "fee": {"amount": 0, "asset_id": "1.3.0"},
        "account": account["id"],
        "owner": account["active"],
        "extensions": {}
    })
    return inst.finalizeOp(op, account["name"], "active", **kwargs)

def update_active_keys(inst, obj, account=None, **kwargs):
    # for testing multi-Sig
    # need fee to update active keys
    fee = inst.fee[6]['fee']['fee']/100000
    inst.transfer(account, fee, 'CYB', '', 'nathan')
    account = cybex.Account(account)
    account["active"] = obj
    op = operations.Account_update(**{
        "fee": {"amount": 0, "asset_id": "1.3.0"},
        "account": account["id"],
        "active": account["active"],
        "extensions": {}
    })
    return inst.finalizeOp(op, account["name"], "active", **kwargs)

def reset_wallet(inst):
    inst.wallet.unlock(CFG['wallet']['test_wallet_pwd'])
    for acc in inst.wallet.getAccounts():
        inst.wallet.removeAccount(acc['name'])
    # add master account key
    inst.wallet.addPrivateKey(inst.chain['master_privkey'])

def genSymbol():
    code = ''
    for i in range(8):
        add = random.choice([chr(random.randrange(65, 91))])
        code += str(add)
    return code

def update_assetSupply(inst, symbol, max_supply):
    asset = cybex.Asset(symbol)
    options = asset['options']
    account = cybex.Account(inst.const['master_account'])
    options.update({
            "max_supply": max_supply
        })
    op = operations.Asset_update(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "issuer": account["id"],
            "asset_to_update": asset["id"],
            "new_options": options,
            "extensions": [],
            "prefix": inst.prefix
        })
    return inst.finalizeOp(op, account["name"], "active")

def failrun(times=3,wait_time=1):
    def decorator(func):
        def wrapper(*args,**kw):
            for i in range(times):
                try:
                    r=func(*args,**kw)
                    return r
                except AssertionError as err:
                    print('用例第一次失败原因:%s'%err)
                    time.sleep(wait_time)
            raise AssertionError
        return wrapper
    return decorator

def get_fee(inst, op=None):
    fees = inst.rpc.get_global_properties([])['parameters']['current_fees']['parameters']
    ops = cybex.cybex.intercept_bitshares.cybex_ops
    out = [{'id': fees[i][0], 'op': ops[i], 'fee': fees[i][1]} for i in range(len(fees))]
    if op == None:
        return out
    elif isinstance(op, int):
        return out[op]
    elif isinstance(op, str):
        index = ops.index(op)
        return out[index]
    else:
        raise Exception('invalid input') 

def create_accounts(inst, num=1):
    out = []
    for i in range(num):
        ts = time.time()
        active = suggest_brain_key()
        owner = suggest_brain_key()
        account = 'test' + str(int(ts))
        try:
            create_account(inst, account, owner=owner['pub_key'], active=active['pub_key'])
        except Exception as err:
            logging.error('create account error ,because %s', err)
            return False
        out.append({'account': account, 'owner': owner, 'active': active})
    if len(out) > 0:
        fid = open('accounts.csv', 'a')
        for i in range(len(out)):
            line = out[i]['account']+','+out[i]['owner']['wif_priv_key']+','+out[i]['owner']['pub_key']+','+out[i]['owner']['brain_priv_key']+','+out[i]['active']['wif_priv_key']+','+out[i]['active']['pub_key']+','+out[i]['active']['brain_priv_key']+',\n'
            fid.write(line)
        fid.close()
    else:
        raise Exception("create account failed")
    return out

def create_asset(inst, precision=5, max_supply=100000000, core_exchange_rate=2000):
    symbol = genSymbol()
    try:
        inst.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, 'description', account='nathan')
    except Exception as err:
        logging.error("failed to create asset,because %s",err)
        return False
    return symbol

def issue_CYB(inst, name, amount):
    inst.transfer(name, amount, 'CYB', '', inst.const['master_account'])

def transfer_asset(inst, name, amount, asset):
    inst.transfer(name, amount, asset, '', inst.const['master_account'])

def issue_asset(inst, symbol, max_supply=100000000):
    inst.issue_asset('nathan', max_supply, symbol, account='nathan')

def get_account_id(acc):
    a = cybex.Account(acc)
    return a['id']


def claim_balance(INSTANCE, acc, asset_sym, bal_id, value):
    try:
        ret = INSTANCE.balance_claim(
                acc['account'],
                bal_id,
                acc['active']['pub_key'],
                value,
                asset_sym)
    except Exception as err:
        logging.warning(err)
        return False
    return True

def cancel_vesting(INSTANCE, id, acc):
    try:
        INSTANCE.cancel_vesting(id, acc['account'])
    except Exception as err:
        logging.warning(err)
        return False
    return True


def transfer_to_name(INSTANCE, from_acc, to_acc, asset_sym, value):
    activeKey = from_acc['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    # assert 0
    try:
        INSTANCE.transfer(
            to_acc['account'],
            value,
            asset_sym,
            '',
            from_acc['account'],
            extensions = [[4, {
                'name': to_acc['account'],
                'asset_sym': asset_sym,
                'fee_asset_sym': 'CYB',
                'hw_cookie1': 100,
                'hw_cookie2': 200
            }]]
        )
    except Exception as err:
        logging.warning(err)
        return False
    return True


def transfer_vesting(INSTANCE,from_acc, to_acc, asset_sym, value, expire = 600):
    try:
        ret = INSTANCE.transfer(
                to_acc['account'], value, asset_sym, '', from_acc['account'],
                extensions = [[1, {
                    'vesting_period': expire,
                    'public_key': to_acc['active']['pub_key']
                }]]
        )
    except Exception as err:
        logging.warning(err)
        return False
    return True



'''
{
    'alice': {
        'account': 'test1536379490',
        'owner': {
            'brain_priv_key': 'RONYONBRAINERCHASMALVISITEMANDYASPONDLETPROSISHBIBIRISANDHIBATTUECHIRPSPOREDCUPROIDCHARISMSKIPPETPRABBLE',
            'wif_priv_key': '5JMtr5dDwzyGC758FvJx2eegdLgX6N17SLnkVs8avZYbZoYmXKj',
            'pub_key': 'CYB6HZdWtzMxn6qJ2y5VVtaWaGZEz7uZvnJpPz7sru2zu612pBMbf'
        },
        'active': {
            'brain_priv_key': 'CASKWOEBREBAREVISALWOOHOOELEIDINASSURELOMBARDJENNIERWIZENEDAZIOLACYESISUNARMDINMONTSPOORMINE',
            'wif_priv_key': '5JPSp7NNxKLnrbHy98YbGQDXRkzfGYtYNCuxnfbYbwRtaUhfrCd',
            'pub_key': 'CYB6qej4oED7Kb3dAaixpTDnaVv3xRyL29XUBa9wxMmtVtN7kv7fd'
        }
    },
    'bob': {
        'account': 'test1536379494',
        'owner': {
            'brain_priv_key': 'FERVORCEDRINEPODALSCAMPVACCARYCRUMBACARIANREDBILLTOWNLYMASSEARCHESCUTULASADLYCHKALIKJOURNALJHOW',
            'wif_priv_key': '5K2r7Sxv7JffZ3E26QGMRuCPz1BdRTEPQzAsoHiofa96WvJjVPK',
            'pub_key': 'CYB7V7VivoXVa4Lc2cvMrCfEpJ1cx1AHqSQGUdpAArKd1N7k6aY1x'
        },
        'active': {
            'brain_priv_key': 'TRAPPYCRANLODGERCUDGELPHOTICSPADLOCKNEFTGILARSOITEMIASMICTREEDVENCOLAGUAYULEVARVEDSIFAKAFOGONFLANKED',
            'wif_priv_key': '5JAHE5Lygrjae6mwDfSFyG7UwJpRx7L4KSrkfoF4HkPYd4WWqvP',
            'pub_key': 'CYB6V1tE6u9s3NAJ2jfc6cM4kZcyn7VA2dqifi5MwHPJgzfKNPPh3'
        }
    },
    'asset1': 'IDTGQFIM',
    'asset2': 'CTWEWWFP'
}

'''
def create_data(INSTANCE):
    data = {}
    
    acc = create_accounts(INSTANCE)
    assert acc
    if acc :
        data['alice'] = acc[0]
    acc = create_accounts(INSTANCE)
    assert acc
    if acc :
        data['bob'] = acc[0]
    # data['bob'] = create_accounts(INSTANCE)[0]
    logging.info("Create account for alice and bob")
    data['asset1'] = create_asset(INSTANCE)
    data['asset2'] = create_asset(INSTANCE)
    assert data['asset1']
    assert data['asset2']
    logging.info("Create 2 asset")
    logging.info(data)
    issue_asset(INSTANCE, data['asset1'])
    issue_asset(INSTANCE, data['asset2'])
    logging.info("issue the 2 assets")
    transfer_asset(INSTANCE, data['alice']['account'], 10000000, data['asset1'])
    transfer_asset(INSTANCE, data['bob']['account'], 10000000, data['asset2'])
    logging.info("transfer 1000000 of %s to alice and 1000000 of %s to bob", data['asset1'], data['asset2'])
    issue_CYB(INSTANCE, data['alice']['account'], 1)
    issue_CYB(INSTANCE, data['bob']['account'], 1)
    logging.info("transfer 1 CYB to the 2 accounts for fee")
    # add_private_key(INSTANCE,[data['alice']['active']['wif_priv_key'],data['alice']['active']['wif_priv_key']])
    # logging.info("add private key in wallet for alice and bob")
    return data

def debug_data():
    data = {
        'alice': {
            'account': 'pytest1',
            'active': {
                'wif_priv_key': '5JjquvRzzidUYmANw7WoJrTpX6JUwfjRebTAfdy7bB6XoLSxaNJ',
                'pub_key': 'CYB8A5SAWzHE4yLKmfzaFdMRh7K521sVqeF5hkukmUkuB865SoX7x'
            },
            'owner': {
                'wif_priv_key': '5JcPZR82XycbPY5SHk7qNAqRS51PHwQuL9TSFNuoT6RoS9ZLshe',
                'pub_key': 'CYB6DV5FJPYpUVeHn1JqkC5aGbFpjUQ68jnCD7TVAQkBc5XiiXd9B'
            }
        },
        'bob': {
            'account': 'pytest3',
            'active': {
                'wif_priv_key': '5K2Cyq6NSdZgHFv8Ri9ZhxwQoPBhPzzBiutrT2bzzCiHyZ2F7eZ',
                'pub_key': 'CYB7sMaFFkxbPmjsCv62gwHPkCPXSryNrQofkfP1Ri2q2zLAi6rrA'
            },
            'owner': {
                'wif_priv_key': '5JosC24ohfyEc5jzUUJy1GNYa4HpRLxa4HtYcZDpLmCdLWZRaNE',
                'pub_key': 'CYB7gV9M2DeNz66tsuW9K4cBR2vjgwwuBBVsXCsLMBk41mUvAuySH'
            }
        },
        'asset1': 'PYTHONA',
        'asset2': 'PYTHONB'
    }
    data2 = {
        'alice': {
            'account': 'test1536379490',
            'owner': {
                'brain_priv_key': 'RONYONBRAINERCHASMALVISITEMANDYASPONDLETPROSISHBIBIRISANDHIBATTUECHIRPSPOREDCUPROIDCHARISMSKIPPETPRABBLE',
                'wif_priv_key': '5JMtr5dDwzyGC758FvJx2eegdLgX6N17SLnkVs8avZYbZoYmXKj',
                'pub_key': 'CYB6HZdWtzMxn6qJ2y5VVtaWaGZEz7uZvnJpPz7sru2zu612pBMbf'
            },
            'active': {
                'brain_priv_key': 'CASKWOEBREBAREVISALWOOHOOELEIDINASSURELOMBARDJENNIERWIZENEDAZIOLACYESISUNARMDINMONTSPOORMINE',
                'wif_priv_key': '5JPSp7NNxKLnrbHy98YbGQDXRkzfGYtYNCuxnfbYbwRtaUhfrCd',
                'pub_key': 'CYB6qej4oED7Kb3dAaixpTDnaVv3xRyL29XUBa9wxMmtVtN7kv7fd'
            }
        },
        'bob': {
            'account': 'test1536379494',
            'owner': {
                'brain_priv_key': 'FERVORCEDRINEPODALSCAMPVACCARYCRUMBACARIANREDBILLTOWNLYMASSEARCHESCUTULASADLYCHKALIKJOURNALJHOW',
                'wif_priv_key': '5K2r7Sxv7JffZ3E26QGMRuCPz1BdRTEPQzAsoHiofa96WvJjVPK',
                'pub_key': 'CYB7V7VivoXVa4Lc2cvMrCfEpJ1cx1AHqSQGUdpAArKd1N7k6aY1x'
            },
            'active': {
                'brain_priv_key': 'TRAPPYCRANLODGERCUDGELPHOTICSPADLOCKNEFTGILARSOITEMIASMICTREEDVENCOLAGUAYULEVARVEDSIFAKAFOGONFLANKED',
                'wif_priv_key': '5JAHE5Lygrjae6mwDfSFyG7UwJpRx7L4KSrkfoF4HkPYd4WWqvP',
                'pub_key': 'CYB6V1tE6u9s3NAJ2jfc6cM4kZcyn7VA2dqifi5MwHPJgzfKNPPh3'
            }
        },
        'asset1': 'IDTGQFIM',
        'asset2': 'CTWEWWFP'
    }
    return data2

def cancel_all(INSTANCE, accs):
    try:
        for acc in accs:
            for o in cybex.Account(acc, cybex_instance=INSTANCE).openorders:
                m = cybex.Market(
                    base = o['base']['asset'],
                    quote = o['quote']['asset'],
                    cybex_instance = INSTANCE)
                logging.info('Cancel the orders of the account')
                logging.info(dict(o))
                logging.info(o['id'])
                logging.info(acc)
                INSTANCE.clear()
                m.cancel(o['id'], acc)
                logging.info("cancel finished")
    except Exception as err:
        logging.info(err)
        return False
    return True


def assert4rte(inst, exp, errinfo="[default]assert result is false"):
    if inst.notcheckrte:
        return "in the mode of not check rte"
    else:
        try:
            assert exp, errinfo
            return True
        except Exception as err:
            logging.info(err)
            return False