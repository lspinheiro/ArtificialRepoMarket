# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
from agents import *
from asset import *
from sympy.solvers import solve
from sympy import Symbol


np.random.seed(10)

class OrderBook(object):
    def __init__(self):
        self.stock_order_book = []
        self.gov_bond_order_book = []
        self.bond_order_book = []
        self.loan_order_book = []
                       
                
    def trade_stock_order(self, order):
        """
        Add orders from single investor.
        Orders are tuples ((decision, quant), agent_type, agent_index)
        """
        self.stock_order_book.append(order)

    def trade_gov_order(self, order):
        self.gov_bond_order_book.append(order)

    def trade_bond_order(self, order):
        self.bond_order_book.append(order)

    def trade_loan_order(self, order):
        self.loan_order_book.append(order)
                
    
    def compute_stock_trades(self, agents,stock, delta = 12):
        '''
        Compute trades given the order book is complete
        In:
            (self item: Orders are tuples ((decision, quant), agent_type, agent_index))
            stock = the stock asset
            delta = tuple with order imbalance sensitivity parameter
        Out:
            None. fund_list and asset_list are changed in the process.
        '''
        self.stock_order_book = np.random.permutation(self.stock_order_book)

        imbalance = sum([order[0][0] * order[0][1] for order in self.stock_order_book]) / stock.quantity
        price = stock.value[-1] * (1 + delta * imbalance)
        # price change
        stock.value = np.append(stock.value, price)
        
        #trades
        current_price =  stock.value[-2]
        pointer1 = 0

        while pointer1 != len(self.stock_order_book):
            if self.stock_order_book[pointer1][0][1] == 0.:
                        pointer1 += 1
            else:
                agent1index = self.stock_order_book[pointer1][2]
                agent1type = self.stock_order_book[pointer1][1]
                agent1decision = self.stock_order_book[pointer1][0][0]

                for pointer2 in xrange(pointer1 + 1, len(self.stock_order_book)):

                    # if buyer meets seller
                    try:
                        if self.stock_order_book[pointer1][0][1] != self.stock_order_book[pointer2][0][1] and self.stock_order_book[pointer2][0][1] != 0.:

                            agent2index = self.stock_order_book[pointer2][2]
                            agent2type = self.stock_order_book[pointer2][1]
                            agent2decision = self.stock_order_book[pointer2][0][0]

                            trades_in_money =  min(self.stock_order_book[pointer1][0][1], self.stock_order_book[pointer2][0][1])
                            trades_in_quantity = trades_in_money / current_price

                            agents[agent1type][agent1index].portfolio.trade_stock(stock, 
                                price = current_price, 
                                quantity = agent1decision * trades_in_quantity, 
                                margin = .0)

                            agents[agent2type][agent2index].portfolio.trade_stock(stock, 
                                price = current_price, 
                                quantity = agent2decision * trades_in_quantity, 
                                margin = .0)

                            # break and move to next if first pointer has sold all assets
                            if self.stock_order_book[pointer1][0][1] == 0.:
                                break
                    except TypeError:
                        print "error"
                        print self.stock_order_book[pointer2][0][1]
                        break

                # break if position could not be liquidated
                if not self.stock_order_book[pointer1][0][1] == 0.:
                    break

                # move to next buyer/vendor 
                pointer1 += 1

        self.stock_order_book = []

        def compute_gov_bond_trades(self, agents):
            # Orders are tuples ((decision, quant), agent_type, agent_index)

            for order in self.gov_bond_order_book:

                agent_index = order[2]
                agent_type = order[1]

                if order[0][0] == 1:
                    agents[agent1type][agent1index].portfolio.add_gov_bond(order[0][1])
                else:
                    agents[agent1type][agent1index].portfolio.remove_gov_bond(order[0][1])


        def compute_bond_trades(self, agents, bond):
            pass

        def compute_loan_trades(self, agents):
            pass



        


                
                
    def reset(self):
        for key in self.order_book:
            self.stock_order_book = []
    
    def __repr__(self):
        return self.order_book.__repr__()
        
        
        

class Market(object):
    def __init__(self, req_liquidity = 0.37):
        self.req_liquidity = req_liquidity
        self.Assets = ["Stock", "CDs", "Bond", "Government Bond", "Cash"]
        self.stock = Stock(quantity = 0.)
        self.bond = RiskyBond(quantity = 0.)
        self.order_book = OrderBook()
        self.interbank_rate = .11 #to be defined
        self.repo_rate = .105 # to be definedbb
        self.agents = {}
        
    def create_initial_market(self, nbanks = 100, nhedge = 200, nmmfs = 200, f_trading_prob = [.4, .4, .2]):
        
        # Initialize assets (gov bonds, stocks and bonds must be a market object. The market needs some of its attrbutes)
        # ammount of cash = ammount of bonds + gov. bonds +  bonds (no lack of money price preassure)
        # bonds are 50% gov, 25% risky, 25% fin, stocks are 50% of gov bonds
        
        

        eMarket = EvolvingMarket(n_trees = 150) # MUST BE MULTIPLE OF 6
        evolved_trees = eMarket.evolve(300) 

        # Initialize financial agents
        # NAV, trading_type and risk profile are random parameters
        # NAVs are sampled from a pareto distribution
        self.agents['banks'] = [
            Bank(type_ = "Bank", 
                NAV = (np.random.pareto(3.) + 1) * 1e8, 
                trading_type = np.random.choice(["technical", "fundamental", "noise"], p= f_trading_prob), 
                etree = evolved_trees, 
                risk_profile = (), 
                name = "Bank {0}".format(i)) for i in xrange(nbanks)
        ]

        self.agents['hedgefunds'] = [
            HedgeFund(type_ = "Hedge Fund", 
                NAV = (np.random.pareto(3.) + 1) * 5e7, 
                trading_type = np.random.choice(["technical", "fundamental", "noise"], p= f_trading_prob), 
                etree = evolved_trees, 
                risk_profile = (), 
                name = "Hedge Fund {0}".format(i)) for i in xrange(nbanks)
        ]

        self.agents['mmfs'] = [
            MMF(type_ = "MMF", 
                NAV = (np.random.pareto(3.) + 1) * 3e8, 
                trading_type = np.random.choice(["technical", "fundamental", "noise"], p= f_trading_prob), 
                etree = evolved_trees, 
                risk_profile = (), name = "MMF {0}".format(i)) for i in xrange(nbanks)
        ]

        # Define initial portfolios (may change in calibration)
        for i in xrange(len(self.agents['banks'])):
            self.agents['banks'][i].create_portfolio()
            self.agents['banks'][i].set_trading_params(evolved_trees, (.1, .5))

            deposits = ((np.random.pareto(3.) + 1) * 1.) * self.agents['banks'][i].portfolio.NAV[-1]
            self.agents['banks'][i].portfolio.receive_deposit(ammount = deposits)
            total = self.agents['banks'][i].portfolio.NAV[-1] + self.agents['banks'][i].portfolio.deposits

            
            stocks = np.random.uniform(.05, .2) * total
            self.agents['banks'][i].portfolio.trade_stock(stock = self.stock, price = self.stock.value[-1],quantity = stocks, margin = 0.)
            self.stock.increase_market_cap(stocks)

            gov_bonds = np.random.uniform(.1, .3) * total
            self.agents['banks'][i].portfolio.add_gov_bond(quantity = gov_bonds)
            
            bonds = min(np.random.uniform(.2, .6) * total, total - stocks - gov_bonds)
            self.agents['banks'][i].portfolio.add_bond(quantity = bonds)

            market_risk = np.random.uniform(.01, 0.15)
            liquidity_risk = np.random.uniform(0.10, 0.50)
            leverage = np.random.normal(12., 3.)
            self.agents['banks'][i].set_risk_profile((market_risk, liquidity_risk, leverage))

        
        for i in xrange(len(self.agents['mmfs'])):
            self.agents['mmfs'][i].create_portfolio()
            self.agents['mmfs'][i].set_trading_params(evolved_trees, (.1, .5))

            total = self.agents['mmfs'][i].portfolio.NAV[-1]
            self.agents['mmfs'][i].portfolio.add_gov_bond(quantity = np.random.uniform(.2, .7) * total)
            self.agents['mmfs'][i].portfolio.add_bond(quantity = np.random.uniform(.0, .3) * total)

            market_risk = np.random.uniform(.00, 0.05)
            liquidity_risk = np.random.uniform(0.8, 1.0)
            leverage = (np.random.pareto(5.) + 1) * 1.
            self.agents['mmfs'][i].set_risk_profile((market_risk, liquidity_risk, leverage))

        for i in xrange(len(self.agents['hedgefunds'])):
            self.agents['hedgefunds'][i].create_portfolio()
            self.agents['hedgefunds'][i].set_trading_params(evolved_trees, (.1, .5))
        
            credit = ((np.random.pareto(5.) + 1) * 1.) * self.agents['hedgefunds'][i].portfolio.NAV[-1]
            self.agents['hedgefunds'][i].portfolio.add_credit(ammount = credit)
            total = self.agents['hedgefunds'][i].portfolio.NAV[-1] + self.agents['hedgefunds'][i].portfolio.credit
        
            stocks = np.random.uniform(.2, 1.) * total
            self.agents['hedgefunds'][i].portfolio.trade_stock(stock = self.stock, price = self.stock.value[-1],quantity = stocks, margin = 0.)
            self.stock.increase_market_cap(stocks)
        
        
            bonds = min(np.random.uniform(.0, .8) * total, total - stocks)
            self.agents['hedgefunds'][i].portfolio.add_bond(quantity = bonds)
        
            gov_bonds = min(np.random.uniform(.0, .2) * total, 0.)
            if gov_bonds == 0:
                pass
            else:
                self.agents['hedgefunds'][i].portfolio.add_gov_bond(quantity = gov_bonds)
        
            market_risk = np.random.uniform(.01, .15)
            liquidity_risk = np.random.uniform(0.0, .5)
            leverage = (np.random.pareto(3.) + 1) * 2.
            self.agents['hedgefunds'][i].set_risk_profile((market_risk, liquidity_risk, leverage))



        # add risky bond repos:
        for k in xrange(20):
            for i in np.random.permutation(len(self.agents['banks'])):
                if self.agents['banks'][i].measure_leverage() < self.agents['banks'][i].max_leverage:


                    for j in np.random.permutation(len(self.agents['mmfs']))[:5]:
                        maximum_money = max(0., 
                            self.agents['banks'][i].portfolio.total_assets(self.stock) * (self.agents['banks'][i].max_leverage - self.agents['banks'][i].measure_leverage()))
                        if maximum_money < 0:
                            print 'mmoney error'
                        repo_margin = max(0., self.agents['banks'][i].portfolio.bond - self.agents['banks'][i].portfolio.colateral['Bond'])
                        if repo_margin < 0:
                            print 'margin error'
                        max_repo_lending = min(repo_margin, maximum_money)

                        if len(self.agents['mmfs'][j].portfolio.repo) > 10:
                            available_capital = self.agents['mmfs'][j].portfolio.cash#- (.1 * self.agents['mmfs'][j].portfolio.total_assets(self.stock))
                            if available_capital < 0:
                                print 'capital error'

                            quantity = min(max_repo_lending, available_capital)
                            if quantity > 0.:
                                #max_repo_lending -= quantity
                                # take repo
                                self.agents['banks'][i].portfolio.make_repo(ammount = quantity, rate = 0.105, 
                                    colateral = "Bond", is_issuer = False, counterpart_index = ('mmfs', j) ,haircut = 0.)
                                self.agents['banks'][i].portfolio.add_bond(quantity = quantity)
                                # do repo
                                self.agents['mmfs'][j].portfolio.make_repo(ammount = quantity, rate = 0.105, 
                                    colateral = "Bond", is_issuer = True, counterpart_index = ('banks', i), haircut = 0.)

                            if max_repo_lending == 0.:
                                break
                        else:
                            available_capital = (np.random.choice([np.random.uniform(.2, .5), np.random.uniform(.3, .8), 1.], p = [0.5, 0.35, 0.15]) *
                                self.agents['mmfs'][j].portfolio.cash)#- (.1 * self.agents['mmfs'][j].portfolio.total_assets(self.stock)))

                            if available_capital < 0:
                                print 'else capital error'

                            quantity = min(max_repo_lending, available_capital)
                            if quantity > 0.:
                                #max_repo_lending -= quantity
                                # take repo
                                self.agents['banks'][i].portfolio.make_repo(ammount = quantity, rate = 0.105, 
                                    colateral = "Bond", is_issuer = False, counterpart_index = ('mmfs', j), haircut = 0.)
                                self.agents['banks'][i].portfolio.add_bond(quantity = quantity)
                                # do repo
                                self.agents['mmfs'][j].portfolio.make_repo(ammount = quantity, rate = 0.105, 
                                    colateral = "Bond", is_issuer = True, counterpart_index = ('banks', i), haircut = 0.)

                            if max_repo_lending == 0.:
                                break



        
        for key in self.agents:
            for index in xrange(len(self.agents[key])):
                self.agents[key][index].portfolio.update_ta(self.stock)




        
    
    def iterate(self, delta = (6, 12)):
        '''
        In:
            delta = market sensitivity to imbalance in offer and demand in asset trades 
        '''
        # Compute decisions for each for every fund and add to order book

        for key in self.agents:
            for index in xrange(len(self.agents[key])):
                order = self.agents[key][index].stock_trading(self.stock, self.bond)
                if order[0] != 0:
                    self.order_book.trade_stock_order((order, key, index))

        self.order_book.compute_stock_trades(self.agents, self.stock, delta = 6)


        for key in self.agents:
            for index in xrange(len(self.agents[key])):
                self.agents[key][index].portfolio.update_ta(self.stock)
                self.agents[key][index].portfolio.update_nav(self.stock)



        self.stock.update_dividend()

        
        
    def simulate_market(self, crisis = (300, 0.2, 0.3), t_max = 30):
        '''
        Crisis is a tuple containing the timestep, the asset index and the fall in value as percentage, fall in liquidity. Ex: (3, 4, 0.5)
        '''
        results = {
            'total_leverage':[],
            'haircut':[],
            'failures':[],
            'border':[],
            'healthy':[]

        }

        results['total_leverage'].append(sum([bank.measure_leverage() for bank in self.agents['banks']]) / len(self.agents['banks']))
        if len(results['haircut']) == 0:
            results['haircut'].append(0.)
        else:
            results['haircut'].append(results['haircut'][-1] + liq_change)
        results['failures'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'R']))
        results['border'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'I']))
        results['healthy'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'S']))

        for i in xrange(crisis[0]):
            self.iterate()



        # initial crisis
        self.bond.update_liquidity(1. * crisis[2])
        self.bond.update_price(1. * crisis[1])
        price_change = crisis[1]
        liq_change = crisis[2]
        last_imbalance = 0.

        # Update price, liquidity and haircuts


        # iteration
        for _ in xrange(crisis[0]):
            print 'iter: ', _
            #update haircut and margin calls
            for index, bank in enumerate(self.agents['banks']):
                bank.portfolio.update_haircut_and_margin(haircut_change = liq_change, price_change = price_change,
                 agents = self.agents, self_index = index)
            
            # update states
            for index, bank in enumerate(self.agents['banks']):
                if bank.portfolio.cash < 0 and bank.state == 'S':
                    bank.state = 'I'
                elif bank.portfolio.cash > 0 and bank.state == 'I':
                    bank.state = 'S'
                elif bank.portfolio.cash < 0 and bank.state == 'I':
                    bank.turns += 1
                    if bank.turns >= 5:
                        bank.state = 'R'

            # trades
            
            for index, bank in enumerate(self.agents['banks']):
                bank.bond_trading(self.bond, self.stock)
                if bank.portfolio.cash > 0:
                    bank.state = 'S'


            ## bond
            for index, bank in enumerate(self.agents['banks']):
                bank.govbond_trading(self.stock, bank.portfolio.bond)
                if bank.portfolio.cash > 0:
                    bank.state = 'S'


            ## stock
            for key in self.agents:
                for index in xrange(len(self.agents[key])):
                    order = self.agents[key][index].stock_trading(self.stock, self.bond)
                    if order[0] != 0:
                        self.order_book.trade_stock_order((order, key, index))

            self.order_book.compute_stock_trades(self.agents, self.stock, delta = 6)

            ## bond
            for index, bank in enumerate(self.agents['banks']):
                if bank.portfolio.cash > 0:
                    bank.state = 'S'

            for key in self.agents:
                for index in xrange(len(self.agents[key])):
                    self.agents[key][index].portfolio.update_ta(self.stock)
                    self.agents[key][index].portfolio.update_nav(self.stock)

            self.stock.update_dividend()


            # Update results

            results['total_leverage'].append(sum([bank.measure_leverage() for bank in self.agents['banks']]) / len(self.agents['banks']))
            if len(results['haircut']) == 1:
                results['haircut'].append(liq_change)
            else:
                results['haircut'].append(results['haircut'][-1] + liq_change)
            results['failures'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'R']))
            results['border'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'I']))
            results['healthy'].append(sum([1 for bank in self.agents['banks'] if bank.state == 'S']))

            ###### price change for next iteration
            bond_imbalance = sum([1. for bank in self.agents['banks'] if bank.state == 'I'])
            delta_imbalance = (bond_imbalance - last_imbalance) / len(self.agents['banks'])
            price_change = .02
            liq_change = delta_imbalance / 10.


        
        return results
        

        

        














