import numpy

class Brain:
	def __init__(self, input_size, hidden_size, output_size):
		self.input_size = input_size
		self.hidden_size = hidden_size
		self.output_size = output_size
		
		# Weights and stuff