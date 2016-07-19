# -*- coding: utf-8 -*-


import numpy as np


class Asset(object):
    '''
    The Fund class represents financial institutions as a whole. They have a series of financial metrics that
    indicates their healthy and performance and perform traders in the market aiming to maximize profits at a
    controled risk.
    '''
    def __init__(self):
        self.state = "S"
        #self.price = np.array([asset_df.Value.sum() / self.quantity])
        #self.set_parameters()
        #self.set_indicators()

        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
        

class Stock(Asset):
    '''
        Volatile stock asset traded in the market
    '''
    def __init__(self, quantity):
        super(Stock, self).__init__()
        self.quantity = 0.
        self.name = "Stock"
        self.value = np.array([1.])
        self.dividend = 10.
        self.liquidity = 1.
        self.default_probab = .0
        self.set_indicators()

    def increase_market_cap(self, quantity):
        self.quantity += quantity

    def update_dividend(self):
        self.dividend = 10. + .95 * (self.dividend - 10.) + np.random.normal(0., 2.)

    def set_indicators(self):
        if self.value.size == 1:
            self.MA, self.TRB, self.Filter, self.VOL, self.Mom, self.MomMA = self.value[-1], 0., 0., 0., 0., 0.
        else:
            self.MA = (self.value[-1] - self.value[:-1].mean())/self.value[:-1].mean()
            self.TRB = (self.value[-1] - self.value[:-1].max())/self.value[:-1].max()
            self.Filter = (self.value[-1] - self.value[:-1].min())/self.value[:-1].min()
            self.VOL = self.value.std()/self.value[:-1].mean()
            self.Mom = self.value[-1] - self.value[0]
            self.MomMA = self.MomMA * ((self.value.size-1) / self.value.size) + self.Mom/self.value.size






class GovBond(Asset):
    '''
    Risk free bond paying a interest rate of 5%.
    '''

    def __init__(self, quantity):
        super(GovBond, self).__init__()
        self.name = "Government Bond"
        self.value = np.array([1.])
        self.interest_rate = 0.10
        self.volatility = 0.
        self.liquidity = 1.
        self.default_probab = .0
        self.quantity = quantity



class RiskyBond(Asset):
    '''
    Risky bond.
    '''
    def __init__(self, quantity):
        super(RiskyBond, self).__init__()
        self.name = "Bond"
        self.value = np.array([1.])
        self.interest_rate = 0.11
        self.volatility = 0.
        self.liquidity = 0.5
        self.price = 1.
        self.risk = .02
        self.default_probab = .0
        self.quantity = quantity

    def increase_market_cap(self, quantity):
        self.quantity += quantity

    def set_risk(self, value):
        self.risk = value

    def update_liquidity(self, new_value):
        self.liquidity = new_value


    def update_price(self, new_price):
        self.price = new_price


##class FinBond(Asset):
#    '''
#    Risky bond.
#    '''
#    def __init__(self, ammount, issuer, premium = .0):
#        super(FinBond, self).__init__()
#        self.name = "Certificate of Deposit"
#        self.ammount = ammount
#        self.issuer = issuer
#        self.interest_rate = 0.105 + premium
#        self.volatility = 0.
#        self.liquidity = 0.9
#
#    def update_liquidity(self, new_value):
#        self.liquidity = new_value

    


class Repo(Asset):
    '''
    Repos are not traded at a central market. Every repo transacion creates an object in both parties with the characteristics of the transaction.
    Feats:
        has repo rate
        counterparty identified by index
        colateral = asset securitizing the operation
    '''

    def __init__(self, rate, ammount, is_issuer, counterpart_index, colateral, haircut, price = 1.):
        super(Repo, self).__init__()
        self.name = "Repurchase Agreement"
        self.price = price
        self.rate = rate
        self.ammount = ammount
        self.time = 1 # in case this is changed in the future
        self.issuer = is_issuer
        self.counterpart_index = counterpart_index
        self.colateral = colateral
        self.liquidity = 1.
        self.haircut = haircut

    def renew(self):
        pass

    def update_price(self, new_price):
        self.price = new_price

    





class Loan(Asset):
    '''
    Interbank lending are not traded at a central market. Every transacion creates an object in both parties with the characteristics of the transaction.
    Feats:
        has a interbank rate
        counterparty identified by index
        no colateral
    '''

    def __init__(self, rate, ammount, is_issuer):
        super(Loan, self).__init__()
        self.name = "Interbank lending"
        self.rate = rate
        self.ammount = ammount
        self.time = 1
        self.issuer = is_issuer
        self.liquidity = 1.



        
        
