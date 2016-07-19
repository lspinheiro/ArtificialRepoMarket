
# coding: utf-8

import os
import re
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import networkx as nx


from market import *
from trader import *
from asset import *
from ga_trading import *



if __name__ == "__main__":
    np.random.seed(10)

    market = Market()

    market.create_initial_market()



    print "% .4g" % np.mean([bank.NAV for bank in market.agents['banks']])
    print "% .4g" % np.mean([bank.NAV for bank in market.agents['mmfs']])
    print "% .4g" % np.mean([bank.measure_leverage() for bank in market.agents['banks']])
    print len(market.agents['mmfs'])
    print market.agents['banks'][0].portfolio.repo[0].counterpart_index




    ########## Leverage stacked plot ##############
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


    ########## Leverage stacked plot ##############
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
    plt.show()



    results = pd.DataFrame(market.simulate_market(crisis = (30, 0.2, 0.3), t_max = 30))


    results.to_csv("results.csv")


    lev_results = (results.total_leverage + 1.).values


    ax = plt.subplot(111)
    ax.plot(range(1,32), lev_results, 'r--', linewidth=2.)
    ax.bar(range(1,32), lev_results)
    ax.set_ylim([2.5,4.])
    ax.set_xlim([1, 31])
    ax.set_xlabel("timestep")
    ax.set_ylabel("Average leverage")
    plt.show()

    results.ix[30, 'haircut'] = 1.000

    ax = results.haircut.plot(kind = 'bar', style='k--')
    ax.set_xlabel("timestep")
    ax.set_ylabel("% of haircut")
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
    plt.savefig("haircuts.png")

    ax = plt.subplot(111)
    ind = results.index

    p1 = ax.plot(ind, results.healthy, '-',color='#ff3333')
    p2 = ax.plot(ind, results.border, color='gold')
    p3 = ax.plot(ind, results.failures, color='#3333ff', )
    ax.legend((p1[0], p2[0], p3[0]), ('NAV', 'Deposits', 'Repos'),loc='center left', bbox_to_anchor=(.5, .9))

    ax = plt.subplot(111)
    ind = results.index
    ax.plot(ind, results.healthy, 'r--',ind, results.border, 'b--',ind, results.failures, 'g--')
    ax.legend(('Solvent', 'Defaulted', 'Bankrupt'),loc='center left', bbox_to_anchor=(.5, .9))
    ax.set_xlabel("timestep")
    ax.set_ylabel("Number of banks")

    plt.savefig("failures.png")



    repos = np.zeros(len(market.agents['banks']))
    deposits = np.zeros(len(market.agents['banks']))
    leverage = np.zeros(len(market.agents['banks']))
    nav = np.zeros(len(market.agents['banks']))

    for i in xrange(len(market.agents['banks'])):
        repos[i] = sum([repo.ammount for repo in market.agents['banks'][i].portfolio.repo])
        deposits[i] = market.agents['banks'][i].portfolio.deposits
        leverage[i] = market.agents['banks'][i].measure_leverage()
        nav[i] = market.agents['banks'][i].portfolio.NAV[-1]


