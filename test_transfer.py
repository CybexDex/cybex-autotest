from modules import *
# from util import create_accounts

def test_transfer(INSTANCE, cleartxpool):
    logging.info('transfer test start')
    value = 1
    # create a new account
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)

    acc = INSTANCE.const['master_account']
    logging.info('get master account %s', acc)
    before = cybex.Account(acc).balance('CYB')
    logging.info('account %s got %s before transfer', acc, before)
    logging.info('transfer 1 CYB from %s to %s', acc, name)
    INSTANCE.transfer(name, value, 'CYB', '', acc)
    after = cybex.Account(acc).balance('CYB')
    delta = (before - after).amount*100000
    time.sleep(15)
    history = get_latest_history(name)
    caculated = history['op'][1]['fee']['amount']
    desired = INSTANCE.fee[0]['fee']['fee']
    assert caculated == desired

def test_transferWithNoKey(INSTANCE, cleartxpool):
    logging.info('transfer with no active key')
    reset_wallet(INSTANCE)
    # create a new account
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    assert cybex.Account(name).balance('CYB') == 0
    try:
        # below line will result in an error since there is no active key in wallet
        INSTANCE.transfer('nathan', 1, 'CYB', '', name)
        # cannot track error here (err=null), dirty workaround
        assert 0
    except Exception as err:
        pass

def test_transferWithNoBalance(INSTANCE, cleartxpool):
    logging.info('transfer with no balance')
    reset_wallet(INSTANCE)
    # create a new account
    account = create_accounts(INSTANCE)[0]
    if account == False:
        logging.info('create account failed')
        assert 0
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    try:
        INSTANCE.transfer('nathan', 1, 'CYB', '', name)
    except Exception as err:
        assert 'Insufficient Balance' in str(err)
    try:
        INSTANCE.transfer('NOACCOUNT', 1, 'CYB', '', name)
    except Exception as err:
        assert 'NOACCOUNT' in str(err)
