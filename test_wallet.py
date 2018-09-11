from modules import *

def test_create(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    logging.info('test create wallet')
    if sys.platform == 'darwin':
        assert os.path.exists(os.path.join(os.environ['HOME'],'Library/Application Support/bitshares/'))
    else:
        assert os.path.exists(os.path.join(os.environ['HOME'],'.local/share/bitshares/bitshares.sqlite'))
    assert INSTANCE.wallet.created()

def test_getAccounts(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    logging.info('test get accounts from wallet')
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    before = len(INSTANCE.wallet.getAccounts())
    INSTANCE.wallet.addPrivateKey(activeKey)
    after = len(INSTANCE.wallet.getAccounts())
    assert after > before
    allAccounts = INSTANCE.wallet.getAccounts()
    check = False
    for element in allAccounts:
        if name == element['name']:
            check = True
            break
    assert check

def test_lock(INSTANCE, cleartxpool):
    logging.info('test lock wallet')
    INSTANCE.wallet.lock()
    assert INSTANCE.wallet.locked()
    
def test_unlock(INSTANCE, cleartxpool):
    logging.info('test unlock wallet')
    INSTANCE.wallet.unlock(INSTANCE.const['test_wallet_pwd'])
    assert not INSTANCE.wallet.locked()

def test_changePassphrase(INSTANCE, cleartxpool):
    logging.info('test change wallet phase')
    INSTANCE.wallet.unlock(INSTANCE.const['test_wallet_pwd'])
    INSTANCE.wallet.changePassphrase('654321')
    INSTANCE.wallet.lock()
    INSTANCE.wallet.unlock('654321')
    assert not INSTANCE.wallet.locked()
    INSTANCE.wallet.changePassphrase(INSTANCE.const['test_wallet_pwd'])
    
def test_getAccount(INSTANCE, cleartxpool):
    logging.info('test get account from wallet')
    reset_wallet(INSTANCE)
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    pubKey = account['active']['pub_key']
    acc = INSTANCE.wallet.getAccount(pubKey)
    assert isinstance(acc, dict)
    assert acc['name'] == name

def test_getActiveKeyForAccount(INSTANCE, cleartxpool):
    logging.info('test add private key')
    reset_wallet(INSTANCE)
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    assert INSTANCE.wallet.getActiveKeyForAccount(name) == activeKey

def test_getPrivateKeyForPublicKey(INSTANCE, cleartxpool):
    logging.info('test get private key from publick key')
    reset_wallet(INSTANCE)
    account = create_accounts(INSTANCE)[0]
    name = account['account']
    logging.info("account %s has been created", name)
    activeKey = account['active']['wif_priv_key']
    pubKey = account['active']['pub_key']
    INSTANCE.wallet.addPrivateKey(activeKey)
    assert INSTANCE.wallet.getPrivateKeyForPublicKey(pubKey) == activeKey


def test_encrypt_decrypt(INSTANCE, cleartxpool):
    logging.info('test decrypt')
    wif = '5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3'
    assert INSTANCE.wallet.decrypt_wif(INSTANCE.wallet.encrypt_wif(wif)) == wif
        