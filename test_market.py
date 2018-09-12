from modules import *


def test_accountopenorders(INSTANCE, market, data4market, cleartxpool):
    
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])

    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    # buy 10 asset2 at price 1,
    # amount to sell (asset1, 10)
    # min to receive (asset2, 10)
    # expiration 3600
    m.buy(1, 10, 3600, killfill= False, account = alice)
    assert len(alice.openorders) == 1
    o = alice.openorders[0]
    base_asset = o['base']['asset']
    quote_asset = o['quote']['asset']
    assert o['base']['asset'].symbol == data4market['asset1']
    assert o['quote']['asset'].symbol == data4market['asset2']
    assert o['base']['amount'] == 10
    assert o['quote']['amount'] == 10

def test_fully_match(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])

    alice_asset1_balance_ahead = alice.balance(asset1)
    alice_asset2_balance_ahead = alice.balance(asset2)
    bob_asset1_balance_ahead = bob.balance(asset1)
    bob_asset2_balance_ahead = bob.balance(asset2)


    # buy 10 asset2 at price 100,
    # amount to sell (asset1, 1000)
    # min to receive (asset2, 10)
    # expiration 3600
    m.buy(100, 10, 3600, killfill = False, account = alice)

    time.sleep(5) # wait for block generation, to ensure order sequence

    # sell 10 asset2 at price 90,
    # amount to sell (asset2, 10)
    # min to receive (asset1, 900)
    # expiration 3600
    m.sell(90, 10, 3600, killfill = False, account = bob)
    time.sleep(5) # wait for block generation, to ensure order sequence

    # orders should be matched, at price 100
    # account1 will pay 1000 asset1, receive 10 asset2
    # account2 will pay 10 asset2, receive 1000 asset1
    assert len(alice.openorders) == 0
    assert len(bob.openorders) == 0

    ticker = m.ticker()
    logging.info(ticker['latest'])
    logging.info(type(ticker['latest']))
    assert ticker['latest'] == 100

    alice_asset1_balance_after = alice.balance(asset1)
    alice_asset2_balance_after = alice.balance(asset2)
    bob_asset1_balance_after = bob.balance(asset1)
    bob_asset2_balance_after = bob.balance(asset2)

    assert alice_asset1_balance_ahead - alice_asset1_balance_after == 1000
    assert alice_asset2_balance_after - alice_asset2_balance_ahead == 10
    assert bob_asset2_balance_ahead - bob_asset2_balance_after == 10
    assert bob_asset1_balance_after - bob_asset1_balance_ahead == 1000


def test_killfill_not_match(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])


    # buy 10 asset2 at price 100,
    # amount to sell (asset1, 1000)
    # min to receive (asset2, 10)
    # expiration 3600
    m.buy(100, 10, 3600, killfill = False, account = alice)

    # sell 9 asset2 at price 110
    # amount to sell (asset2, 9)
    # min to receive (asset1, 990)
    # expiration 3600
    # with pytest.raises(Exception) as info:
    #     m.sell(110, 9, 3600, True, bob)

    assert len(alice.openorders) == 1
    assert len(bob.openorders) == 0
    

def test_killfill(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])


    # buy 10 asset2 at price 100,
    # amount to sell (asset1, 1000)
    # min to receive (asset2, 10)
    # expiration 3600
    m.buy(100, 10, 3600, killfill = False, account = alice)

    # sell 9 asset2 at price 90
    # amount to sell (asset2, 9)
    # min to receive (asset1, 810)
    # expiration 3600
    m.sell(90, 9, 3600, killfill = True, account = bob)

    # orders should be matched, at price 100
    # account1 will pay 900 asset1, receive 9 asset2
    # account2 will pay 9 asset2, receive 900 asset1
    # order2 will be fully filled,
    # amount to sell left: 100
    assert len(alice.openorders) == 1
    assert len(bob.openorders) == 0

    # create another order like the previous one
    # killfill will except when it can not be fully filled
    with pytest.raises(Exception) as info:
        m.sell(90, 9, 3600, True, bob)

    # order1 will be left in order book
    assert len(alice.openorders) == 1

def test_partially_match(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])


    # buy 10 asset2 at price 100,
    # amount to sell (asset1, 1000)
    # min to receive (asset2, 10)
    # expiration 3600
    m.buy(100, 10, 3600, killfill = False, account = alice)

    # sell 20 asset2 at price 90
    # amount to sell (asset2, 20)
    # min to receive (asset1, 1800)
    # expiration 3600
    m.sell(90, 20, 3600, killfill = False, account = bob)

    # orders should be matched, at price 100
    # account1 will pay 1000 asset1, receive 10 asset2
    # account2 will pay 10 asset2, receive 1000 asset1
    # order2 will be partially filled,
    # amount to sell left: 10
    assert len(alice.openorders) == 0
    assert len(bob.openorders) == 1

def test_cull_small_order(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])

    # sell 1999.999 asset1 at price 1999.999
    # amount to sell (asset2, 1)
    # min to receive (asset2, 1)
    m.sell(1999.999, 1, 3600, killfill = False, account = bob)

    # to ensure order 1 applied first
    time.sleep(5)

    # buy 1 asset2 at price 2000
    # amount to sell (asset1, 2000)
    # min to receive (asset2, 1)
    m.buy(2000, 1, 3600, killfill = False, account = alice)

    # after matching
    # since usd_for_sale(2000) > core_for_sale(1) * match_price(1999.9999)
    # usd will receive core_for_sale(1)
    # core will receive core_for_sale(1) * match_price(1999.999) ->1999.999
    # usd will pay core receive, and core will pay usd receive

    # alice will leave an order with amount to sell(asset1, 0.001), at price 1:2000
    # min_to_receive will be 0.001 / 2000 = 0.0000005
    # min_to_receive will be less than precision
    # and will be culled

    time.sleep(5)
    assert len(alice.openorders) == 0
    assert len(bob.openorders) == 0
   
def test_market_history(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset(data4market['asset1'])
    asset2 = cybex.Asset(data4market['asset2'])
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    alice = cybex.Account(data4market['alice']['account'])
    bob = cybex.Account(data4market['bob']['account'])

    start = datetime.utcnow() - timedelta(seconds = 3600)
    end = datetime.utcnow()
    assert isinstance(
        m.get_market_history(60, start, end),
        list)
    start = datetime.utcnow().replace(
        hour = 0, minute = 0, second = 0)
    end = start + timedelta(seconds = 1)
    start = start - timedelta(seconds = 1)

    m.get_market_history(86400, start, end)

def test_fill_order_history(INSTANCE, market, data4market, cleartxpool):
    asset1 = cybex.Asset('CYB')   
    asset2 = cybex.Asset('JADE.ETH')
    m = cybex.Market(base = asset1, quote = asset2,
        cybex_instance = INSTANCE)
    m.get_fill_order_history(100)
