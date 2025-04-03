# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:13:48 2023

@author: marce
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 10:42:28 2023

@author: giaco
"""

import agentpy as ap
import numpy as np
import Loan as Loan

class Bank(ap.Agent):

    def setup(self):
        
        # balance sheet variables
        self.loans = []
        self.reserves = 0
        self.total_deposits = 0
        self.equity = 0
        self.deposits = {}
        
        
        # behavioural variables 
        self.CAR = 0                    
        self.threshold = 0
        self.interest_rate = 0
        
        self.repayment_time = 0
        
        self.interests_payment = 0
        self.dividends = 0
        
    def evaluate_request(self, firm,  credit_requested):
            
        
        # firm_equity = firm.equity
        # firm_debt = sum([ln.remaining_amount for ln in firm.loans_list])       
        
        # #Calculate the total debt of the company after granting the credit
            
        # new_firm_debt = firm_debt + credit_requested
            
        # pi_firm = new_firm_debt / (new_firm_debt + firm_equity)
        # firm_risk_weight = pi_firm
            
            
        #     #verify Basil II condition 
        # if(self.equity >= self.CAR*(0.9*self.loans + firm_risk_weight*credit_requested) ):


        if(self.threshold>0):                
            new_loan = Loan.Loan(credit_requested,credit_requested, self.interest_rate, self.id, firm.id, self.repayment_time+1, [])
                
            self.loans.append(new_loan)
            
            return new_loan
            
        else:
            
            new_loan = Loan.Loan(0,0, self.interest_rate, self.id, firm.id, self.repayment_time+1)
            return new_loan
   
   

    def receive_payment(self, total_payment, interest_payment):

        self.reserves += interest_payment#total_payment        
        self.interests_payment += interest_payment
        #print(self.interests_payment, self.reserves)
        
    
    def distribute_dividends(self):
    
        self.dividends = self.interests_payment
        self.interests_payment = 0
        
        div_h = self.dividends/len(self.model.Household_agents)
        for ag_h in self.model.Household_agents:
            ag_h.receive_dividends(div_h)    
            
        self.reserves -= self.dividends    
            
    def update_loans_list(self):
        
        for ln in self.loans:
            
            if(ln.remaining_time == 0):
                
                self.loans.remove(ln)
                
                
                
    def compute_total_deposits(self):
        
        self.total_deposits = sum(self.deposits.values())