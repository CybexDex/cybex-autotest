from modules import *

def pytest_addoption(parser): 
    parser.addoption("--chain", action="store",default="dextestchain",help="option to specify chain")
    parser.addoption("--notcheckrte", action="store_true",help="option to disable the assert for rte")

@pytest.fixture(scope='session')
def INSTANCE(pytestconfig):
    chainName = pytestconfig.getoption('chain')
    chainId = CFG[chainName]['chain_id']
    chainNodeUrl = CFG[chainName]['node_url']
    if chainId != '90be01e82b981c8f201c9a78a3d31f655743b29ff3274727b1439b093d04aa23':
        cybex.cybex.cybex_debug_config(chainId)
    instance = cybex.cybex.Cybex(node = chainNodeUrl)
    instance.const = dict(CFG[chainName])
    instance.chain = dict(CFG[chainName])
    instance.notcheckrte = pytestconfig.getoption('notcheckrte')
    fees = instance.rpc.get_global_properties([])['parameters']['current_fees']['parameters']
    ops = cybex.cybex.intercept_bitshares.cybex_ops
    instance.fee = [{'id': fees[i][0], 'op': ops[i], 'fee': fees[i][1]} for i in range(len(fees))]
    logging.info(instance.const)
    return instance

@pytest.fixture(autouse=True, scope='session')
def initialize(INSTANCE):
    # if INSTANCE.const['chain_id'] != '90be01e82b981c8f201c9a78a3d31f655743b29ff3274727b1439b093d04aa23':
    #    cybex.cybex.cybex_debug_config(INSTANCE.const['chain_id'])
    if sys.platform == 'darwin':
        sqlite_path = os.path.join(os.environ['HOME'], 'Library/Application Support/bitshares/')
    else:
        sqlite_path = os.path.join(os.environ['HOME'], '.local/share/bitshares/')

    def backup_wallet():
        """ constructing a wallet will backup old wallet sqlite file
        """
        if os.path.exists(sqlite_path):
            backup_path = os.path.join(os.getcwd(), '.backup')
            try:
                os.remove(os.path.join(backup_path, 'bitshares.sqlite'))
                shutil.move(os.path.join(sqlite_path, 'bitshares.sqlite'),
                            backup_path)
            except:
                pass

    def restore_wallet():
        """ Restore wallet sqlite file from tmp directory
        """
        try:
            os.remove(os.path.join(sqlite_path, 'bitshares.sqlite'))
        except:
            pass

        backup_path = os.path.join(os.getcwd(), '.backup')
        if os.path.exists(os.path.join(backup_path, 'bitshares.sqlite')):
            shutil.move(
                    os.path.join(
                        backup_path, 'bitshares.sqlite'),
                    sqlite_path)
    backup_wallet()
    if not INSTANCE.wallet.created():
        INSTANCE.wallet.create(CFG['wallet']['test_wallet_pwd'])
    if INSTANCE.wallet.locked():
        INSTANCE.wallet.unlock(CFG['wallet']['test_wallet_pwd'])    
    yield
    restore_wallet()

@pytest.fixture(scope='function')
def market(INSTANCE, data4market):
    cancel_all(INSTANCE, [data4market['alice']['account'], data4market['bob']['account']])
    yield
    cancel_all(INSTANCE, [data4market['alice']['account'], data4market['bob']['account']])


@pytest.fixture(scope='module')
def data4market(INSTANCE):
    # logging.info(debug_data())
    data = create_data(INSTANCE)
    # data = debug_data()
    add_private_key(INSTANCE,[data['alice']['active']['wif_priv_key'],data['bob']['active']['wif_priv_key']])
    logging.info("add private key in wallet for alice and bob")
    return data


@pytest.fixture(scope='module')
def data4cybexop(INSTANCE):
    # logging.info(debug_data())
    data = create_data(INSTANCE)
    # data = debug_data()
    add_private_key(INSTANCE,[data['alice']['active']['wif_priv_key'],data['bob']['active']['wif_priv_key']])
    logging.info("add private key in wallet for alice and bob")
    return data

@pytest.fixture(scope='function')
def cleartxpool(INSTANCE):
    INSTANCE.clear()
    yield
    INSTANCE.clear()
