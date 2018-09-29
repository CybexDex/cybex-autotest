from modules import *
from bitshares.amount import Amount

def test_precision(INSTANCE, cleartxpool):
    assert cybex.Asset('CYB').precision == 5

def test_flags(INSTANCE, cleartxpool):
    assert cybex.Asset('CYB').flags != None

def test_createAsset(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    symbol = genSymbol()
    precision = 5
    max_supply = 100000000
    core_exchange_rate = 2000
    # create asset
    logging.info("create asset %s", symbol)
    INSTANCE.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, 'description', account='nathan')
    assert cybex.Asset(symbol)['symbol'] == symbol
    assert cybex.Asset(symbol)['precision'] == precision
    assert cybex.Asset(symbol)['issuer'] == cybex.Account('nathan')['id']
    assert cybex.Asset(symbol)['options']['issuer_permissions'] == 79
    assert cybex.Asset(symbol)['options']['max_supply'] == str(int(max_supply*1e5))
    assert cybex.Asset(symbol)['options']['core_exchange_rate']['base']['amount'] == int(core_exchange_rate*1e5)
    # issue asset
    INSTANCE.issue_asset('nathan', max_supply, symbol, account='nathan')
    assert cybex.Account('nathan').balance(symbol) == max_supply
    # do a transfer
    INSTANCE.transfer('null-account', 1, symbol, '', 'nathan')
    assert cybex.Account('null-account').balance(symbol) == 1
    # check fee
    dynamic_asset_data_id = cybex.Asset(symbol)['dynamic_asset_data_id']
    pool = INSTANCE.rpc.get_objects([dynamic_asset_data_id])[0]
    assert pool['accumulated_fees'] == 0
    # assert pool['fee_pool'] == 50000000

def test_updateAsset(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    symbol = genSymbol()
    precision = 5
    max_supply = 100000000
    core_exchange_rate = 2000
    # create asset
    logging.info("create asset %s", symbol)
    INSTANCE.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, 'description', account='nathan')
    new_max_supply = 10000
    update_assetSupply(INSTANCE, symbol, new_max_supply)
    assert cybex.Asset(symbol)['options']['max_supply'] == new_max_supply

def test_burnAsset(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    symbol = genSymbol()
    precision = 1
    max_supply = 100
    core_exchange_rate = 2000
    # create asset
    logging.info("create asset %s", symbol)
    INSTANCE.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, 'description', account='nathan')
    INSTANCE.issue_asset('nathan', max_supply, symbol, account='nathan')
    dynamic_asset_data_id = cybex.Asset(symbol)['dynamic_asset_data_id']
    current_supply1 = INSTANCE.rpc.get_objects([dynamic_asset_data_id])[0]['current_supply']
    INSTANCE.reserve(Amount(amount=1, asset=symbol), account='nathan')
    current_supply2 = INSTANCE.rpc.get_objects([dynamic_asset_data_id])[0]['current_supply']
    assert current_supply1/10 == current_supply2/10+1

def test_haltAsset(INSTANCE, cleartxpool):
    reset_wallet(INSTANCE)
    symbol = genSymbol()
    precision = 1
    max_supply = 100
    core_exchange_rate = 2000
    # create asset
    logging.info('burn asset test')
    logging.info("create asset %s", symbol)
    INSTANCE.create_asset(symbol, precision, max_supply, {symbol: 1, 'CYB': core_exchange_rate}, 'description', account='nathan')
    INSTANCE.issue_asset('nathan', max_supply, symbol, account='nathan')
    assert cybex.Account('nathan').balance(symbol) == max_supply
    INSTANCE.transfer('null-account', 1, symbol, '', 'nathan')
    assert cybex.Account('nathan').balance(symbol) == max_supply-1
    cybex.Asset(symbol, cybex_instance=INSTANCE).halt()
    try:
        INSTANCE.transfer('null-account', 2, symbol, '', 'nathan')
    except Exception as err:
        assert 'is not whitelisted' in str(err)