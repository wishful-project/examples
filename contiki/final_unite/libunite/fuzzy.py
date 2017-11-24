import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


fused_estimation = ctrl.Antecedent(np.arange(0, 11, 1), 'fused_estimation')
kde_result = ctrl.Antecedent(np.arange(0, 11, 1), 'kde_result')
current = ctrl.Antecedent(np.arange(0, 11, 1), 'current')

pov = ctrl.Consequent(np.arange(0, 11, 1), 'pov')

fused_estimation['low'] = fuzz.trimf(fused_estimation.universe, [0, 0, 5])
fused_estimation['medium'] = fuzz.trimf(fused_estimation.universe, [2, 5, 8])
fused_estimation['high'] = fuzz.trimf(fused_estimation.universe, [5, 8, 10])

kde_result['low'] = fuzz.trimf(kde_result.universe, [0, 0, 5])
kde_result['medium'] = fuzz.trimf(kde_result.universe, [2, 5, 8])
kde_result['high'] = fuzz.trimf(kde_result.universe, [5, 10, 10])

current['low'] = fuzz.trimf(current.universe, [0, 0, 5])
current['medium'] = fuzz.trimf(current.universe, [2, 5, 8])
current['high'] = fuzz.trimf(current.universe, [5, 10, 10])

pov['low'] = fuzz.trimf(pov.universe, [0, 0, 5])
pov['medium'] = fuzz.trimf(pov.universe, [2, 5, 8])
pov['high'] = fuzz.trimf(pov.universe, [5, 10, 10])


proportional=1

if proportional==1:

	rule1 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['low'], pov['high'])
	rule2 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['medium'], pov['high'])
	rule3 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['high'], pov['high'])
	rule4 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['low'], pov['high'])
	rule5 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['medium'], pov['high'])
	rule6 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['high'], pov['high'])
	rule7 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['low'], pov['high'])
	rule8 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['medium'], pov['high'])
	rule9 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['high'], pov['high'])

	rule10 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['low'], pov['high'])
	rule11 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['medium'], pov['high'])
	rule12 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['high'], pov['high'])
	rule13 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['low'], pov['high'])
	rule14 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['medium'], pov['medium'])
	rule15 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['high'], pov['medium'])
	rule16 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['low'], pov['high'])
	rule17 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['medium'], pov['medium'])
	rule18 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['high'], pov['medium'])

	rule19 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['low'], pov['high'])
	rule20 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['medium'], pov['high'])
	rule21 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['high'], pov['high'])
	rule22 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['low'], pov['high'])
	rule23 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['medium'], pov['medium'])
	rule24 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['high'], pov['medium'])
	rule25 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['low'], pov['high'])
	rule26 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['medium'], pov['low'])
	rule27 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['high'], pov['low'])


else:
	rule1 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['low'], pov['low'])
	rule2 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['medium'], pov['low'])
	rule3 = ctrl.Rule(fused_estimation['low'] & kde_result['low'] & current['high'], pov['high'])
	rule4 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['low'], pov['low'])
	rule5 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['medium'], pov['low'])
	rule6 = ctrl.Rule(fused_estimation['low'] & kde_result['medium'] & current['high'], pov['high'])
	rule7 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['low'], pov['high'])
	rule8 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['medium'], pov['high'])
	rule9 = ctrl.Rule(fused_estimation['low'] & kde_result['high'] & current['high'], pov['high'])

	rule10 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['low'], pov['low'])
	rule11 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['medium'], pov['medium'])
	rule12 = ctrl.Rule(fused_estimation['medium'] & kde_result['low'] & current['high'], pov['high'])
	rule13 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['low'], pov['medium'])
	rule14 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['medium'], pov['medium'])
	rule15 = ctrl.Rule(fused_estimation['medium'] & kde_result['medium'] & current['high'], pov['high'])
	rule16 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['low'], pov['high'])
	rule17 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['medium'], pov['high'])
	rule18 = ctrl.Rule(fused_estimation['medium'] & kde_result['high'] & current['high'], pov['medium'])

	rule19 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['low'], pov['high'])
	rule20 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['medium'], pov['high'])
	rule21 = ctrl.Rule(fused_estimation['high'] & kde_result['low'] & current['high'], pov['high'])
	rule22 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['low'], pov['high'])
	rule23 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['medium'], pov['medium'])
	rule24 = ctrl.Rule(fused_estimation['high'] & kde_result['medium'] & current['high'], pov['medium'])
	rule25 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['low'], pov['high'])
	rule26 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['medium'], pov['high'])
	rule27 = ctrl.Rule(fused_estimation['high'] & kde_result['high'] & current['high'], pov['high'])


controller = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27])

fls_system = ctrl.ControlSystemSimulation(controller)

# the following code is adopted for retrieving the output!!

def calculate_fuzzy(fused_estimation, kde_result, current):
	fls_system.input['fused_estimation'] = fused_estimation
	fls_system.input['kde_result'] = kde_result
	fls_system.input['current'] = current
	#print fused_estimation, kde_result, current
	# calculate the output
	try:
		fls_system.compute()
		# print the results
		result=fls_system.output['pov']/10
		return result
	except:
		return 'Error'
