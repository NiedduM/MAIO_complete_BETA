# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:04:52 2023

@author: marce
"""


class Loan(object):
    
    def __init__(self, granted_amount, remaining_amount, interest_rate, id_bank, id_firm, remaining_time, weighted_KAU_list):
        
        self.granted_amount = granted_amount
        self.remaining_amount = remaining_amount
        self.interest_rate = interest_rate
        self.id_bank = id_bank
        self.id_firm = id_firm
        self.remaining_time = remaining_time
        self.weighted_KAU_list = weighted_KAU_list
        
    def determine_payment(self):
        
        return self.interest_rate/(1-pow(1+self.interest_rate, -self.remaining_time))*self.remaining_amount
    
    def determine_interest_payment(self):
    
        return self.interest_rate*self.remaining_amount
    
    def determine_capital_payment(self):
        
        total = self.determine_payment()
        interest = self.determine_interest_payment()
        
        return total-interest
    
    def execute_payment(self):
        
        payment = self.determine_payment()
        print(payment)
        self.remaining_amount = (1+self.interest_rate)*self.remaining_amount - payment
        
        
        #self.remaining_amount 
        
        