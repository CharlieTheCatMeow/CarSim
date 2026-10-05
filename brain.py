import numpy

class Brain:
	def __init__(self, input_size, hidden_size, output_size):
		self.input_size = input_size
		self.hidden_size = hidden_size
		self.output_size = output_size
		
		# Weights and stuff
		self.weight_1 = numpy.random.randn(self.input_size, self.hidden_size) * 0.5
		self.bias_1 = numpy.random.randn(self.hidden_size) * 0.5
		
		self.weight_2 = numpy.random.randn(self.hidden_size, self.output_size) * 0.5
		self.bias_2 = numpy.random.randn(self.output_size) * 0.5
	
	def think(self, inputs):
		inputs = numpy.array(inputs, dtype = float)
		
		hidden_layer = numpy.tanh(inputs @ self.weight_1 + self.bias_1)
		output_layer = numpy.tanh(hidden_layer @ self.weight_2 + self.bias_2)
		
		throttle = output_layer[0]
		steering = output_layer[1]
		return throttle, steering
	
	def copy(self):
		new_brain = Brain(self.input_size, self.hidden_size, self.output_size)
		new_brain.weight_1 = self.weight_1.copy()
		new_brain.bias_1 = self.bias_1.copy()
		new_brain.weight_2 = self.weight_2.copy()
		new_brain.bias_2 = self.bias_2.copy()
		return new_brain
	
	def mutated_copy(self, mutation_rate = 0.1):
		new_brain = Brain(self.input_size, self.hidden_size, self.output_size)
		new_brain.weight_1 = self.weight_1 + numpy.random.randn(*self.weight_1.shape) * mutation_rate
		new_brain.bias_1 = self.bias_1 + numpy.random.randn(*self.bias_1.shape) * mutation_rate
		new_brain.weight_2 = self.weight_2 + numpy.random.randn(*self.weight_2.shape) * mutation_rate
		new_brain.bias_2 = self.bias_2 + numpy.random.randn(*self.bias_2.shape) * mutation_rate
		return new_brain
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	