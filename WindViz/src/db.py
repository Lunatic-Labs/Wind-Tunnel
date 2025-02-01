class Database():
	def __init__(self):
		self.data = {}

	def set_attribute(self, name, channel_num, channels, config):
		self.data[name] = {"num_channels" : channel_num, "channels" : channels, "configuration" : config}

	def get_attribute(self, name):
		return self.data[name]
		
