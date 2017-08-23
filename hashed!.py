import os
import hashlib


def get_files_hash(files_names):
	files_dict = {}
	for name in files_names:
		with open(name, 'rb') as f:
			files_dict[name] = hashlib.md5(f.read()).hexdigest()
			print('Proceed: {}'.format(name))

	return files_dict


directory = input('Choose directory: ')
os.chdir(directory)
files_names = os.listdir(directory)

#here we delete dir's from our list to avoid error
for name in files_names:
	if os.path.isdir(name):
		files_names.remove(name)

files_hash = get_files_hash(files_names)

all_hashes = []
need_remove_names = []
for name, file_hash in files_hash.items():
	if file_hash not in all_hashes:
		all_hashes.append(file_hash)
		continue

	need_remove_names.append(name)
	print('Identical!\n{}'.format(name))

if len(need_remove_names) > 0:
	if input('Delete files? Y/N?') == 'Y':
		for name in need_remove_names:
			os.remove(name)
else:
	print('No matches.')
