# -*- coding: utf-8 -*-
"""
Created on Tue May  2 16:47:02 2023

@author: marce
"""

import agentpy as ap

class Firm(ap.Agent):
    
    def setup(self):
    
        self.KAU_list =[]
        self.wealth = 0
        self.cash_for_KAU = {}
        self.dividends = 0
        self.money_requests = {}
        self.equity = 0
        self.debt = 0
        self.loans_list = []
        self.KAU_debt_payment = {}
        self.KAU_dividends = {}
        
        self.my_bank = object()
        
        self.deposit = 0


    def create_dictionaries(self):
            
        for lk in self.KAU_list:
        
            self.money_requests[lk.id] = 0
            self.KAU_debt_payment[lk.id] = 0
            self.KAU_dividends[lk.id] = 0

        
    def set_cash_for_KAUs(self):
        
        numKAU = len(self.KAU_list)
        
        for lk in self.KAU_list:
            self.cash_for_KAU[lk.id] = self.wealth/numKAU
            
        
    def distribute_dividends(self):
        
        self.dividends = 0
        
        for lk in self.KAU_list:
            if(self.cash_for_KAU[lk.id] - self.KAU_dividends[lk.id] >= 0):
                self.dividends += self.KAU_dividends[lk.id]
                self.cash_for_KAU[lk.id] -= self.KAU_dividends[lk.id]
                self.KAU_dividends[lk.id] = 0
                if(self.cash_for_KAU[lk.id]<0):
                    print('Error')
            else:
                self.dividends += self.cash_for_KAU[lk.id]
                self.cash_for_KAU[lk.id] = 0
                self.KAU_dividends[lk.id] = 0
                if(self.cash_for_KAU[lk.id]<0):
                    print('Error')
            
            
        for ag_h in self.model.Household_agents:
            div_h = self.dividends*ag_h.property_shares[self.id]
            ag_h.receive_dividends(div_h)
        
        # Attenzione a possibili differenze tra sum div_h e self.dividends!!
        self.my_bank.deposits[self.id] -= self.dividends
        self.wealth -= self.dividends

        
    def update_cash_for_KAU(self, KAU_id, delta_cash):
        
        self.cash_for_KAU[KAU_id] += delta_cash
        self.wealth += delta_cash
        self.my_bank.deposits[self.id] += delta_cash
        
        
    def gather_KAU_request(self, KAU_id, request_amount):
      
        self.money_requests[KAU_id] = request_amount
        
        
    def reset_KAU_requests(self):
        
        for KAU_id in self.money_requests.keys():
            self.money_requests[KAU_id] = 0

    
    def send_credit_request(self):
        
        #calculate interests and debt payment for all KAUs
        capital_payback = 0
        interests = 0
        for d in self.loans_list:
            
            payment = d.determine_payment()
            interest_payment = d.determine_interest_payment()
            
            capital_payback += payment - interest_payment
            interests += interest_payment
            
            for lk in self.KAU_list:
                
                self.money_requests[lk.id] += d.weighted_KAU_list[lk.id]*(payment - interest_payment)
                
                self.KAU_debt_payment[lk.id] += d.weighted_KAU_list[lk.id]*payment
                
                self.KAU_dividends[lk.id] -= d.weighted_KAU_list[lk.id]*interest_payment
        
        for lk in self.KAU_list:
            
            self.money_requests[lk.id] += lk.net_earnings
            
            self.KAU_dividends[lk.id] += lk.net_earnings
            
            self.money_requests[lk.id] -= self.cash_for_KAU[lk.id]    
                

        total_credit_request = sum([val for val in self.money_requests.values()])
        
        
            

        if(total_credit_request > 0):
            
            print('\n Credit request ', total_credit_request)
            print('Capital repayment', capital_payback)
            print('Difference', capital_payback - total_credit_request, ' Interests', interests)
            new_loan = self.my_bank.evaluate_request(self, total_credit_request)
            
            
            weighted_KAU_list = dict([(k, self.money_requests[k]/total_credit_request) for k in self.money_requests.keys()] )

            
            if(new_loan.granted_amount >0):
                
                new_loan.weighted_KAU_list = weighted_KAU_list
                self.loans_list.append(new_loan)
                
                #self.wealth += new_loan.granted_amount
                
                for lk in self.KAU_list:
                    
                    self.update_cash_for_KAU(lk.id, new_loan.granted_amount*weighted_KAU_list[lk.id])
                    #self.cash_for_KAU[lk.id] += new_loan.granted_amount*weighted_KAU_list[lk.id]
                    
                    
        self.reset_KAU_requests()        


    def pay_wages(self):
        
        for lk in self.KAU_list:
            
            lk.pay_wages()
            self.update_cash_for_KAU(lk.id, -lk.total_wage_payment)



    def execute_financial_payments(self):        
        
        #print('execution', self.id)
        for k_id in self.KAU_debt_payment.keys():
            
            self.update_cash_for_KAU(k_id, -self.KAU_debt_payment[k_id])

            self.KAU_debt_payment[k_id] = 0
            
            
        for l in self.loans_list:
            
            if(l.remaining_time <= self.my_bank.repayment_time):
                #print(l.id_bank)
                b = self.model.Bank_agents.select(self.model.Bank_agents.id == l.id_bank)[0]
                #print(b.id)
                payment = l.determine_payment()
                interest_payment = l.determine_interest_payment()
                print(self.id)
                b.receive_payment(payment, interest_payment)
                l.execute_payment()
                
                
        self.pay_wages()
                
        self.distribute_dividends()
        
            
    def update_loans_age(self):
        
        for l in self.loans_list:
            
            l.remaining_time -= 1
            if(l.remaining_time == 0):
                self.loans_list.remove(l)
                

    def compute_total_debt(self):
        
        self.debt = sum([l.remaining_amount for l in self.loans_list])
        
        
                
    def compute_wealth_from_dep(self):
        
        self.deposit = self.my_bank.deposits[self.id]