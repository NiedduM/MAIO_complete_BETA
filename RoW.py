# -*- coding: utf-8 -*-
"""
Created on Mon Jan 8 18:50:20 2024

@author: marce
"""

import agentpy as ap

class RoW(ap.Agent):
    
    def setup(self):
        
        self.consumption_budget = 0
        self.consumption_budgets = {}
        self.consumption_shares = {}
        self.consumptions = {}
        self.sails = {}
        self.net_exports = 0
        self.suppliers_weights = {}
        self.attempt_number = 0
        self.liquidity = 0
        self.prices = {}
        self.GDP = 0
        self.growth_rate = 0
        self.consumption2GDP = 0

    def determine_consumption_budgets(self):
        
        self.consumption_budget = self.consumption2GDP*self.GDP
        
        for comm in self.consumption_shares.keys():
            
            self.consumption_budgets[comm] = self.consumption_shares[comm]*self.consumption_budget

        
    def buy(self, commodity):
        
        
        if(self.attempt_number == 0):
            for ag in self.suppliers_weights[commodity].keys():
                
                demand = self.suppliers_weights[commodity][ag]*self.consumption_budgets[commodity]/ag.price
                #print(demand)
                bought_quantity = ag.sell(demand)
                
                expenditure = bought_quantity*ag.price
                
                self.consumptions[commodity] += expenditure
                self.liquidity -= expenditure
                #print('RoW buy :liquidity', self.liquidity)
            self.attempt_number +=1
    
    def sell(self, commodity, demand):
        
        sold_quantity = 0
        if(demand>0):
            sold_quantity =  demand       

        self.sails[commodity] += self.prices[commodity]*sold_quantity
        self.liquidity += self.prices[commodity]*sold_quantity
        #print('RoW sell :liquidity', self.liquidity)
        return sold_quantity
    
    
    def update_GDP(self):
                        
        self.GDP *= 1+self.growth_rate
        
        for comm in self.consumption_shares.keys():
            
            self.sails[comm] = 0
            self.consumptions[comm] = 0
            
    def get_price(self, commodity):
        
        return self.prices[commodity]
         
    def reset_market_vars(self):
        
        self.attempt_number = 0
    
    def update_sellers_list(self, commodity):
        
        pass
