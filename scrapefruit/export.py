import jsonlines

class Exporter:

	def __init__(self, app):
		self.file = app.config.get("OUTPUT_FILE")
		self.writer = jsonlines.open(self.file, 'w')

	def write(self, item):
		self.writer.write(item)

	def shutdown(self):
		self.writer.close()

	def get_output(self):
		result = []
		with jsonlines.open(self.file) as reader:
			for obj in reader:
				result.append(obj)
		return result
