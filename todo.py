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

	def print_all_tasks(self, list_name=None):
		if list_name:
			print(f"List: {list_name}")
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

def _get_list_name_from_path(path):
	"""Extract the list name from a file path."""
	return os.path.basename(path)[:-4] if path.endswith('.txt') else os.path.basename(path)

def _list_all_lists():
	"""List all available task lists."""
	data_dir = os.path.join(script_dir, "data")
	if not os.path.isdir(data_dir):
		print("No lists found.")
		return
	lists = []
	try:
		for name in os.listdir(data_dir):
			if name.endswith(".txt") and not name.startswith("."):
				lists.append(name[:-4])
	except OSError:
		print("Error reading lists directory.")
		return
	if not lists:
		print("No lists found.")
	else:
		print("Available lists:")
		for list_name in sorted(lists):
			print(f"  {list_name}")

def _create_new_list(list_name):
	"""Create a new empty list."""
	safe_name = _sanitize_list_name(list_name)
	new_path = os.path.join(script_dir, "data", f"{safe_name}.txt")
	if os.path.exists(new_path):
		print(f"List '{safe_name}' already exists.")
		return new_path
	# Create the list by instantiating TodoService (will create file on close)
	todo_service = TodoService(new_path)
	todo_service.close()
	print(f"Created new list: {safe_name}")
	return new_path

def _get_list_files(data_dir):
	"""Get list of .txt files (excluding hidden files) in the data directory."""
	try:
		if os.path.isdir(data_dir):
			return [f for f in os.listdir(data_dir) if f.endswith(".txt") and not f.startswith(".")]
	except OSError:
		pass
	return []

def _delete_list(list_name):
	"""Delete a list."""
	safe_name = _sanitize_list_name(list_name)
	list_path = os.path.join(script_dir, "data", f"{safe_name}.txt")
	
	if not os.path.exists(list_path):
		print(f"List '{safe_name}' does not exist.")
		return False
	
	# Check if there are other lists - prevent deleting the only list
	data_dir = os.path.join(script_dir, "data")
	txt_files = _get_list_files(data_dir)
	if len(txt_files) <= 1:
		print(f"Cannot delete '{safe_name}': it's the only list.")
		return False
	
	try:
		# Check if we're deleting the current list before deletion
		current = _read_current_path()
		is_current = (current == list_path)
		
		os.remove(list_path)
		print(f"Deleted list: {safe_name}")
		
		# If the deleted list was the current list, switch to another list
		if is_current:
			# Find another existing list to switch to
			if os.path.exists(default_file_path):
				_write_current_path(default_file_path)
			else:
				# Find any remaining list
				for name in sorted(_get_list_files(data_dir)):
					other_list = os.path.join(data_dir, name)
					_write_current_path(other_list)
					break
		
		return True
	except OSError as e:
		print(f"Error deleting list '{safe_name}': {e}")
		return False

arguments = sys.argv[1:]

# Handle --list-all / -l flag to show all lists
if len(arguments) > 0 and arguments[0] in ("--list-all", "-l"):
	_list_all_lists()
	sys.exit(0)

# Handle --new-list flag to create a new list
if len(arguments) >= 2 and arguments[0] == "--new-list":
	new_list_path = _create_new_list(arguments[1])
	_write_current_path(new_list_path)
	sys.exit(0)

# Handle --delete-list flag to delete a list
if len(arguments) >= 2 and arguments[0] == "--delete-list":
	_delete_list(arguments[1])
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

# Get the list name for display
list_name = _get_list_name_from_path(filePath)

todo = TodoService(filePath)

if len(arguments) == 0:
	todo.print_all_tasks(list_name)
elif len(arguments) >= 2 and arguments[0] == "-f":
	todo.remove_tasks(list(map(lambda x: int(x), arguments[1:])))
elif len(arguments) >= 3 and arguments[0] == "-e":
	print(f"List: {list_name}")
	todo.edit_task(int(arguments[1]), " ".join(arguments[2:]))
else:
	# Strip leading dash from first argument if present (for adding items)
	task_args = arguments[:]
	if task_args and task_args[0].startswith('-') and len(task_args[0]) > 1:
		task_args[0] = task_args[0][1:]
	todo.add_task(" ".join(task_args))

todo.close()
