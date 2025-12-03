# -*- coding: utf-8 -*-
"""
Created on Tue May  2 19:29:49 2023

@author: marce
"""
import random as random
import agentpy as ap
import numpy as np
import math as math

class Household(ap.Agent):
    
    def setup(self):
        # STOCKS
        self.wealth = 0
        self.property_shares = {}
        
        # FLOWS
        self.income = 0
        self.wage = 0
        self.dividends = 0
        self.consumption = 0

        # PARAMETERS AND OTHER VARIABLES
        self.consumption_budget = 0
        self.wealth2income_target = 0 
        self.csi = 0
        self.consumption_budgets = {}
        self.consumption_shares = {}
        self.consumptions_qt = {}
        self.consumption_from_RoW = {}
        
        self.my_seller = {}
        self.attempt_number = 0
        self.rationing_level = 0
        self.rationing_threshold = 0
        self.sellers_list = {}
        self.field_of_view = 0
        self.memory_loss = 0
        self.opportunism_degree = 0
        
        self.employer_id = -1
        self.flag_employed = 0
        self.wage = 0
        self.gov_transfer = 0
        
        self.my_bank = object()
        
        
    def determine_consumption_budgets(self):
        
        self.determine_disposable_income()
        
        self.consumption = 0
        #self.income = self.dividends + self.wage
        self.dividends = 0
        self.wage = 0
        self.consumption_budget = self.disposable_income + self.csi*(self.wealth - self.income - self.wealth2income_target*self.disposable_income)
        if(self.consumption_budget<0):
            self.consumption_budget = 0
        
        for k in self.consumption_shares.keys():
            
            self.consumptions_qt[k] = 0
            self.consumption_budgets[k] = self.consumption_budget*self.consumption_shares[k]

    
    def update_sellers_list(self, commodity):
        
        #remove randomly elements from the list
        
        n_removed_max = round(len(self.sellers_list[commodity])*self.memory_loss)


        if(n_removed_max>0):
            n_removed = n_removed_max#np.random.randint(n_removed_max)
            
            for i in range(n_removed):
                self.sellers_list[commodity].pop()   #np.random.randint(len(self.sellers_list[commodity])))   # if you want to remove first elements give to pop() 0 as argument
                
            
        # uppend new sellers in the list
        
            #new_sellers = self.model.localKAU_agents.random(n_removed_max)
            n_added = 0
            for new_s in self.model.localKAU_agents.random(len(self.model.localKAU_agents)):
                if(not(new_s in self.sellers_list[commodity])):
                    self.sellers_list[commodity].append(new_s)
                    n_added += 1
                    if(n_added == n_removed):
                        break
                    
            
        # sort sellers by price
        
        self.sellers_list[commodity].sort(key = lambda seller: seller.price)

        
    def change_my_seller(self, commodity):
        
        
        new_seller = self.sellers_list[commodity][0]
        
        if(new_seller.id == self.my_seller[commodity].id and len(self.sellers_list[commodity])>1):
            
            self.my_seller[commodity] = self.sellers_list[commodity][1]
            
        else:
            self.sellers_list[commodity].remove(new_seller)
            self.sellers_list[commodity].append(self.my_seller[commodity])            
            self.my_seller[commodity] = new_seller
            
        print(self.id, 'I changed my seller')       


    def reset_market_vars(self):
        
        self.attempt_number = 0
        self.rationing_level = 0


    def buy(self, commodity):
        
            
        
        if(self.attempt_number == 0):
            
            
            self.buy_from_RoW(commodity)
            
            r = np.random.random()
            
            if(r< self.opportunism_degree):
                
                self.change_my_seller(commodity)
                        
            self.buy_from_seller(self.my_seller[commodity], commodity, True)

        
        elif(self.attempt_number == 1):
                                                
            if(self.rationing_level > self.rationing_threshold):
                print(self.id, 'I am rationed')
                self.change_my_seller(commodity)
                
                self.buy_from_seller(self.my_seller[commodity], commodity, True)
                
            else:                    
                
                self.buy_from_sellers_list(commodity)
                
        else:
             
             self.buy_from_sellers_list(commodity)
             
        self.attempt_number +=1
                 
                 
    def buy_from_RoW(self, commodity):
        
        RoW = self.model.RoW[0]
        price = RoW.get_price(commodity)
        demanded_quantity = self.consumption_from_RoW[commodity]*self.consumption_budgets[commodity]/price        
        bought_quantity = RoW.sell(commodity, demanded_quantity)
                    
        self.consumptions_qt[commodity] += bought_quantity
        
        consumption = bought_quantity*price
        self.consumption += consumption
        self.wealth -= consumption
        self.my_bank.deposits[self.id] -= consumption
        
        self.consumption_budgets[commodity] -= consumption        


    def buy_from_sellers_list(self, commodity):

        for seller in self.sellers_list[commodity]:
            
            if(seller.supply>0):
                                           
                self.buy_from_seller(seller, commodity, False)
                
                break   



    def buy_from_seller(self, seller, commodity, is_my_seller):
        
        
        price = seller.get_price()
        demanded_quantity = self.consumption_budgets[commodity]/price
        bought_quantity = seller.sell(demanded_quantity)
        
        if(is_my_seller == True and demanded_quantity > 0):
            
            self.rationing_level = 1 - bought_quantity/demanded_quantity
            #print(self.id, 'I am writing rationing level = ',self.rationing_level )
            
        self.consumptions_qt[commodity] += bought_quantity
        
        consumption = bought_quantity*price
        self.consumption += consumption
        self.wealth -= consumption
        self.my_bank.deposits[self.id] -= consumption
        
        self.consumption_budgets[commodity] -= consumption
   
        
    def receive_dividends(self, dividends):
        
        self.dividends += dividends
        self.wealth += dividends
        self.my_bank.deposits[self.id] += dividends

        
    def receive_wage(self, wage):
        
        self.wage = wage
        self.wealth += wage
        self.my_bank.deposits[self.id] += wage
        
    def receive_unemployment_benefit(self, ub):
        
        self.wage = ub
        self.wealth += ub
        self.my_bank.deposits[self.id] += ub  
        
    def reveice_transfer(self, transfer_amount):
        
        self.gov_transfer = transfer_amount
        self.wealth += transfer_amount
        self.my_bank.deposits[self.id] += transfer_amount       
         
        
    def search_job(self):
                
        employers = self.model.localKAU_agents.select(self.model.localKAU_agents.flag_vacancies == 1)

        if(len(employers) > 0):
            for employer in employers.random(1):
                #employer = employers.random(1)[0]            
                employer.hire(self)            
                self.flag_employed = 1
                self.employer_id = employer.id
                break
        
    def update_employement_status(self):
        
        self.flag_employed = 0
        self.employer_id = -1
        
        
    def determine_disposable_income(self):
        
        self.income = self.dividends + self.wage + self.gov_transfer
        
        rates = self.model.Government[0].tax_rates['labor']
        my_income_rate = 0
        
        if(self.flag_employed != 0):
            for i, inc_class in enumerate(rates.keys()):
                
                if(self.income < inc_class):
                    
                    my_income_rate = rates[inc_class]
                    break
                
        self.labor_tax = self.wage*my_income_rate        
        
        self.dividend_tax = self.dividends*self.model.Government[0].tax_rates['dividends']
        
        self.disposable_income = self.income - self.labor_tax - self.dividend_tax
        
    def pay_taxes(self):
        
        
        self.wealth -= self.labor_tax
        self.my_bank.deposits[self.id] -= self.labor_tax
        
        self.wealth -= self.dividend_tax
        self.my_bank.deposits[self.id] -= self.dividend_tax
        self.model.Government[0].receive_taxes(self.labor_tax + self.dividend_tax)
        