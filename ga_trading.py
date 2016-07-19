import numpy as np
import copy
import re



class DecisionTree(object):
    '''
    Decision tree class for technical traders strategies.
    The class has the decision mechanism as well as the evolving rules.
    '''
    def __init__(self):
        self.indicators = ['MA', 'TRB','Filter', 'VOL','Mom','MomMA']
        self.condition = ['if','elsif', 'else']
        self.logical = ['and','or']
        self.negate = ['', 'not']
        self.operators = ['==','<','>']
        self.choices = [-1, 1, 0]
        #self.values = np.random.uniform(-1., 1.) deprecated
        self.generate_tree()
        self.fitness = [0, 0]
        
    def generate_rule(self):
        rules = ['{0} ( {1} {2} {3})'.format(np.random.choice(self.negate),
                                        np.random.choice(self.indicators), 
                                        np.random.choice(self.operators), 
                                        np.random.uniform(-1., 1.))]
        
        random_event = np.random.uniform() 
        while random_event > 0.7:
            
            rules.append(np.random.choice(self.logical))
            rules.append('{0} ( {1} {2} {3})'.format(np.random.choice(self.negate),
                                        np.random.choice(self.indicators), 
                                        np.random.choice(self.operators), 
                                        np.random.uniform(-1., 1.)))
            
            random_event = np.random.uniform() 
            
        return rules
    
    def generate_tree(self):
        '''
        Generate tree of random rules. Used separately for buy and sell strategies.
        '''
        self.tree = []
        self.decisions = []
        self.tree.append(self.generate_rule())
        self.decisions.append(np.random.choice([-1,1]))

        for i in xrange(8):
            if np.random.uniform() < 0.7:
                self.tree.append(self.generate_rule())
                self.decisions.append(np.random.choice([-1,1]))
        return None

    
    def make_decision(self, asset):
        '''
        Function to choose rules from tree and make an order.
        '''
        MA, TRB,Filter, VOL,Mom,MomMA = asset.MA, asset.TRB, asset.Filter, asset.VOL, asset.Mom, asset.MomMA
        for index in xrange(len(self.tree)):
            branch = self.tree[index]
            if eval(" ".join(branch)):
                return self.decisions[index]

        return 0
        
        
    def mutate(self):
        '''
        Chooses a random rule and mutates one element of the rule.
        '''
        
        # todo (doing)
        branch_index = 0#np.random.choice(range(len(self.tree)))
        branch = self.tree[branch_index]
        rule_index = 0#np.random.choice(range(len(branch)))
        
        # if logical connector, choose another random logical conector
        if self.tree[branch_index][rule_index] in self.logical:
            index_ = self.logical.index(self.tree[branch_index][rule_index])
            self.tree[branch_index][rule_index] = self.logical[1 - index_]
            
        # if is rule, choose element of rule to change and use regex to change element
        else:
            choice = np.random.choice(['indicator', 'operator','negate', 'decision','value'])
            
            if choice == 'indicator':
                ind_ = next(x for x in self.indicators if (' ' + x + ' ') in self.tree[branch_index][rule_index])
                new_ind = np.random.choice([e for e in self.indicators if e != ind_])
                index_ = self.indicators.index(ind_)
                index2_ = self.tree[branch_index][rule_index].index(ind_)
                
                self.tree[branch_index][rule_index] = self.tree[branch_index][rule_index][:index2_] + new_ind + self.tree[branch_index][rule_index][index2_+len(ind_):]
                
            elif choice == 'operator':
                ind_ = next(x for x in self.operators if x in self.tree[branch_index][rule_index])
                new_ind = np.random.choice([e for e in self.operators if e != ind_])
                index_ = self.operators.index(ind_)
                index2_ = self.tree[branch_index][rule_index].index(ind_)
                self.tree[branch_index][rule_index] = self.tree[branch_index][rule_index][:index2_] + new_ind + self.tree[branch_index][rule_index][index2_+len(ind_):]
            
            elif choice == 'negate':
                if 'not' in self.tree[branch_index][rule_index]:
                    self.tree[branch_index][rule_index] = self.tree[branch_index][rule_index][3:]
                else:
                    self.tree[branch_index][rule_index] = 'not' + self.tree[branch_index][rule_index]
            elif choice == 'decision':
                self.decisions[branch_index] *= -1
                            
            else: # is value
                value_ = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", self.tree[branch_index][rule_index])[0]
                new_value = float(value_) * np.random.uniform(-2, 2)
                start_index = self.tree[branch_index][rule_index].find(value_)
                self.tree[branch_index][rule_index] = self.tree[branch_index][rule_index][:start_index] + str(new_value) + ')'
                
                
    def crossover(self, other_tree):
        '''
        Chooses random rules from 2 trees and exchanges the rules among them.
        '''
        self_rule_index = np.random.choice(range(len(self.tree)))
        other_rule_index = np.random.choice(range(len(other_tree.tree)))
        self.tree[self_rule_index], other_tree.tree[other_rule_index] = other_tree.tree[other_rule_index], self.tree[self_rule_index]
        self.decisions[self_rule_index], other_tree.decisions[other_rule_index] = other_tree.decisions[other_rule_index], self.decisions[self_rule_index]
    
    def replace(self):
        '''
        Delete random old rule and replaces it with new rule.
        '''
        old_rule_index = np.random.choice(range(len(self.tree)))
        
        new_rule = ['{0} ( {1} {2} {3})'.format(np.random.choice(self.negate),
                                        np.random.choice(self.indicators), 
                                        np.random.choice(self.operators), 
                                        np.random.uniform(-1., 1.))]
        
        self.tree[old_rule_index] = new_rule
    
    def evolve(self):
        '''
        Evolves tree buy means of mutations, crossover and replacements.
        
        '''
    
    def calculate_fitness(self, ta_hist, avg_gain):
        '''
        Calculates fitness by improvement in TA.
        ''' 
        gain = (ta_hist[-1] - ta_hist[-2])/ta_hist[-2] - avg_gain
        self.fitness[0] += 1
        self.fitness[1] = ((self.fitness[0] - 1) * self.fitness[1] + gain)/self.fitness[0]





class FakeAsset(object):
    '''
    Simple trader to evolve strategies.
    Can only be technical. Keeps only TA history 
    '''
    def __init__(self):
        self.price = np.array([1.])
        self.set_indicators()
        self.type_ = 'variable income'
    
    def set_indicators(self):
        if self.price.size == 1:
            self.MA, self.TRB, self.Filter, self.VOL, self.Mom, self.MomMA = self.price[-1], 0, 0, 0, 0, 0
        else:
            self.MA = (self.value[-1] - self.value[:-1].mean())/self.value[:-1].mean()
            self.TRB = (self.value[-1] - self.value[:-1].max())/self.value[:-1].max()
            self.Filter = (self.value[-1] - self.value[:-1].min())/self.value[:-1].min()
            self.VOL = self.value.std()/self.value[:-1].mean()
            self.Mom = self.value[-1] - self.value[0]
            self.MomMA = self.MomMA * ((self.value.size-1) / self.value.size) + self.Mom/self.value.size







class EvolvingMarket(object):
    def __init__(self, n_trees):
    	# n_tree must be multiple of six
        self.trees = [DecisionTree() for _ in xrange(n_trees)]
        self.quantities = [1e3 for _ in xrange(n_trees)]
        self.cash = [1e3 for _ in xrange(n_trees)]
        self.asset = FakeAsset()
        self.TA = [[self.cash[i] + self.quantities[i] * self.asset.price[0]] for i in xrange(n_trees)]
        self.n = n_trees
        
    def evolve(self, gen):
        
        # Iterate over number of generations
        for i in xrange(gen):
            
            # trade
            decisions = [tree.make_decision(self.asset) for tree in self.trees]
            quantity = [np.random.randint(1, 0.25*self.quantities[i]) for i in xrange(self.n)]
            imbalance = sum([decisions[i]*quantity[i] for i in xrange(self.n)])/ (1e3 * self.n)
            price = (1 + imbalance) * self.asset.price[-1]
            self.asset.price = np.append(self.asset.price, price)
            
            # clear orders

            for order_ind in xrange(self.n):
                if decisions[order_ind]==0 or quantity[order_ind] == 0:
                    continue
                    
                for order2_ind in xrange(order_ind+1, self.n):
                    if quantity[order2_ind] == 0 or decisions[order_ind] == 0:
                        continue
                    elif decisions[order_ind] == -1*decisions[order2_ind]:
                        
                        trade_quantity = min(quantity[order_ind], quantity[order2_ind])
                        trade_money = trade_quantity * self.asset.price[-2]
                        self.quantities[order_ind] += trade_quantity * decisions[order_ind]
                        quantity[order_ind] -= trade_quantity
                        self.quantities[order2_ind] += trade_quantity * decisions[order2_ind]
                        quantity[order2_ind] -= trade_quantity
                        self.cash[order_ind] -= trade_money * decisions[order_ind]
                        self.cash[order2_ind] -= trade_money * decisions[order2_ind]
                        if quantity[order_ind] == 0:
                            break
                    else:
                        continue
                     
                        
            # update total assets
            for i in xrange(self.n):
                self.TA[i].append(self.cash[i] + self.quantities[i] * self.asset.price[-1])
                
            # Calculate fitness
            market_avg_gain = np.array([(self.TA[i][-1] - self.TA[i][-2])/self.TA[i][-2] for i in xrange(self.n)]).mean()

            for i in xrange(len(self.trees)):
                self.trees[i].calculate_fitness(self.TA[i], market_avg_gain)
            
            # start survival of the fittest
            new_pop = []
            
            # selection
            #self.trees = sorted(self.trees, key = lambda x: x.fitness[1])
            fitness = [self.trees[i].fitness[1] for i in xrange(self.n)]
            probab = np.array([fitness[i] if fitness[i] > 0 else 0 for i in xrange(self.n)])
            probab /= probab.sum()
            try:
                selected_tree_indexes = np.random.choice(a = range(self.n), size = self.n/3, replace=False,p = probab).tolist()
            except ValueError:
                selected_tree_indexes = np.random.choice(a = range(self.n), size = self.n/3, replace=False).tolist()
            for tree_index in selected_tree_indexes:
                new_pop.append(copy.deepcopy(self.trees[tree_index]))
            
            indexes_left = [i for i in range(self.n) if i not in selected_tree_indexes]
            
            # crossover
            for _ in xrange(self.n/6):
                tree1_index, tree2_index = np.random.choice(indexes_left, size=2, replace=False)
                self.trees[tree1_index].crossover(self.trees[tree2_index])
                new_pop.append(copy.deepcopy(self.trees[tree1_index]))
                new_pop.append(copy.deepcopy(self.trees[tree2_index]))
            
            # mutation
            for _ in xrange(self.n/3):
                rtree_index = np.random.choice(indexes_left)
                self.trees[rtree_index].mutate()
                new_pop.append(copy.deepcopy(self.trees[rtree_index]))
                
            self.trees = copy.deepcopy(new_pop)
            
            # new elements
            #for _ in xrange(self.n/3):
                
            
            # reset cash and quantities and TA
            self.quantities = [1e3 for _ in xrange(self.n)]
            self.cash = [1e3 for _ in xrange(self.n)]
            self.TA = [[self.cash[i] + self.quantities[i] * self.asset.price[-1]] for i in xrange(self.n)]
        
        return self.trees