
 # -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 16:37:33 2023

@author: Squilibrati
"""


import numpy as np
import agentpy as ap
import random as random

import math as math #updated 3 Jun 24 

class LocalKAU(ap.Agent):
    
    def setup(self):
        
        #STOCKS      
        self.commodities_stock = {}
        self.commodities_stock_value = {}

        
        #FLOWS
        self.previous_demand = 0
        self.production_planned = 0
        self.supply = 0        
        self.production = 0  
        self.total_costs = 0
        self.revenues = 0
        self.earnings = 0
        self.sold_quantity = 0 
        self.inputs_consumption = {}
        self.total_expenditure = {}
        self.demanded_quantity = {}


        #PRICES
        self.prices = {}  
        self.price = 0        
        self.my_commodity_stock_value_old = 0
        self.unit_cost = 0        
        self.markup = 0
        
        # PARAMETERS
        self.tech_coeff = {}      

        
        self.my_activity = ''
        self.my_commodity = ''
        self.owner_id = -1
       
        self.my_seller = {}
        self.attempt_number = 0
        self.rationing_level = 0
        self.rationing_threshold = 0
        self.sellers_list = {}
        self.field_of_view = 0
        self.memory_loss = 0
        self.opportunism_degree = 0
        
        self.expected_demand = 0
        self.independence_periods = 0
        self.target_speed = 0
        self.expectation_error = 0        
        self.target_stock = {}
        
        # CAPITAL
        self.capital_coeff = {}
        self.capital_depreciation = {}     
        self.target_capital = {}
        self.capital_purchase = {}
        self.capital_demanded_quantity =  {}
        self.capital_stocks = {}
        self.capital_stocks_value = {}
        self.capacity_utilization_target = 0
        self.capital_quote = 0
        self.total_demanded_quantity = {}
        
        self.my_firm = object()
        
        # Labor
        self.flag_vacancies = 0
        self.wage_offer = 0
        self.labor_demand = 0
        self.employees_list = []
        self.labor_tech_coeff = 0
        self.max_straordinari = 0.3

##############################
# DEMAND EXPECTATIONS FORMATION
##############################
 
    def form_demand_expectation(self):
        
        self.expectation_error = self.previous_demand - self.expected_demand
        if(self.previous_demand == 0):
            if(self.expected_demand == 0):
                self.expectation_error = 0 
            else:
                self.expectation_error = -1
        else:
            self.expectation_error = self.expectation_error/self.previous_demand
        
        self.expected_demand = self.previous_demand
        
        self.previous_demand = 0
        

##############################
# PLANS METHODS
##############################

    def set_stock_targets(self):
    
        for comm in self.commodities_stock.keys():
        
            self.target_stock[comm] = self.independence_periods*self.tech_coeff[comm]*self.expected_demand/(1-self.tech_coeff[self.my_commodity])
 
    def set_capital_targets(self):
        
        for comm in self.capital_stock.keyes():
            
            self.target_capital[comm] = self.capital_coeff*self.expected_demand/((1-self.tech_coeff[self.my_commodity])*self.capacity_utilization_target)


    def plan_production(self):
                
        delta_stock = self.target_speed*(self.target_stock[self.my_commodity] - self.commodities_stock[self.my_commodity])
        
        delta_capital_stock = 0
        if(self.capital_coeff[self.my_commodity]>0):
            delta_capital_stock = self.target_speed*(self.target_capital[self.my_commodity] - self.capital_stocks[self.my_commodity])
        
        self.production_planned = (self.expected_demand + delta_stock + delta_capital_stock)/(1-self.tech_coeff[self.my_commodity])
        self.production_planned = max(self.production_planned, 0)

        Prod_max = min([self.commodities_stock[k]/self.tech_coeff[k] if self.tech_coeff[k]!=0 else math.inf for k in self.commodities_stock.keys()])    #updated 3 Jun 24 
        Prod_max_capital = min([self.capital_stocks[k]/self.capital_coeff[k] if self.capital_coeff[k]!=0 else math.inf for k in self.commodities_stock.keys()])    #updated 3 Jun 24 
        self.production_planned = min(Prod_max, Prod_max_capital, self.production_planned)
        
        
    def plan_demanded_quantities(self):
    
        for comm in self.commodities_stock.keys():  # devo togliere il mio prodotto
        
            self.demanded_quantity[comm] = self.plan_demanded_quantity(comm)
        
    def plan_demanded_quantity(self, commodity):
        
        demanded_quantity = self.production_planned*self.tech_coeff[commodity] + self.target_speed*(self.target_stock[commodity] - self.commodities_stock[commodity])
        
        demanded_quantity = max(0,demanded_quantity)
        
        return demanded_quantity
    
    def plan_demanded_capital_quantities(self):
    
        for comm in self.commodities_stock.keys():  # devo togliere il mio prodotto
        
            self.capital_demanded_quantity[comm] = self.plan_demanded_capital_quantity(comm)
        
    def plan_demanded_capital_quantity(self, commodity):
        
        demanded_quantity = self.capital_stocks[commodity]*self.capital_depreciation[commodity] + self.target_speed*(self.target_capital[commodity] - self.capital_stocks[commodity])
        
        demanded_quantity = max(0,demanded_quantity)
        
        return demanded_quantity
    
    def plan_total_demanded_quantities(self):
        
        for comm in self.demanded_quantity.keys():
            self.total_demanded_quantity[comm] = self.demanded_quantity[comm] + self.capital_demanded_quantity[comm]
            #self.total_demanded_quantity[comm] = min(total_demand, self.my_firm.cash_for_KAU[self.id]/self.prices[comm])
            self.capital_quote = self.capital_demanded_quantity[comm]/self.total_demanded_quantity[comm]

    def plan_labor_demand(self):
        
        no_employees = len(self.employees_list)
        
        no_employees_needed = self.production_planned*self.labor_tech_coeff
        
        no_employees_gap = no_employees_needed - no_employees
        
        print('Test KAU ',self.id, no_employees,no_employees_needed, no_employees_gap)
        if(no_employees_gap<0):
            no_firings = int(-no_employees_gap)
            
            for i in range(no_firings):
                
                removed = self.employees_list.pop(np.random.randint(0, len(self.employees_list)))
                removed.update_employement_status()
        
            self.labor_demand = 0
            self.flag_vacancies = 0
            
        else:
            self.labor_demand = int(no_employees_gap) + 1
            self.flag_vacancies = 1        


    def make_plans(self):
    
        self.set_stock_targets()
        self.set_capital_targets()
        self.plan_production()
        self.plan_demanded_quantities()
        self.plan_demanded_capital_quantities()
        self.plan_total_demanded_quantities()
        self.plan_labor_demand()
        
        
##############################
# LIQUIDITY NEEDS
##############################        


    def compute_liquidity_needs(self):
        
        # liquidity for expanding the input-output stock
        liquidity_needs = self.price*self.target_speed*(self.target_stock[self.my_commodity] - self.commodities_stock[self.my_commodity])        
        liquidity_needs = max(0, liquidity_needs)
        
        
        #liquidity for inputs purchases
        for comm in self.commodities_stock.keys():
            
            if(comm != self.my_commodity):                
                
                liquidity_needs += self.prices[comm]*self.total_demanded_quantity[comm]
        
        # liquidity 4 labor payment
        
        liquidity_needs += self.wage_offer*self.production_planned*self.labor_tech_coeff
                
        
        
        self.my_firm.gather_KAU_request(self.id, liquidity_needs)
        
      
##############################
# HIRINGS AND WAGE PAYMENTS
##############################     

    def hire(self, ag):
        
        self.employees_list.append(ag)
        
        self.labor_demand -= 1
        
        if(self.labor_demand == 0):
            
            self.flag_vacancies = 0
        
        
      
    def pay_wages(self):
        
        self.total_wage_payment = self.wage_offer*self.production_planned*self.labor_tech_coeff
        
        wage4worker = self.total_wage_payment/len(self.employees_list)
        
        for wk in self.employees_list:
            
            wk.receive_wage(wage4worker)
            
        #self.my_firm.update_cash_for_KAU(self.id, - self.total_wage_payment)    
        
        print('wage payment', wage4worker)
        #ATTENZIONE: NECESSARIO METTERE UN CONTROLLO SU STOCK MONETA        
      
##############################
# PRODUCTION METHODS
##############################
        
    def produce(self):
                        
        # il calcolo di prod max non è necessario perchè l'ho già calcolato col piano produttivo
        if(self.labor_tech_coeff >0):
            self.production = min(self.production_planned, (1+ self.max_straordinari)*len(self.employees_list)/self.labor_tech_coeff)
        else:
            self.production = self.production_planned
        
        self.sold_quantity = 0
        self.revenues = 0
        self.total_costs = 0


        self.total_costs += self.total_wage_payment
        
        for k in self.commodities_stock.keys():
            
            self.commodities_stock[k] -= self.production*self.tech_coeff[k]
            if(k != self.my_commodity):
                self.total_costs += self.prices[k]*self.production*self.tech_coeff[k]
                self.commodities_stock_value[k] -= self.prices[k]*self.production*self.tech_coeff[k]
                
            
            
        self.commodities_stock[self.my_commodity] += self.production
        
        self.set_supply()
        
        
        
        for k in self.inputs_consumption.keys():
            self.inputs_consumption[k] = 0
            self.total_expenditure[k] = 0

         
        
    def set_supply(self):
        
        if(self.commodities_stock[self.my_commodity] > self.tech_coeff[self.my_commodity]*self.expected_demand/(1-self.tech_coeff[self.my_commodity])):
            self.supply = self.commodities_stock[self.my_commodity] - self.tech_coeff[self.my_commodity]*self.expected_demand/(1-self.tech_coeff[self.my_commodity])
        else:
            self.supply = self.commodities_stock[self.my_commodity] - 0.5*self.tech_coeff[self.my_commodity]*self.expected_demand/(1-self.tech_coeff[self.my_commodity])
        
        if(self.supply < 0):
            self.supply = 0




##############################
# PRICE SETTING METHODS #
##############################
       
    def set_price(self):
        
        pass
        
        
##############


##############################
# INTERMEDIATE GOODS DEMAND METHODS
##############################

    def adjust_demanded_quantity(self):
        
        total_planned_expenditure = 0
        
        for comm in self.total_demanded_quantity.keys():
            
            total_planned_expenditure += self.prices[comm]*self.total_demanded_quantity[comm]
             
        if(total_planned_expenditure> self.my_firm.cash_for_KAU[self.id]):
            
            factor = total_planned_expenditure/self.my_firm.cash_for_KAU[self.id]
            
            for comm in self.total_demanded_quantity.keys():
                
                self.total_demanded_quantity[comm] *= factor/self.prices[comm]


##############################
# GOODS MARKET METHODS
##############################
        
    def sell(self, demand):
        
        sold_quantity = 0
        if(demand>0):
            sold_quantity = min(self.supply, demand)
        
        self.supply -= sold_quantity
        self.commodities_stock[self.my_commodity] -= sold_quantity

        self.previous_demand += demand
        
        self.sold_quantity += sold_quantity
        self.revenues += self.price*sold_quantity

        self.my_firm.update_cash_for_KAU(self.id, self.price*sold_quantity)
        
        return sold_quantity


    def reset_market_vars(self):
        
        self.attempt_number = 0
        self.rationing_level = 0                  
    
    ## SELLERS LIST EVOLUTION
    
    def update_sellers_list(self, commodity):
        
        #remove randomly elements from the list
        
        n_removed_max = round(len(self.sellers_list[commodity])*self.memory_loss)

        #print(n_removed_max)
        
        if(n_removed_max>0):
            n_removed = n_removed_max#np.random.randint(n_removed_max)
            
            for i in range(n_removed):
                self.sellers_list[commodity].pop()#np.random.randint(len(self.sellers_list[commodity])))   # if you want to remove first elements give to pop() 0 as argument
                
            
        # uppend new sellers in the list
        
            # new_sellers = self.model.localKAU_agents.random(n_removed_max)
            
            # for new_s in new_sellers:
            #     if(not(new_s in self.sellers_list[commodity])):
            #         self.sellers_list[commodity].append(new_s)
                    
            n_added = 0
            for new_s in self.model.localKAU_agents.random(len(self.model.localKAU_agents)):
                if(not(new_s in self.sellers_list[commodity])):
                    self.sellers_list[commodity].append(new_s)
                    n_added += 1
                    if(n_added == n_removed):
                        break
            
        # sort sellers by price
        
        self.sellers_list[commodity].sort(key = lambda seller: seller.price)

    ##

    def buy(self, commodity):
        
        if(commodity != self.my_commodity):
            
            
            
            if(self.attempt_number == 0):
                
                r = np.random.random()
                
                if(r< self.opportunism_degree):
                    
                    self.change_my_seller(commodity)
                
                self.buy_from_seller(self.my_seller[commodity], commodity, True)
                
            
            elif(self.attempt_number == 1):
                
                if(self.rationing_level > self.rationing_threshold):
                    
                    self.change_my_seller(commodity)
                    
                    self.buy_from_seller(self.my_seller[commodity], commodity, True)
                    
                else:                    
                    
                    self.buy_from_sellers_list(commodity)
                    
            else:
                 
                 self.buy_from_sellers_list(commodity)
                 
            self.attempt_number +=1
            
    def change_my_seller(self, commodity):
        
        
        new_seller = self.sellers_list[commodity][0]
        
        if(new_seller.id == self.my_seller[commodity].id and len(self.sellers_list[commodity])>1):
            
            self.my_seller[commodity] = self.sellers_list[commodity][1]
            #self.sellers_list[commodity].remove(self.sellers_list[commodity][1])
            #self.sellers_list[commodity].append(self.my_seller[commodity])
            
        else:
            self.sellers_list[commodity].remove(new_seller)
            self.sellers_list[commodity].append(self.my_seller[commodity])            
            self.my_seller[commodity] = new_seller
            
        print(self.id, 'I changed my seller')             
                 
                 

    def buy_from_sellers_list(self, commodity):

        for seller in self.sellers_list[commodity]:
            
            if(seller.supply>0):
                                           
                self.buy_from_seller(seller, commodity, False)
                
                break                  
                    
    
    def buy_from_seller(self, seller, commodity, is_my_seller):
        
        
        price = seller.get_price()
        demanded_quantity = min(self.my_firm.cash_for_KAU[self.id]/price, self.total_demanded_quantity[commodity] )
        bought_quantity = seller.sell(demanded_quantity)
        
        if(is_my_seller == True and demanded_quantity > 0):
            self.rationing_level = 1 - bought_quantity/demanded_quantity
            #print(self.rationing_level)
                
        capital_bought_quantity = self.capital_quote[commodity]*bought_quantity
        inputs_bought_quantity = bought_quantity - capital_bought_quantity
        
        self.commodities_stock[commodity] += inputs_bought_quantity
        self.inputs_consumption[commodity] += inputs_bought_quantity
        
        self.capital_stocks[commodity] += capital_bought_quantity
        self.capital_purchase[commodity] += capital_bought_quantity
        
        self.total_demanded_quantity[commodity] -= bought_quantity
        expenditure = bought_quantity*price
        self.total_expenditure[commodity] += expenditure
        self.my_firm.update_cash_for_KAU(self.id, -expenditure)
        
        


##############################
# UPDATE PRICES 
##############################
            
    def update_prices(self):
        
        for commodity in self.commodities_stock.keys():
            
            if(self.inputs_consumption[commodity]>0):
                
                self.prices[commodity] = self.total_expenditure[commodity]/self.inputs_consumption[commodity]
                #print(self.prices[commodity])
            

##############################
# EARNINGS COMPUTATION
##############################
        
    def compute_earinings(self):
        
        
        self.my_commodity_stock_value_old = self.commodities_stock_value[self.my_commodity]
        
        self.update_my_stock()
        
        delta_stock = self.commodities_stock_value[self.my_commodity] - self.my_commodity_stock_value_old
        
        
        tax_rate = self.model.Government.tax_rates['VAT'][self.my_commodity]
        
        self.VAT = tax_rate/(1+tax_rate)*self.revenues
        
        self.earnings = max(0, self.revenues - self.total_costs + delta_stock)
        
        self.net_earnings = max(0, self.revenues -self.VAT - self.total_costs + delta_stock)
 
        self.income_tax = self.net_earnings*self.Government.tax_rates['corporate']

##############################
# REVALUATIONS METHODS
##############################


    def update_my_stock(self):
        
        pass
       
    
    def revaluate_inputs_stocks(self):
                
        for k in self.commodities_stock.keys():
            
            if(k!=self.my_commodity):
                self.commodities_stock_value[k] = self.prices[k]*self.commodities_stock[k]


    def depreciate_capital(self):
        
        for comm in self.capital_stocks.keys():
            
            self.capital_stocks[comm] *= (1-self.capital_depreciation[comm])
##############################
#  ACCESSORY METHODS
##############################

    def get_price(self):
        
        return self.price
    


class LocalKAU_price(LocalKAU):
    
    def setup(self):
        
        LocalKAU.setup(self)
        
        
    def compute_unit_cost(self):
        
        self.unit_cost = 0
        for k in self.commodities_stock.keys():
            self.unit_cost += self.prices[k]*self.tech_coeff[k]
            
        self.unit_cost += self.wage_offer*self.labor_tech_coeff
         
        
    def update_my_stock(self):
        
        self.commodities_stock_value[self.my_commodity] = self.commodities_stock[self.my_commodity]*self.price
        #print(self.commodities_stock_value[self.my_commodity], self.commodities_stock[self.my_commodity])
        
    def pay_taxes(self):
        
        expenditure = self.VAT + self.income_tax
        
        self.my_firm.update_cash_for_KAU(self.id, -expenditure)        
        
        self.model.Government.receive_taxes(expenditure)