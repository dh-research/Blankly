"""
    ZeroRPC server for communicating with other languages or GUIs
    Copyright (C) 2021  Emerson Dove

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import Blankly
from calc import calc as real_calc
import sys
import zerorpc


# Tickers shouldn't be accessed from this class. Interfaces will not have access to them
class TradeInterface:
    def __init__(self):
        self.__auth_path = None
        self.__preferences_path = None
        self.__exchanges = []

    def calc(self, text):
        """ Very basic connectivity test, given a string compute the output """
        try:
            return real_calc(text)
        except Exception as e:
            return 0.0

    def echo(self, text):
        """echo any text """
        return text

    def init(self, auth_path, preferences_path):
        # Called from the dashboard
        self.__exchanges = []
        self.__auth_path = auth_path
        self.__preferences_path = preferences_path

    def create_portfolio(self, exchange_type, portfolio_name):
        if exchange_type == "coinbase_pro":
            self.__exchanges.append(Blankly.Coinbase_Pro(portfolio_name=portfolio_name,
                                                         auth_path=self.__auth_path,
                                                         preferences_path=self.__preferences_path))
        elif exchange_type == "binance":
            self.__exchanges.append(Blankly.Binance(portfolio_name=portfolio_name,
                                                    auth_path=self.__auth_path,
                                                    preferences_path=self.__preferences_path))
        else:
            raise ValueError("Exchange not found or unsupported")

    """ External State """
    def get_exchange_state(self, name):
        for i in range(len(self.__exchanges)):
            if self.__exchanges[i].get_name() == name:
                return [self.__exchanges[i].get_exchange_state(), name]

    """ 
    Internal State, this has all the currencies. This is mainly used for an initial definition of which currencies
    are being used, get model state is what will matter for the reporting into these blocks
    """
    def get_portfolio_state(self, name):
        for i in range(len(self.__exchanges)):
            if self.__exchanges[i].get_name() == name:
                return [self.__exchanges[i].__get_portfolio_state(), name]

    def run_model(self, name, currency_pair=None):
        for i in range(len(self.__exchanges)):
            if self.__exchanges[i].get_name() == name:
                self.__exchanges[i].start_models(currency_pair)

    def assign_model(self, portfolio_name, currency_pair, model_name, args=None):
        for i in range(len(self.__exchanges)):
            if self.__exchanges[i].get_name() == portfolio_name:
                self.__exchanges[i].append_model(model_name, currency_pair, args)

    """
    Three indicators at the top of the GUI - JSON with only 3 keys
    """
    def update_indicators(self, name):
        for i in range(len(self.__exchanges)):
            if self.__exchanges[i].get_name() == name:
                return self.__exchanges[i].get_indicators()


def parse_port():
    port = 4242
    try:
        port = int(sys.argv[1])
    except Exception as e:
        pass
    return '{}'.format(port)


def main():
    addr = 'tcp://127.0.0.1:' + parse_port()
    s = zerorpc.Server(TradeInterface())
    s.bind(addr)
    print('start running on {}'.format(addr))
    s.run()


if __name__ == '__main__':
    main()
