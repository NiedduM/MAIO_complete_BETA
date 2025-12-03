# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 12:17:03 2024

@author: marce
"""

import numpy as np
import agentpy as ap


class Government(ap.Agent):
    
    def setup(self):
        
        #STOCKS
        self.liquidity = 0
        
        #FLOWS
        self.consumption_budget = 0
        self.unemployment_benefits = 0
        self.taxes = 0
        
        #PARAMS
        self.tax_rates = {}
        self.average_wage = 0
        self.ub_fraction = 0
        self.transfer_fraction = 0
        
        self.consumption_budgets = {}
        self.consumption_shares = {}
        self.consumption_from_RoW = {}
        self.consumptions = {}
        self.consumption = 0
        
        self.attempt_number = 0
        
        
    def make_period_account(self):
        
        self.liquidity += self.taxes
        
        self.taxes = 0
        
    def compute_average_wage(self):
        
        employed_list = self.model.Household_agents.select(self.model.Household_agents.flag_employed == 1)
        
        if(len(employed_list) >0):
            self.average_wage = sum(employed_list.wage)/len(employed_list)
            
        #print(self.average_wage)
        


    def distribute_transfers(self):
        
        transfers = self.average_wage*self.transfer_fraction*len(self.model.Household_agents)
        
        transfers_h = self.average_wage*self.transfer_fraction
        
        if(self.liquidity < transfers):
            
            if(self.liquidity>0):
            
                transfers_h =  self.liquidity/len(self.model.Household_agents) #transfers/self.liquidity
            else:
                transfers_h = 0
            
        for h in self.model.Household_agents:
            
            h.reveice_transfer(transfers_h)
            self.liquidity -= transfers_h
        
        
    def distribute_unemployment_benefits(self):
        
        self.compute_average_wage()
        
        unemployed_list = self.model.Household_agents.select(self.model.Household_agents.flag_employed == 0)
        
        if(len(unemployed_list)>0):
            
            self.unemployment_benefits = len(unemployed_list)*self.average_wage*self.ub_fraction
    
            if(self.liquidity > self.unemployment_benefits):
                
                ub = self.average_wage*self.ub_fraction
            
            else:
                
                ub = max(0,self.liquidity/len(unemployed_list))
                
            for h in unemployed_list:
                
                h.receive_unemployment_benefit(ub)
                self.liquidity -= ub
        else:
              
            self.unemployment_benefits = 0
                


    def determine_consumption_budgets(self):
       
        self.consumption_budget = max(0, self.liquidity)
       
        for comm in self.consumption_shares.keys():
            
            self.consumption_budgets[comm] = self.consumption_shares[comm]*self.consumption_budget
            self.consumptions[comm] = 0
        self.consumption = 0
            
    def buy(self, commodity):
        
        
        if(self.attempt_number == 0):
            if(self.consumption_budgets[commodity] > 0):
                self.buy_from_RoW(commodity)
        
        if(self.consumption_budgets[commodity] > 0):


            
            sellers_list = self.model.localKAU_agents.select(self.model.localKAU_agents.my_commodity == commodity ) #and self.model.localKAU_agents.supply>0)

            n_sellers = len(sellers_list)
            
            if(n_sellers > 0):
                
                demand = self.consumption_budgets[commodity]/n_sellers
                
                for s in sellers_list:
                    
                    price = s.get_price()
                    
                    demanded_quantity = demand/price
                    
                    bought_quantity = s.sell(demanded_quantity)
                    #print('Gov buying from ', s.id)
                    expenditure = bought_quantity*price
                    
                    self.consumption_budgets[commodity] -= expenditure
                    self.liquidity -= expenditure
                    self.consumption += expenditure
                    self.consumptions[commodity] += expenditure
        
        self.attempt_number +=1        
                    
    def buy_from_RoW(self, commodity):
        
        RoW = self.model.RoW[0]
        price = RoW.get_price(commodity)
        demanded_quantity = self.consumption_from_RoW[commodity]*self.consumption_budgets[commodity]/price        
        bought_quantity = RoW.sell(commodity, demanded_quantity)
        consumption = bought_quantity*price
        self.liquidity -= consumption        
        self.consumption_budgets[commodity] -= consumption
        self.consumption += consumption
        self.consumptions[commodity] += consumption
                    
    def reset_market_vars(self):
        
        self.attempt_number = 0
    
    def update_sellers_list(self, commodity):
        
        pass
       

    def receive_taxes(self, amount):
        
        self.taxes += amount
        
        

        
        

        
    

        
        
        
    
    
    