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
DEFAULT_LIST_NAME = "tasks"
DEFAULT_SELECTION = 1
default_file_path = os.path.join(script_dir, "data", f"{DEFAULT_LIST_NAME}.txt")
current_path_file = os.path.join(script_dir, "data", ".current")

def _read_current_path():
	try:
		if os.path.exists(current_path_file):
			with open(current_path_file, 'r', encoding='utf-8') as f:
				return f.read().strip()
	except OSError:
		pass
	return None

def _write_current_path(path):
	try:
		dir_path = os.path.dirname(current_path_file)
		if dir_path:
			os.makedirs(dir_path, exist_ok=True)
		with open(current_path_file, 'w', encoding='utf-8') as f:
			f.write(path)
	except OSError:
		pass

def _sanitize_list_name(name):
	safe = "".join([c for c in name.strip() if c.isalnum() or c in ('-', '_')])
	return safe or DEFAULT_LIST_NAME

def _matching_list_paths(prefix):
	data_dir = os.path.join(script_dir, "data")
	matches = []
	try:
		if not os.path.isdir(data_dir):
			return []
		for name in os.listdir(data_dir):
			if not name.endswith(".txt"):
				continue
			base = name[:-4]
			if base.startswith(prefix):
				matches.append(os.path.join(data_dir, name))
	except OSError:
		return []
	return sorted(matches)

def _print_help():
	"""Print usage information for todo."""
	help_text = """todo - A minimalist command line task manager

USAGE:
    todo                                    List all tasks
    todo [list_name]                        Switch to a different list
    todo -[task description]                Add a new task
    todo -f ID [ID...]                      Finish (remove) one or more tasks
    todo -e ID [new description]            Edit a task
    todo help                               Show this help message
    todo --help                             Show this help message
    todo -h                                 Show this help message

OPTIONS:
    --location PATH                         Use a specific file location
    --task LIST_NAME                        Use a specific list name

EXAMPLES:
    todo -Buy milk                          Add a task
    todo -f 1                               Finish task with ID 1
    todo -f 1 2 3                           Finish tasks with IDs 1, 2, and 3
    todo -e 2 Buy more milk                 Edit task with ID 2
    todo groceries                          Switch to 'groceries' list
    todo --task work -Finish report         Add task to 'work' list
"""
	print(help_text)

def _select_list_from_prefix(args, current_path):
	if len(args) == 0 or args[0].startswith('-'):
		return current_path, args
	list_name = _sanitize_list_name(args[0])
	matches = _matching_list_paths(list_name)
	if len(matches) == 0:
		new_path = os.path.join(script_dir, "data", "{}.txt".format(list_name))
		return new_path, args[1:]
	if len(matches) == 1:
		return matches[0], args[1:]
	print("Multiple lists found:")
	for idx, path in enumerate(matches, 1):
		print("[{}] {}".format(idx, os.path.basename(path)[:-4]))
	default_sel = DEFAULT_SELECTION
	try:
		choice = input("Select list [1-{}] (default {}): ".format(len(matches), default_sel)).strip()
		sel = int(choice) if choice else default_sel
		if sel < 1 or sel > len(matches):
			sel = default_sel
	except (ValueError, EOFError):
		sel = default_sel
	return matches[sel - 1], args[1:]

arguments = sys.argv[1:]

# Check for help command first
if len(arguments) > 0 and arguments[0] in ('help', '--help', '-h'):
	_print_help()
	sys.exit(0)

saved_path = _read_current_path()
filePath = saved_path or default_file_path
while len(arguments) >= 2 and arguments[0] in ("--location", "--task"):
	if arguments[0] == '--location':
		filePath = arguments[1]
	elif arguments[0] == '--task':
		task_name = arguments[1].strip()
		safe_task_name = _sanitize_list_name(task_name)
		filePath = os.path.join(script_dir, "data", "{}.txt".format(safe_task_name))
	arguments = arguments[2:]

filePath, arguments = _select_list_from_prefix(arguments, filePath)

if filePath != saved_path:
	_write_current_path(filePath)

todo = TodoService(filePath)

if len(arguments) == 0:
	todo.print_all_tasks()
elif len(arguments) >= 2 and arguments[0] == "-f":
	todo.remove_tasks(list(map(lambda x: int(x), arguments[1:])))
elif len(arguments) >= 3 and arguments[0] == "-e":
	todo.edit_task(int(arguments[1]), " ".join(arguments[2:]))
else:
	# Strip leading dash from first argument if present (for adding items)
	task_args = arguments[:]
	if task_args and task_args[0].startswith('-') and len(task_args[0]) > 1:
		task_args[0] = task_args[0][1:]
	todo.add_task(" ".join(task_args))

todo.close()
