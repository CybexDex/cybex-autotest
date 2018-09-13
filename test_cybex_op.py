from modules import *

def test_transfer_to_name_fail(INSTANCE, data4cybexop, cleartxpool):
    '''
        send a unexisted asset to transfer function, should raise exception.
    '''
    fro = data4cybexop['alice']
    to = data4cybexop['bob']
    ass = 'asdfa'
    value = round(random.random(),3)
    logging.info("transfer %d %s from %s to %s, should fail",value, ass, fro['account'], to['account'])
    with pytest.raises(Exception, match=r'.*asdfa.*') as info:
        INSTANCE.transfer(
            to['account'],
            value,
            ass,
            '',
            fro['account'],
            extensions = [[4, {
                'name': to['account'],
                'asset_sym': ass,
                'fee_asset_sym': 'CYB',
                'hw_cookie1': 100,
                'hw_cookie2': 200
            }]]
        )
    logging.info(info)
    
def test_transfer_to_name(INSTANCE, data4cybexop, cleartxpool):
    fro = data4cybexop['alice']
    to = data4cybexop['bob']
    ass = data4cybexop['asset1']
    value = round(random.random(),3)
    logging.info("transfer %f %s from %s to %s",value, ass, fro['account'], to['account'])
    assert transfer_to_name(INSTANCE, fro, to, ass, value)
    logging.info('Tx has been sent to chain, wait 10s ...')
    time.sleep(10)
    tx = get_latest_history(data4cybexop['bob']['account'])
    logging.info("tx:")
    logging.info(tx)
    assert tx['op'][1]['from'] == get_account_id(data4cybexop['alice']['account'])
    assert tx['op'][1]['to'] == get_account_id(data4cybexop['bob']['account'])
    assert int(tx['op'][1]['amount']['amount']) == int(value * 100000)
    assert tx['op'][1]['amount']['asset_id'] == cybex.Asset(ass)['id']

def test_claim_vesting_balance(INSTANCE, data4cybexop, cleartxpool):
    fro = data4cybexop['alice']
    to = data4cybexop['bob']
    ass = data4cybexop['asset1']
    value = random.randint(1,10)
    expire = 3

    fro_account = cybex.Account(fro['account'])
    to_account = cybex.Account(to['account'])
    vesting = to_account.vesting_balances
    balance_ahead = to_account.balance(ass)
    logging.info("transfer %d %s from %s to %s , lock time is %d", value, ass, fro['account'], to['account'], expire)
    assert transfer_vesting(INSTANCE, fro, to, ass, value, expire)
    logging.info("wait 5s for new block to ensure sequence")
    time.sleep(5)
    vesting_new = to_account.vesting_balances
    logging.info(vesting)
    logging.info(vesting_new)
    logging.info(balance_ahead)
    assert len(vesting_new) == len(vesting) + 1
    new_obj = [json.loads(x) for x in list(
            set([json.dumps(x) for x in vesting_new]) -
            set([json.dumps(x) for x in vesting]))][0]
    logging.info("wait 30s for lib")
    time.sleep(30)
    logging.info("claim the vesting balance")
    assert claim_balance(INSTANCE, data4cybexop['bob'], data4cybexop['asset1'], new_obj['id'], value)
    logging.info("wait 5s for new block to ensure sequence")
    time.sleep(5)
    balance_after = to_account.balance(ass)
    assert pytest.approx((balance_after - balance_ahead).amount) == value
    assert 'vesting_policy' in new_obj
    assert new_obj['sender'] == fro_account['id']
    assert new_obj['vesting_policy']['vesting_duration_seconds'] == expire
    assert new_obj['balance']['amount'] == value
    assert 'id' in new_obj



