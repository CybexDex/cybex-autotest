import time
import threading
import socket
from rte_order import *

class RTEEndpoint(object):

    order_book_thread = {} # static

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        if len(self.order_book_thread) == 0:
            self.order_book_thread['t'] = threading.Thread(target = self.__fetch_order_book_loop)
            self.order_book_thread['t'].daemon = True
            self.order_book_thread['t'].start()
        self._th = self.order_book_thread['t']

    def __fetch_order_book_loop(self):
        current_order_id = -1
        while True:
            result = self.get_cmd_result('dump -t order -l 100')
            result = sorted(result, key = lambda x: int(x[0]))
            new_order_cnt = 0
            for x in result:
                rte_id = int(x[0])
                order = RTEOrder.get_order_by_rte_order_id(rte_id)
                if not order:
                    assert rte_id > current_order_id
                    RTEOrder({
                        'order_id': rte_id,
                        'sell_asset_id': x[2].strip(),
                        'recv_asset_id': x[3].strip(),
                        'sell_qty': int(x[4]),
                        'recv_qty': int(x[5]),
                        'status': x[6].strip(),
                        'acct_id': x[7].strip(),
                        'psell': int(x[8]),
                        'precv': int(x[9]),
                        'chain_sell': int(x[10]),
                        'chain_recv': int(x[11]),
                        'chain_order_id': int(x[12]),
                        'trx_id': x[13].strip(),
                        'trade_ids': x[14].strip()
                    })
                    new_order_cnt += 1
                    current_order_id = rte_id
                else:
                    order.status = x[6].strip()
                    order.chain_order_id = int(x[12])
                    order.psell = int(x[8])
                    order.precv = int(x[9])
                    order.chain_sell = int(x[10])
                    order.chain_recv = int(x[11])
                    order.trade_ids = x[14].strip()
            print('{} new orders found'.format(new_order_cnt))
            time.sleep(1)

    def get_cmd_result(self, command):
        result = []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._ip, self._port))
            s.sendall(command.encode())

            for line in s.makefile('r'):
                if line == "EOF\n":
                    break;
                result.append(line)
        return [l.strip().split(',') for l in result[4:-2]]

    def get_account_open_orders(self, name):
        account_orders = RTEOrder.get_order_by_account(name)
        return list(filter(lambda x:x.status in ['pnew', 'open'], account_orders))

    def get_account_balances(self, name, asset = ''):
        result = self.get_cmd_result('dump -t balance -f {}'.format(name))
        return [{
            'account_id': '1.2.' + str(int(x[0])),
            'account': x[1].strip(),
            'asset_id': '1.3.' + str(int(x[2])),
            'asset': x[3].strip(),
            'settled': int(x[4]),
            'pdebit': int(x[5]),
            'pcredit': int(x[6]),
         } for x in result if asset == '' or x[3].strip() == asset]

def run_test():
    instance = RTEEndpoint('127.0.0.1', 20001)
    print(instance.get_account_balances('nathan'))
    print(instance.get_account_balances('nathan', 'CYB'))
    print(instance.get_account_balances('allegra-1441'))
    print(instance.get_account_balances('allegra-1441', 'JADE.USDT'))
    while True:
        for x in instance.get_account_open_orders('abbey-459'):
            print(dict(x))
        time.sleep(10)
    time.sleep(1000)

if __name__ == '__main__':
    run_test()
