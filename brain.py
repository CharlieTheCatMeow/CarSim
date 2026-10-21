import numpy

class Brain:
	def __init__(self, input_size, hidden_sizes, output_size, initialize=True):
		if isinstance(hidden_sizes, int):
			hidden_sizes = [hidden_sizes]
		else:
			hidden_sizes = list(hidden_sizes)
			
		self.input_size = input_size
		self.hidden_sizes = hidden_sizes
		self.output_size = output_size
		self.layer_sizes = [input_size] + hidden_sizes + [output_size]
		
		# Weights and stuff
		self.weights = []
		self.biases = []
		
		if initialize:
			for i in range(len(self.layer_sizes) - 1):
				in_size = self.layer_sizes[i]
				out_size = self.layer_sizes[i + 1]
				scale = numpy.sqrt(1.0 / in_size)
				self.weights.append(numpy.random.randn(in_size, out_size) * scale)
				self.biases.append(numpy.zeros(out_size))
	
	def think(self, inputs):
		activation = numpy.asarray(inputs, dtype=numpy.float32)
		for weight, bias in zip(self.weights, self.biases):
			activation = numpy.tanh(activation @ weight + bias)
		return activation
	
	def copy(self):
		new_brain = Brain(self.input_size, self.hidden_sizes, self.output_size, initialize=False)
		new_brain.weights = [weight.copy() for weight in self.weights]
		new_brain.biases = [bias.copy() for bias in self.biases]
		return new_brain
	
	def mutated_copy(self, mutation_rate = 0.1):
		new_brain = Brain(self.input_size, self.hidden_sizes, self.output_size, initialize=False)
		new_brain.weights = [
			w + numpy.random.randn(*w.shape) * mutation_rate for w in self.weights
		]
		new_brain.biases = [
			b + numpy.random.randn(*b.shape) * mutation_rate for b in self.biases
		]
		return new_brain
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	