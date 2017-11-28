import os
import hashlib


def get_files_hash(files_names):
	files_dict = {}
	for name in files_names:
		if os.path.isdir(name):
			continue
		with open(name, 'rb') as f:
			files_dict[name] = hashlib.md5(f.read()).hexdigest()
			print('Proceed: {}'.format(name))

	return files_dict

def get_files_names(dir):
	os.chdir(dir)
	list = os.listdir(dir)
	files_names = []
	for name in list:
		files_names.append(os.path.abspath(name))

	return files_names

directories = []
subdirs = []

directories.append(input('Choose directory: '))
files_names = get_files_names(directories[0])

for name in files_names:
	if os.path.isdir(name):
		subdirs.append(name)
else:
	if len(subdirs) > 0:
		if input('Check subfolders?\nY/N? ') == 'Y':
			directories.extend(subdirs)

all_hashes = []
need_remove_names = []

for dir in directories:
	files_names = get_files_names(dir)

	files_hash = get_files_hash(files_names)

	for name, file_hash in files_hash.items():
		if file_hash not in all_hashes:
			all_hashes.append(file_hash)
			continue

		need_remove_names.append(name)

if len(need_remove_names) > 0:
	for name in need_remove_names:
		print('Identical >> {}'.format(name))
	if input('Delete files?\nY/N? ') == 'Y':
		for name in need_remove_names:
			os.remove(name)
else:
	print('No matches.')
