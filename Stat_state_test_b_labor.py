# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 12:01:32 2025

@author: marce
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov 29 16:02:26 2025

@author: marce
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 11:12:25 2024

@author: marce
"""

import numpy as np
import matplotlib.pyplot as plt
from NewExperimenter import Experimenter
import math as math

%matplotlib

Galileo = Experimenter() 


seed = 2
Y = 100
n_sector = 3


# ROW

GDP_RoW = 1000
RoW_price = np.ones(n_sector)
c_RoW = 0#0.02
alpha_RoW = 0*np.array([0.35, 0.25, 0.4])


# KAU

C = np.array([[0.1, 0.2, 0.3],[0.05, 0.1, 0.12],[0.05, 0.1, 0.05]])


delta = np.array([[0, 0, 0],[0, 0, 0],[0.01, 0.01, 0]]) #capital depreciation

gamma = np.array([[0, 0, 0],[0, 0, 0],[0.1, 0.15, 0]]) #capital tech coeff

cap_ut = np.ones((n_sector,n_sector)) #np.array([[0, 0, 0],[0, 0, 0],[0.9, 0.9, 0]]) #capital target capacity utilization

# delta = np.zeros((n_sector,n_sector))
# gamma = delta
# cap_ut = delta

cap_target_speed = 0*np.array([0.05, 0.05, 0])

KAU_price = np.ones(n_sector).reshape(n_sector, 1)
wages = np.ones(n_sector).reshape(n_sector, 1)
labor_tech_coeff = np.array([0.1, 0.2, 0.1]).reshape(n_sector, 1)

KAU_from_RoW = np.zeros((n_sector,n_sector))# np.array([[0.0, 0.2, 0.3],[0.1, 0, 0.2],[0, 0.2, 0]])

# HOUSEHOLDS

n_households = 50
lambdaT = np.array([5 for k in range(n_households)])
csi = np.array([0.1 for k in range(n_households)])
alpha = np.array([0.5, 0.2, 0.3])


H_from_RoW = 0*np.array([0.1, 0.2, 0.1])


# GOVERNMENT


alpha_gov = np.array([0.3, 0.2, 0.5])

Gov_from_RoW = 0*np.array([0.2, 0.1, 0.1])


tax_rates = {}
tax_rates['corporate'] = 0.0
tax_rates['VAT'] = 0.0*np.ones(n_sector)
tax_rates['dividends'] = 0.0
tax_rates['labor'] = {math.inf: 0.0}

ub_frac = 0.0
transfer_frac = 0.0


params = Galileo.create_initcond_simplified(seed, Y, GDP_RoW, RoW_price, c_RoW, alpha_RoW, n_sector, C, delta, gamma, cap_ut, cap_target_speed, KAU_price, wages, labor_tech_coeff, KAU_from_RoW, n_households, lambdaT, csi, alpha, H_from_RoW, alpha_gov, Gov_from_RoW, tax_rates, ub_frac, transfer_frac)


n_steps = 100
folder_path = 'Experiments/Test/SteadyState/b_labor'
results = Galileo.execute_single_scenario(params, n_steps, folder_path)



