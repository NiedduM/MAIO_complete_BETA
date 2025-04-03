# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 12:17:03 2024

@author: marce
"""


import agentpy as ap


class Governement(ap.Agent):
    
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
        
        self.consumption_budgets = {}
        self.consumption_shares = {}
        
        
    def make_period_account(self):
        
        self.liquidity += self.taxes
        
        self.taxes = 0
        


    def distribute_transfers(self):
        
        transfers = self.average_wage*self.transfer_fraction*len(self.model.Households_agents)
        
        transfers_h = self.average_wage*self.transfer_fraction
        
        if(self.liquidity < transfers):
            
            if(self.liquidity>0):
            
                transfers_h = transfers/self.liquidity
            else:
                transfers_h = 0
            
        for h in self.model.Households_agents:
            
            h.reveice_transfer(transfers_h)
        
        
    def distribute_unemployment_benefits(self):
        
        unemployed_list = self.model.Hosehold_agents.select(self.model.Hosehold_agents.flag_employed == 0)
        
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
            
         
        
        
    def buy(self, commodity):
        
        if(self.consumption_budgets[commodity] > 0):
            
            sellers_list = self.model.localKAU_agents.select(self.model.localKAU_agents.my_commodity == commodity and self.model.localKAU_agents.supply>0)

            n_sellers = len(sellers_list)
            
            if(n_sellers > 0):
                
                demand = self.consumption_budgets[commodity]/n_sellers
                
                for s in sellers_list:
                    
                    price = s.get_price()
                    
                    demanded_quantity = demand/price
                    
                    bought_quantity = s.sell(demanded_quantity)
                    
                    expenditure = bought_quantity*price
                    
                    self.consumption_budgets[commodity] -= expenditure
                    self.liquidity -= expenditure
        
                    

                    
    def reset_market_vars(self):
        
        pass
    
    def update_sellers_list(self, commodity):
        
        pass
       

    def receive_taxes(self, amount):
        
        self.taxes += amount
        
        

        
        

        
    

        
        
        
    
    
    