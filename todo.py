#!/usr/bin/env python3
import os
import sys
import textwrap

class ASCIITable(object):
	def __init__(self, headers):
		if type(headers) != list:
			raise TypeError("Header row is expected as a list")
		self.headers = []
		self.data = []
		for i in headers:
			try:
				self.headers.append(str(i))
			except:
				raise ValueError("Unable to convert {} into string".format(i))

	def add_row(self, row):
		if len(self.headers) != len(row):
			raise ValueError("Size of headers and row do not match")
		rowData = []
		for i in row:
			try:
				rowData.append(str(i))
			except:
				raise ValueError("Unable to convert {} into string".format(i))
		self.data.append(rowData)

	def __str__(self):
		columnWidth = []
		asciiTable = ''
		for i in range(len(self.headers)):
			maxWidth = 0
			maxWidth = max(maxWidth, len(str(self.headers[i])))
			for j in range(len(self.data)):
				maxWidth = max(maxWidth, len(str(self.data[j][i]).translate({'\u0336': None})))
			columnWidth.append(maxWidth + 2)
		asciiTable += '+' + '+'.join(map(lambda i: '-' * i, columnWidth)) + '+\n'
		asciiTable += '|' + '|'.join([self.headers[i].center(columnWidth[i]) for i in range(len(columnWidth))]) + "|\n"
		asciiTable += '+' + '+'.join(map(lambda i: '-' * i, columnWidth)) + '+\n'
		for row in self.data:
			asciiTable += '|' + '|'.join([row[i].center(columnWidth[i]) for i in range(len(columnWidth))]) + "|\n"
		asciiTable += '+' + '+'.join(map(lambda i: '-' * i, columnWidth)) + '+'
		return asciiTable

class TodoService(object):
	def __init__(self, filePath):
		self.filePath = filePath
		self.tasks = {}
		self.next_id = 1
		self._load()

	def _load(self):
		"""Load tasks from the .txt file."""
		if os.path.exists(self.filePath):
			with open(self.filePath, 'r', encoding='utf-8') as f:
				for line in f:
					line = line.strip()
					if line:
						parts = line.split('|', 1)
						if len(parts) == 2:
							try:
								task_id = int(parts[0])
								task = parts[1]
								self.tasks[task_id] = task
								if task_id >= self.next_id:
									self.next_id = task_id + 1
							except ValueError:
								pass

	def _save(self):
		"""Save tasks to the .txt file."""
		# Ensure the directory exists
		dir_path = os.path.dirname(self.filePath)
		if dir_path and not os.path.exists(dir_path):
			os.makedirs(dir_path)
		with open(self.filePath, 'w', encoding='utf-8') as f:
			for task_id in sorted(self.tasks.keys()):
				f.write("{}|{}\n".format(task_id, self.tasks[task_id]))

	def add_task(self, task):
		# Sanitize newlines from task text to prevent file format corruption
		sanitized_task = task.replace('\n', ' ').replace('\r', ' ')
		self.tasks[self.next_id] = sanitized_task
		self.next_id += 1

	def remove_tasks(self, ids):
		if len(ids) != 0:
			for task_id in ids:
				if task_id in self.tasks:
					del self.tasks[task_id]

	def edit_task(self, id, task):
		if id in self.tasks:
			# Sanitize newlines from task text to prevent file format corruption
			sanitized_task = task.replace('\n', ' ').replace('\r', ' ')
			self.tasks[id] = sanitized_task

	def print_all_tasks(self):
		asciiTable = ASCIITable(["ID", "Task"])
		for task_id in sorted(self.tasks.keys()):
			task = self.tasks[task_id]
			wrapped_task = textwrap.wrap(task)
			if wrapped_task:
				asciiTable.add_row([task_id, wrapped_task[0]])
				for i in range(1, len(wrapped_task)):
					asciiTable.add_row(['', wrapped_task[i]])
		print(asciiTable)

	def close(self):
		self._save()

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Default file path: data/tasks.txt in the same directory as the script
default_file_path = os.path.join(script_dir, "data", "tasks.txt")

arguments = sys.argv[1:]

filePath = default_file_path
if len(arguments) >= 2 and arguments[0] == '--location':
	filePath = arguments[1]
	arguments = arguments[2:]

todo = TodoService(filePath)

if len(arguments) == 0:
	todo.print_all_tasks()
elif len(arguments) >= 2 and arguments[0] == "-f":
	todo.remove_tasks(list(map(lambda x: int(x), arguments[1:])))
elif len(arguments) >= 3 and arguments[0] == "-e":
	todo.edit_task(int(arguments[1]), " ".join(arguments[2:]))
else:
	todo.add_task(" ".join(arguments))

todo.close()