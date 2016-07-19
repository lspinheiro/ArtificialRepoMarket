# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 08:33:50 2016

@author: Leonardo
"""

import os
import re
import copy

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from sympy.solvers import solve
from sympy import Symbol

from market import *
from agents import *
from asset import *
from ga_trading import *


if __name__ == '__main__':

	print "... Creating artificial market."
	market = Market()
	market.create_initial_market()

	repos = np.zeros(len(market.agents['banks']))
	deposits = np.zeros(len(market.agents['banks']))
	leverage = np.zeros(len(market.agents['banks']))
	nav = np.zeros(len(market.agents['banks']))

	for i in xrange(len(market.agents['banks'])):
	    repos[i] = sum([repo.ammount for repo in market.agents['banks'][i].portfolio.repo])
	    deposits[i] = market.agents['banks'][i].portfolio.deposits
	    leverage[i] = market.agents['banks'][i].measure_leverage()
	    nav[i] = market.agents['banks'][i].NAV

	N = len(market.agents['banks'])
	ind = np.arange(N)

	fontP = FontProperties()
	fontP.set_size('small')
	fig = plt.figure(figsize=(12,6))
	ax = plt.subplot(111)


	p1 = ax.bar(ind, nav, 1, color='#ff3333')
	p2 = ax.bar(ind, deposits, 1, color='gold', bottom=nav)
	p3 = ax.bar(ind, repos, 1, color='#3333ff', bottom=[nav[j] +deposits[j] for j in range(N)])
	ax.legend((p1[0], p2[0], p3[0]), ('NAV', 'Deposits', 'Repos'),loc='center left', bbox_to_anchor=(.4, .9))

	plt.savefig("leverage.png")

	bond = np.zeros(len(market.agents['banks']))
	stock = np.zeros(len(market.agents['banks']))
	gov = np.zeros(len(market.agents['banks']))
	cash = np.zeros(len(market.agents['banks']))


	for i in xrange(len(market.agents['banks'])):
	    gov[i] = market.agents['banks'][i].portfolio.gov_bond
	    bond[i] = market.agents['banks'][i].portfolio.bond
	    stock[i] = market.agents['banks'][i].portfolio.stock
	    cash[i] = market.agents['banks'][i].portfolio.cash


	N = len(market.agents['banks'])
	ind = np.arange(N)

	fontP = FontProperties()
	fontP.set_size('small')
	fig = plt.figure(figsize=(12,6))
	ax = plt.subplot(111)


	p1 = ax.bar(ind, gov, 1, color='#ff3333')
	p2 = ax.bar(ind, bond, 1, color='gold', bottom=gov)
	p3 = ax.bar(ind, stock, 1, color='#3333ff', bottom=[gov[j] +bond[j] for j in range(N)])
	p4 = ax.bar(ind, cash, 1, color='#5F9EA0', bottom=[gov[j] +bond[j]+stock[j] for j in range(N)])
	ax.legend((p1[0], p2[0], p3[0], p4[0]), ('Government Bonds', 'Risky Asset', 'Stock', 'Cash'),loc='center left', bbox_to_anchor=(.4, .85))
	plt.savefig("assets.png")

	print "... Starting Simulation."
	results = pd.DataFrame(market.simulate_market(crisis = (30, 0.2, 0.3), t_max = 30))
	results.to_csv("simulation_results.csv")