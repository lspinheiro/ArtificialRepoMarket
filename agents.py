# -*- coding: utf-8 -*-

import numpy as np
from ga_trading import *
from asset import *

class FinancialInstitution(object):
    '''
    The FinancialInstitution class represents financial inrwemediaries as a whole. They have a series of financial metrics that
    indicates their healthy and performance and perform traders in the market aiming to maximize profits at a
    controled risk.
    '''
    def __init__(self,  type_, NAV, trading_type, etree, name):
    	'''
    	Inputs:
    		asset_list = List with the asset objects from the market
    		asset_name_list = list with names of assets (maybe deprecated)
    		type_ = Financial agent type (bank, hedge, mmf)
    		trading_type = list defining trading profile for the different assets (fixed inc, securitization, stocks)
    		etree = Genetic evolved tree of technical trading strategies for choosing
    		risk_profile = tuple with risk limits for market risk, liquidity_risk  = (max percent var loss, max percent iliq. assets)
    		missing = name, nav, initial leverage, 
    		max_concentration = Dict(risk:num, risk_free:[cash, gov, cd], loan)
    	'''
        self.state = "S"
        self.type_ = type_
        self.NAV = NAV # if fund_df.NAV.size == 1 else fund_df.NAV[0]
        self.trading_type = trading_type
        self.name = name
        self.turns = 0
        self.set_trading_params(etree, f_treshhold = (0.1, 0.5))


    def set_trading_params(self, evolved_trees, f_treshhold):

		if self.trading_type == 'technical':
			self.decision_tree = np.random.choice(evolved_trees)

		elif self.trading_type == 'fundamental':
			self.tau = np.random.uniform(f_treshhold[0], f_treshhold[1])

		else:
			self.probabilities = [.34, .32, .34]

    def create_portfolio(self):
		# portfolio kept in quantities
		self.portfolio = Portfolio(self.NAV)




    def stock_trading(self, stock, bond):
    	'''
        Function of trading strategies based on trader type:
        In:
        Out:
            list of orders in the format (decision, quantity_in_money)

        Trades are at 8 percent of cash or position. Limit is on concentration
        '''

        if self.state == "S":

        	# decision
        	if self.trading_type == 'technical':
        		decision = self.decision_tree.make_decision(stock)

        	elif self.trading_type == 'fundamental':
        		value = stock.dividend / 10.
        		if (stock.value[-1] - value ) < - self.tau:
        			decision =  1
        		elif (stock.value[-1] - value ) > self.tau:
        			decision =  -1
        		else:
        			decision =  0

        	else:
        		decision = np.random.choice([-1, 0, 1], p = self.probabilities)
        		



    		# if buy
    		if decision == 1:

    			return (1, 0.08 * self.portfolio.cash)
    			
    		elif decision == -1:
    			return (-1, 0.08 * self.portfolio.stock * stock.value[-1])
    		else:
    			return (0, 0)

    	elif self.state == "I":
    		quantity = - min(self.portfolio.cash, 0.)
    		quantity = min(quantity, self.portfolio.stock * stock.value[-1])
    		return (-1, self.portfolio.stock * stock.value[-1])

    	else:
    		return (0, 0)



    def repo_trading(self, stock, r_bond):
    	
    	pass

    def govbond_trading(self, stock, r_bond):

    	if self.state == "S":

    		mrisk = self.measure_market_risk(stock, r_bond)
    		lrisk = self.measure_liquidity_risk(stock, r_bond)


    		if self.portfolio.cash > 0.: 
    			quantity = np.random.uniform() * self.portfolio.cash

    			return (1, quantity)
    		else:
    			return (0, 0)

    	if self.state == "I":

    		quantity = - min(self.portfolio.cash, 0.)
    		quantity = min(quantity, self.portfolio.gov_bond)
    		
    		return (-1, quantity)



    def bond_trading(self, bond, stock):

		mrisk = self.measure_market_risk(stock, bond)
		lrisk = self.measure_liquidity_risk(stock, bond)
		leverage = self.measure_leverage()

		if self.state == "S":
			if (self.portfolio.cash > np.float64(0.)) & (mrisk < self.max_var) & (lrisk > self.min_liquidity):

				quantity = np.random.uniform() * self.portfolio.cash

				return (1, quantity)

    		elif (mrisk < self.max_var) | (lrisk > self.min_liquidity):
    			quantity = - min(self.portfolio.cash, 0.) 
	    		quantity = min(quantity, self.portfolio.bond) * np.random.uniform()

	    		return (-1, quantity)

    		else:
    			return (0, 0)

			if self.state == "I":

				event = np.random.uniform()
	    		if event < bond.liquidity:

		    		quantity = - min(self.portfolio.cash, 0.)
		    		quantity = min(quantity, self.portfolio.bond)
		    		#self.portfolio.remove_bond(quantity)
		    		return (-1, quantity)

    def loan_trading(self):
    	if self.portfolio.cash < 0.:
    		return (1., np.abs(self.portfolio.cash))
    	else:
    		return (-1., np.abs(self.portfolio.cash))


    def set_risk_profile(self, risk_profile):
    	'''
    	Function to define risk profile for leverage, market risk and liquidity risk
    	In:
    		tuple (max_var_percent_loss, min_liquidity, max_leverage)
    		VaR vary from 1 percent to to 15 percent
    		liquidity vary from 0. to 1.
    		leverage vary from 1. to inf (following pareto)

    	'''
    	self.max_var = risk_profile[0]
    	self.min_liquidity = risk_profile[1]
    	self.max_leverage = risk_profile[2]

    def measure_leverage(self):
		leverage =  self.portfolio.total_liabilities() / self.NAV
		return leverage


    def measure_market_risk(self, stock, bond):
    	'''
    	Calculate market risk and liquidity risk of the portifolio
    	'''

    	market_risk = 0.

    	# Stocks
    	if stock.value.size > 1:
    		market_risk += np.mean(np.diff(stock.value)) + 1.65 * np.std(np.diff(stock.value)) * self.portfolio.stock
    	else:
    		market_risk += 1.28 * 0.08 * self.portfolio.stock

    

    	# Repos
    	for repo in self.portfolio.repo:
    		market_risk += 1.28 * 0. * repo.ammount

    	# CDs
    	for cd in self.portfolio.fin_bond:
    		market_risk += 1.28 * 0.1 * cd.ammount

    	# Loans
    	for loan in self.portfolio.loan:
    		market_risk += 1.28 * 0. * loan.ammount

    	nav_and_liab = self.NAV + self.portfolio.total_liabilities()

    	return market_risk / nav_and_liab



    def measure_liquidity_risk(self, stock, r_bond):
    	'''

    	'''
    	liquidity = 0.
    	liquidity +=  1. * self.portfolio.cash
    	#liquidity += stock.liquidity * self.portfolio.stock * stock.value[-1]
    	liquidity += 1. * self.portfolio.gov_bond
    	#liquidity += r_bond.liquidity * self.portfolio.bond

    	for repo in self.portfolio.repo:
    		if repo.issuer:
    			liquidity += repo.ammount * repo.liquidity

    	# loans

    	for loan in self.portfolio.loan:
    		if loan.issuer:
    			liquidity += loan.ammount * loan.liquidity

    	

    	nav_and_liab = self.portfolio.NAV[-1] + self.portfolio.total_liabilities()
    	return liquidity / nav_and_liab

    def measure_complementary_liq(self, stock, r_bond):

    	liquidity = 0.
    	liquidity += r_bond.liquidity * self.portfolio.bond

    	# fin bonds
    	for cd in self.portfolio.fin_bond:
    		liquidity += cd.ammount * cd.liquidity

    	nav_and_liab = self.portfolio.NAV[-1] + self.portfolio.total_liabilities()
    	return liquidity / nav_and_liab



    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name





class HedgeFund(FinancialInstitution):
	'''
	Generaly are technical traders
	Admit more risk than banks
	Less leverage than banks
	'''

	def __init__(self,  type_, NAV, trading_type, etree, risk_profile, name):
		super(HedgeFund, self).__init__(type_, NAV, trading_type, etree, name)

	

	def __str__(self):
		print self.name
		print "NAV: ", self.NAV
		print "Max Var: ", self.max_var
		print "Min Liquidity: ", self.min_liquidity
		print "Max Leverage: ", self.max_leverage
		return ""
		

class Bank(FinancialInstitution):
	'''
	Generaly are fundamental traders
	High risk control (prudential regulation)
	The most leveraged
	'''

	def __init__(self,  type_, NAV, trading_type, etree, risk_profile, name):
		super(Bank, self).__init__(type_, NAV, trading_type, etree, name)

	def __str__(self):
		print self.name
		print "NAV: ", self.NAV
		print "Deposits: ", self.deposits
		print "Max Var: ", self.max_var
		print "Min Liquidity: ", self.min_liquidity
		print "Max Leverage: ", self.max_leverage
		return ""


class MMF(FinancialInstitution):
	'''
	Generaly are fundamental / noise traders
	Low risk admission, provide liquidity to others
	Low leverage
	'''

	def __init__(self,  type_, NAV, trading_type, etree, risk_profile, name):
		super(MMF, self).__init__(type_, NAV, trading_type, etree, name)

	def __str__(self):
		print self.name
		print "NAV: ", self.NAV
		print "Max Var: ", self.max_var
		print "Min Liquidity: ", self.min_liquidity
		print "Max Leverage: ", self.max_leverage
		return ""



class Portfolio(object):
	"""
	Class to keep track of assets in a Fin. agents portfolio and calculate metrics.
	"""

	def __init__(self, NAV):
		# assets
		self.cash = NAV
		self.stock = 0.
		self.gov_bond = 0.
		self.bond = 0.
		self.fin_bond = []
		self.repo = []
		self.loan = []
		# liabilities
		self.broker_margin = 0. # stocks
		self.credit = 0. # for bonds
		self.deposits = 0.
		#nav
		self.NAV = np.array([NAV])
		self.ta = np.array([0.])
		self.colateral = {'Government Bond': 0.,
			'Bond' : 0.,
			'CD': 0.
		}

	def total_assets(self, stock):
		ta = 0
		ta += self.cash
		ta += self.stock * stock.value[-1]
		ta += self.gov_bond
		ta += self.bond
		#for fin_bond in self.fin_bond:
		#	liquidity += fin_bond.liquidity * fin_bond.ammount
		for repo in self.repo:
			if repo.issuer:
				ta += repo.ammount 

		for loan in self.loan:
			if loan.issuer:
				ta += loan.ammount

		return ta

	def total_risky(self, stock):
		return (self.stock * stock.value[-1] + self.bond) / self.total_assets(stock)

	def total_risk_free(self, stock):

		cds = sum([cd.ammount for cd in self.fin_bond])
		return (self.cash + self.gov_bond + cds) / self.total_assets(stock)

	def total_loans(self, stock):

		repos = 0

		for repo in self.repo:
			if repo.issuer:
				repos += repo.ammount

		loans = 0

		for loans in self.loan:
			if loan.issuer:
				loans += loan.ammount

		return (repos + loans) / self.total_assets(stock)

	def total_liabilities(self):
		liabilities = 0

		for repo in self.repo:
			if not repo.issuer:
				liabilities += repo.ammount 

		for loan in self.loan:
			if not loan.issuer:
				liabilities += loan.ammount

		# liabilities
		liabilities += self.broker_margin # stocks
		liabilities += self.credit # for bonds
		liabilities += self.deposits

		return liabilities

	def trade_stock(self, stock, price, quantity, margin = .0):
		self.cash -= (quantity * price - margin)
		self.stock += quantity
		self.broker_margin += margin


	def add_gov_bond(self, quantity):
		self.gov_bond += quantity
		self.cash -= quantity

	def remove_gov_bond(self, quantity):
		self.gov_bond -= quantity
		self.cash += quantity


	def add_bond(self, quantity):
		self.bond += quantity
		self.cash -= quantity

	def remove_bond(self, quantity):
		self.bond -= quantity
		self.cash += quantity

	def add_fin_bond(self, ammount, issuer, premium = .0):
		self.fin_bond.append( FinBond(ammount, issuer, premium = .0))
		self.cash -= ammount

	def issue_fin_bond(self, ammount):
		self.credit += ammount
		self.cash += ammount

	def sell_fin_bond(self, bond_index, self_id, other_id):
		pass

	def make_repo(self, ammount, rate, is_issuer,counterpart_index, colateral, haircut):
		
		if is_issuer:
			self.repo.append( Repo(rate, ammount, is_issuer, counterpart_index, colateral, haircut))
			self.cash -= ammount

		else:
			self.repo.append( Repo(rate, ammount, is_issuer, counterpart_index, colateral, haircut))
			self.cash += ammount
			self.colateral[colateral] += ammount

	def update_haircut_and_margin(self, haircut_change, price_change, agents, self_index):

		if self.bond > 1. and len(self.repo) > 0:

			cum_haircut = self.colateral['Bond'] / sum([repo.ammount for repo in self.repo if not repo.issuer])
			
			self.bond *= (1. - price_change)

			self.colateral['Bond'] *= (1. + haircut_change)
			#delta_colateral  = self.colateral['Bond'] * (haircut_change)

			cum_haircut *= (1. + haircut_change)
			
			while self.colateral['Bond'] > (self.bond + 1.):

				index = np.random.choice(len(self.repo))

				if not self.repo[index].issuer:
					other = self.repo[index].counterpart_index
					ammount = self.repo[index].ammount


					del self.repo[index]
					self.cash -= ammount
					self.colateral['Bond'] -= ammount * cum_haircut

					for repo in agents[other[0]][other[1]].portfolio.repo:
						if repo.counterpart_index[1] == self_index and repo.ammount == ammount:
							del repo
							agents[other[0]][other[1]].portfolio.cash += ammount
							break
				else:
					pass
		else:
			pass




	def undo_repo(self):

		for repo in self.repo:
			if repo.issuer:
				self.cash += ((1. + repo.rate)**(1./360)) * repo.ammount
			else:
				self.cash -= ((1. + repo.rate)**(1./360)) * repo.ammount

		self.repo = []

	def make_loan(self , ammount, rate, is_issuer):
		'''
		Repos and loans remove/increase cash in create right/obligation in issuer/buyer at t=0 and reverse at t = 1.

		'''
		
		if is_issuer:
			self.loan.append( Loan(rate, ammount, is_issuer))
			self.cash -= ammount

		else:
			self.loan.append( Loan(rate, ammount, is_issuer))
			self.cash += ammount

	def undo_loan(self):

		for loan in self.loan:
			if loan.issuer:
				self.cash += ((1. + loan.rate)**(1./360)) * loan.ammount
			else:
				self.cash -= ((1. + loan.rate)**(1./360)) * loan.ammount

		self.loan = []


	def receive_deposit(self, ammount):
		self.deposits += ammount
		self.cash += ammount


	def withdraw_deposit(self, ammount):
		self.deposits -= ammount
		self.cash -= ammount

	def add_credit(self, ammount):
		self.credit += ammount
		self.cash += ammount

	def update_nav(self, stock):
		self.NAV =  np.append(self.NAV, ( (self.total_assets(stock) - self.total_liabilities()) - self.NAV[-1]))

	def update_ta(self, stock):
		self.ta = np.append(self.ta, self.total_assets(stock))

	def metrics(self, stock):
		pass


	def __str__(self):
		print "Assets"
		print "Cash: ", self.cash
		print "Stock: ", self.stock
		print "Government Bonds: ", self.gov_bond
		print "Bond: ", self.bond
		print "Repos: ", (len(self.repo), sum([repo.ammount for repo in self.repo]))
		#print "Interbank Loans: ", self.loan
		print "-------"
		print "Liabilities"
		print "Colateral: ", self.colateral['Bond'] # stocks
		#print "Credit: ", self.credit # for bonds
		print "Deposits: ", self.deposits
		print "-------"
		print "NAV"
		print "NAV: ", self.NAV
		print "-------"
		return " "

	def portfolio_summary(self, stock):

		print "TA: ", self.total_assets(stock)
		print "Liabilities: ", self.total_liabilities()



