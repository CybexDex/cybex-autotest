import logging

logger = logging.getLogger('RTEOrder')

class RTEOrder(dict):
    order_book = {} # maps from rte_order_id to RTEOrder object
    chain_order_book = {} # maps from chain_order_id to RTEOrder object
    account_order_book = {} # maps from account_name to RTEOrder object list

    def __init__(self, d):
        super().__init__(d)
        self.order_book[d['order_id']] = self
        try:
            self.account_order_book[d['acct_id']].append(self)
        except:
            self.account_order_book[d['acct_id']] = [self]

        chid = int(d['chain_order_id'])
        if chid != -1:
            assert chid not in self.chain_order_book
            self.chain_order_book[chid] = self

    @property
    def status(self):
        return self['status']

    @status.setter
    def status(self, v):
        self['status'] = v

    @property
    def chain_order_id(self):
        return self['chain_order_id']

    @chain_order_id.setter
    def chain_order_id(self, i):
        assert self['chain_order_id'] == -1 or i == self['chain_order_id']
        self['chain_order_id'] = i
        self.chain_order_book[i] = self

    @property
    def psell(self):
        return self['psell']

    @psell.setter
    def psell(self, v):
        if v != self['psell']:
            logger.debug('psell of rte order {rte_id} changed from {old} to {new}'.format(
                rte_id = self['order_id'], old = self['psell'], new = v))
            self['psell'] = v

    @property
    def precv(self):
        return self['precv']

    @precv.setter
    def precv(self, v):
        if v != self['precv']:
            logger.debug('precv of rte order {rte_id} changed from {old} to {new}'.format(
                rte_id = self['order_id'], old = self['precv'], new = v))
            self['precv'] = v

    @property
    def chain_sell(self):
        return self['chain_sell']

    @chain_sell.setter
    def chain_sell(self, v):
        if v != self['chain_sell']:
            logger.debug('chain_sell of rte order {rte_id} changed from {old} to {new}'.format(
                rte_id = self['order_id'], old = self['chain_sell'], new = v))
            self['chain_sell'] = v

    @property
    def chain_recv(self):
        return self['chain_recv']

    @chain_recv.setter
    def chain_recv(self, v):
        if v != self['chain_recv']:
            logger.debug('chain_recv of rte order {rte_id} changed from {old} to {new}'.format(
                rte_id = self['order_id'], old = self['chain_recv'], new = v))
            self['chain_recv'] = v

    @property
    def trade_ids(self):
        return self['trade_ids']

    @trade_ids.setter
    def trade_ids(self, v):
        trade_ids = v.strip()[1:-1].split(' ') # eliminate '(' and ')'

        self['fill_orders'] = [self.order_book[int(i)] for i in trade_ids if i.isdigit() and int(i) in self.order_book]
        self['trade_ids'] = v

    @classmethod
    def get_order_by_account(cls, name):
        return cls.account_order_book.get(name, [])

    @classmethod
    def get_order_by_rte_order_id(cls, id):
        return cls.order_book.get(id, [])

    @classmethod
    def get_order_by_chain_order_id(cls, id):
        return cls.chain_order_book.get(id, [])
