# -*- coding: utf-8 -*-
"""
Created on Tue May  2 19:44:17 2023

@author: marce
"""
import numpy as np
import agentpy as ap

import Firm as Fm
import Household as Hh
import LocalKAU_ordinato as lKAU
import Bank as Bk
import Government as Gov
import RoW as RoW

class MyModel(ap.Model):
    
    def setup(self):
        
        
        self.Firm_agents = ap.AgentList(self, self.p.nFirms, Fm.Firm)
        self.Household_agents = ap.AgentList(self, self.p.nHouseholds, Hh.Household)
        
        if(self.p.KAUtype == 'unitcost'):
            self.localKAU_agents = ap.AgentList(self, self.p.nKAUs, lKAU.LocalKAU_unitcost)
        elif(self.p.KAUtype == 'price'):
            self.localKAU_agents = ap.AgentList(self, self.p.nKAUs, lKAU.LocalKAU_price)
        
        
        self.Bank_agents = ap.AgentList(self, self.p.nBanks, Bk.Bank)
        
        self.Government = ap.AgentList(self, 1, Gov.Government)
        
        self.RoW = ap.AgentList(self, 1, RoW.RoW)
        
        
        self.buyer_agents = self.Household_agents + self.localKAU_agents + self.Government + self.RoW
        
        self.nBuyers = self.p.nKAUs + self.p.nHouseholds + 2
        
        self.seller_agents = self.localKAU_agents + self.RoW
        
        
        self.round_number = self.p.round_number
        
        for i,lk in enumerate(self.localKAU_agents):
            
            # assegnazione prodotti a KAU
            lk.my_activity = self.p.KAUactivity_list[i]
            lk.my_commodity = self.p.KAUcommodity_list[i]        
        
            # assegnazione KAU a firm
            owner = self.Firm_agents[self.p.KAUFirm_list[i]]
            owner.KAU_list.append(lk)
            lk.my_firm = owner
            
        self.initialize_firms()
        self.initialize_localKAUs()
        self.initialize_households()
        self.initialize_banks()
            
        self.Government.liquidity = self.p.Gov_var['liquidity']
        self.Government.tax_rates = self.p.Gov_var['tax_rates'].copy()
        self.Government.consumption_shares = self.p.Gov_var['consumption_shares'].copy()

        self.RoW.liquidity = self.p.RoW_var['liquidity']
        self.RoW.suppliers_weights = self.p.RoW_var['suppliers_weights'].copy()
        self.RoW.consumption_shares = self.p.RoW_var['consumption_shares'].copy()

        
        self.shocks_counter = 0
            
    def initialize_firms(self):
        
        for i,f in enumerate(self.Firm_agents):
            
            f.wealth = self.p.Firms_var['wealth'][i]
            f.set_cash_for_KAUs()
            f.create_dictionaries()
            selected = np.random.randint(0,high = self.p.nBanks)
            f.my_bank = self.Bank_agents[selected]
            f.loans_list = self.p.Firms_var['loans'][i].copy()
            for l in f.loans_list:
                print(l.remaining_amount)
                l.id_bank = f.my_bank.id
                l.id_firm = f.id
                l.weighted_KAU_list = dict([(lk.id, 1/len(f.KAU_list) ) for lk in f.KAU_list] )
        
            
    def initialize_localKAUs(self):
        
        for i, lk in enumerate(self.localKAU_agents):
            
            lk.commodities_stock = self.p.localKAUs_var['commodities_stock'][i].copy()
            lk.capital_stocks = self.p.localKAUs_var['capital_stock'][i].copy()
            
            lk.tech_coeff = self.p.localKAUs_var['tech_coeff'][i].copy()
            lk.capital_coeff = self.p.localKAUs_var['capital_coeff'][i].copy()
            lk.capital_depreciation = self.p.localKAUs_var['capital_depreciation'][i].copy()
            
            lk.prices = self.p.localKAUs_var['prices'].copy()
            lk.price = lk.prices[lk.my_commodity]
            
            
            lk.unit_cost = 0
            
            if(self.p.KAUtype == 'unitcost'):
                for k in lk.tech_coeff.keys():
                    if(k != lk.my_commodity):
                        lk.unit_cost += lk.tech_coeff[k]*lk.prices[k]
                        lk.commodities_stock_value[k] = lk.commodities_stock[k]*lk.prices[k]
                        
                lk.unit_cost = lk.unit_cost/(1-lk.tech_coeff[lk.my_commodity])
                lk.commodities_stock_value[lk.my_commodity] = lk.unit_cost*lk.commodities_stock[lk.my_commodity]
                
            else:
                for k in lk.tech_coeff.keys():
                    lk.unit_cost += lk.tech_coeff[k]*lk.prices[k]
                    lk.commodities_stock_value[k] = lk.commodities_stock[k]*lk.prices[k]
                    lk.capital_stocks_value[k] = lk.capital_stocks[k]*lk.prices[k]
            

            
            lk.my_commodity_stock_value_old = lk.commodities_stock_value[lk.my_commodity]
            
            lk.previous_demand = self.p.localKAUs_var['previous_demand'][i] #.copy()
            lk.expected_demand = lk.previous_demand
            #lk.demand_change = lk.previous_demand
            
            lk.markup = self.p.localKAUs_var['markup'][i]
            
            lk.independence_periods = self.p.localKAUs_var['independence_periods'][i]
            lk.target_capacity_utilization = self.p.localKAUs_var['target_capacity_utilization'][i]
            
            lk.target_speed = self.p.localKAUs_var['target_speed'][i]
            lk.markup_speed = self.p.localKAUs_var['markup_speed'][i]
            lk.earnings = self.p.localKAUs_var['earnings'][i]
            
            lk.my_seller = {}#self.p.localKAUs_var['my_seller'][i].copy()     
            
            
            for com in self.p.localKAUs_var['my_seller'][i].keys():
                
                index = int(self.p.localKAUs_var['my_seller'][i][com])
                lk.my_seller[com] = self.seller_agents[index]
            
            lk.rationing_threshold = self.p.localKAUs_var['rationing_threshold'][i]
            lk.field_of_view = self.p.localKAUs_var['field_of_view'][i]
            lk.memory_loss = self.p.localKAUs_var['memory_loss'][i]
            lk.opportunism_degree = self.p.localKAUs_var['opportunism_degree'][i]        
            
            for k in lk.tech_coeff.keys():
                
                lk.inputs_consumption[k] = 0
                lk.demanded_quantity[k] = 0
                lk.total_expenditure[k] = 0
                
                lk.capital_purchase[k] = 0
                lk.capital_demanded_quantity[k] = 0
                lk.total_demanded_quantity[k] = 0
                
                
                n_seller = round(lk.field_of_view*len(self.localKAU_agents.select(self.localKAU_agents.my_commodity == k)))
                n_seller = max(1,n_seller)
                list_seller = self.localKAU_agents.select(self.localKAU_agents.my_commodity == k).random(n_seller)
                lk.sellers_list[k] = [s for s in list_seller]
            
            lk.sellers_list.append(self.RoW)
            
            lk.wage_offer = self.p.localKAUs_var['wage_offer'][i]
            lk.labor_tech_coeff = self.p.localKAUs_var['labor_tech_coeff'][i]
            
            
                
    def initialize_households(self):
        
        for i,h in enumerate(self.Household_agents):
                        
            h.property_shares = dict(zip(self.Firm_agents.id ,self.p.Households_var['property_shares'][i].copy()))
            h.wealth = self.p.Households_var['wealth'][i]
            #h.dividends = self.p.Households_var['dividends'][i]
            h.wealth2income_target =  self.p.Households_var['wealth2income_target'][i]
            h.csi = self.p.Households_var['csi'][i]
            h.consumption_shares = self.p.Households_var['consumption_shares'][i].copy()
            
            h.my_seller = self.p.Households_var['my_seller'][i].copy()
            
            for com in self.p.Households_var['my_seller'][i].keys():
                
                index = int(self.p.Households_var['my_seller'][i][com])
                h.my_seller[com] = self.seller_agents[index]
                
            h.rationing_threshold = self.p.Households_var['rationing_threshold'][i]
            h.field_of_view = self.p.Households_var['field_of_view'][i]
            h.memory_loss = self.p.Households_var['memory_loss'][i]
            h.opportunism_degree = self.p.Households_var['opportunism_degree'][i]        

            
            for k in h.consumption_shares.keys():
                n_seller = round(h.field_of_view*len(self.localKAU_agents.select(self.localKAU_agents.my_commodity == k)))
                n_seller = max(1,n_seller)
                list_seller = self.localKAU_agents.select(self.localKAU_agents.my_commodity == k).random(n_seller)
                h.sellers_list[k] = [s for s in list_seller]
            h.sellers_list.append(self.RoW)
                #print([sell.id for sell in h.sellers_list[k]])
                
            selected = np.random.randint(0,high = self.p.nBanks)
            h.my_bank = self.Bank_agents[selected]
            
            employer_id = self.p.Households_var['employer'][i]
            
            if(employer_id >= 0):
                employer = self.localKAU_agents[self.p.Households_var['employer'][i]]
                h.employer_id = employer.id
                h.flag_employed = 1                
                employer.employees_list.append(h)

    def initialize_banks(self):
        
        for i,b in enumerate(self.Bank_agents):
            
            
            for f in self.Firm_agents:
                
                for ln in f.loans_list:
                    if(ln.id_bank == b.id):
                        b.loans.append(ln)
            
            b.reserves = self.p.Banks_var['reserves'][i] 
            
            for h in self.Household_agents.select(self.Household_agents.my_bank.id == b.id):
                b.deposits[h.id] = h.wealth
                
            for f in self.Firm_agents.select(self.Firm_agents.my_bank.id == b.id):
                b.deposits[f.id] = f.wealth                
            
            
            b.total_deposits = sum([b.deposits[ag] for ag in b.deposits.keys()])    
                
            loans_sum = sum([ln.remaining_amount for ln in b.loans])
            
            b.equity = loans_sum + b.reserves - b.total_deposits
            
            b.CAR = self.p.Banks_var['CAR'][i]
            b.interest_rate = self.p.Banks_var['interest_rate'][i]
            b.threshold = self.p.Banks_var['threshold'][i]
            b.repayment_time = self.p.Banks_var['repayment_time'][i]




            
    def step(self):
        
        
        
        if(self.p.shocks['active']):
            
            if(self.shocks_counter < self.p.shocks['number'] and np.mod(self.t-2, self.p.shocks['frequency']) == 0):                
                
                if(self.p.shocks['agents'] == 'Household'):               
                    
                    self.Household_agents.wealth += self.p.shocks['quantity']/self.p.nHouseholds
                    self.shocks_counter += 1
                    print(self.t, ' Shocks activated')
        
        self.localKAU_agents.form_demand_expectation()
        
        self.localKAU_agents.make_plans()
        
        self.localKAU_agents.compute_liquidity_needs()
        
        self.Firm_agents.send_credit_request()
        
        # Labor market round
        self.Household_agents.select(self.Household_agents.flag_employed ==0).search_job()
 
        
        self.Firm_agents.execute_financial_payments()
        
        self.Bank_agents.distribute_dividends()
        
        self.localKAU_agents.produce()
        
        self.localKAU_agents.set_price()
        
        self.Household_agents.determine_consumption_budgets()
                
        self.localKAU_agents.adjust_demanded_quantity()
        
        self.localKAU_agents.depreciate_capital()
        
        self.Government.distribute_unemployment_benefits()
        
        self.Government.distribute_transfers()
        
        self.Government.determine_consumption_budgets()
        
        self.Row.determine_consumption_budgets()
        
        for commodity in self.p.commodities_list:
            
            self.buyer_agents.reset_market_vars()
            self.buyer_agents.update_sellers_list(commodity)          
            for n in range(self.round_number):
                self.buyer_agents.random(self.nBuyers).buy(commodity)
                
                        
        self.localKAU_agents.update_prices()
        
        self.localKAU_agents.compute_earinings()        
        
        self.localKAU_agents.revaluate_inputs_stocks()
        
        self.Firm_agents.update_loans_age()
        
        self.Bank_agents.update_loans_list()
        
        self.Household_agents.pay_taxes()
        
        self.localKAU_agents.pay_taxes()
        
        self.Government.make_period_account()
        
        
    def update(self):
        
        
        # MACRO VARIBLES
        self.record('Nominal Production', sum(self.localKAU_agents.production*self.localKAU_agents.price))
        self.record('Total Revenues', sum(self.localKAU_agents.revenues))
        #self.record('Intermediate consumption', sum(sum([self.localKAU_agents.inputs_consumption[k] for k in self.localKAU_agents.inputs_consumption.keys()])))
        self.record('Total costs', sum(self.localKAU_agents.total_costs))
        self.record('GDP', sum(self.Household_agents.income))
        self.record('Firms liquidity', sum(self.Firm_agents.wealth))
        self.record('Households liquidity', sum(self.Household_agents.wealth))
        self.record('Total liquidity',sum(self.Firm_agents.wealth) +  sum(self.Household_agents.wealth))
        #@self.record('Integral', self.calculate_integral())
        self.record('Consumption', sum(self.Household_agents.consumption))
        
        # SECTORIAL VARIABLES
        for com in self.p.commodities_list:
            self.record('Real production of '+ com, sum(self.localKAU_agents.select(self.localKAU_agents.my_commodity == com).production))
            #self.record('Nominal production of'+ com, sum(self.localKAU_agents.select(self.localKAU_agents.my_commodity == com).production*self.localKAU_agents.select(self.localKAU_agents.my_commodity == com).price)            
        
        # FIRMS
        
        self.Firm_agents.record('wealth')
        self.Firm_agents.compute_total_debt()
        self.Firm_agents.record('debt',)
        self.Firm_agents.compute_wealth_from_dep()
        self.Firm_agents.record('deposit')
        self.Firm_agents.record('dividends')
    
        # HOUSEHOLDS   
     
        self.Household_agents.record('consumption')
        self.Household_agents.record('wealth')
        self.Household_agents.record('income')
        # self.Household_agents.record('consumption_budget')       
 
        # # LOCAL KAU VARIABLES
       
        self.localKAU_agents.record('production')
        self.localKAU_agents.record('price')
        self.localKAU_agents.record('markup')
        self.localKAU_agents.record('supply')
        self.localKAU_agents.record('previous_demand')
        self.localKAU_agents.record('earnings')
        
        for lk in self.localKAU_agents:
            lk.record('no_employees', len(lk.employees_list))
        
        for lk in self.localKAU_agents:
            for com in self.p.commodities_list:
                lk.record(com+' stock', lk.commodities_stock[com])
        
        int_cons = 0
        for lk in self.localKAU_agents:
            for com in self.p.commodities_list:
                lk.record( com + ' consumption', lk.inputs_consumption[com])
                int_cons += lk.inputs_consumption[com]
        self.record('Int_cons', int_cons)
        
        for f in self.Firm_agents:
            for lk in f.KAU_list:
                lk.record('wealth', f.cash_for_KAU[lk.id])
                
                
        ## BANK VARIABLES
        
        # self.Bank_agents.record('dividends')
        # self.Bank_agents.record('reserves')
        # self.Bank_agents.compute_total_deposits()
        # self.Bank_agents.record('total_deposits')
                
                
    def calculate_integral(self):
        
        integral = 0
        
        for com in self.p.commodities_list:
            for lk in self.localKAU_agents:
                integral += lk.inputs_consumption[com]
            
        integral += sum(self.Household_agents.consumption_budget)
        integral += sum(self.Household_agents.wealth)
        
        return integral
       
        
    def end(self):
        
        self.Household_agents.record('wealth')
        self.Household_agents.record('income')        
        
        return
        