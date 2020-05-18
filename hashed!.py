from os import scandir as scandir
from os import chdir as chdir
from os import stat as stat
from os import getcwd as getcwd

from os.path import isfile as isfile
from os.path import isdir as isdir
from os.path import basename as basename
from os.path import dirname as dirname
from os.path import split as split

from hashlib import blake2b as blake2b

try:
	# notice: not from core libs
	from send2trash import send2trash
except ImportError:
	print('Try: pip install send2trash')


def only_files(items):
	return list(filter(lambda name: isfile(name), items))

def only_folders(items):
	return list(filter(lambda name: isdir(name), items))

def get_path(scan_items):
	return list(map(lambda name: name.path, scan_items))

def sortByTime(items):
	return sorted(items, key=lambda item: stat(item).st_mtime)

def ignoreBigFiles(items): # less than 1GB
	return list(filter(lambda item: stat(item).st_size <= 1073741824, items))

def getKeyByValue(value, dictionary):
	index = list(dictionary.values()).index(value)
	return list(dictionary.keys())[index]

def get_files(root_dir):
	items = scandir(root_dir)
	items = get_path(items)
	items = sortByTime(items)
	items = ignoreBigFiles(items)

	files = only_files(items)
	if input('Check subfolders? Y/N\n') == 'Y':
		dirs = only_folders(items)
		
		while dirs:
			items = scandir(dirs[0])
			items = get_path(items)
			items = sortByTime(items)
			items = ignoreBigFiles(items)

			files = files + only_files(items)
			dirs = dirs + only_folders(items)

			dirs.pop(0)

	return files

def get_hash(files):
	hash_dict = {}
	dir = ""
	i = 1
	total = len(files)
	for path in files:
		if dir != dirname(path):
			dir = dirname(path)
			chdir(dir)

		with open(path, 'rb') as f:
			hash = blake2b(f.read()).hexdigest()
			hash_dict[path] = hash
		
		print(f"\rDone: {i}/{total}", end="")
			
		i = i + 1

	return hash_dict

def find_collisions(hash_dict):
	checked_hashes = []
	collisions = {}
	for path, hash in hash_dict.items():
		if hash not in checked_hashes:
			checked_hashes.append(hash)
		else:
			origin = getKeyByValue(hash, hash_dict)
			collisions[path] = { 'origin': origin, 'isDeleted': False }

	return collisions

def decide(collisions):
	deleteList = []
	print("You can decide by your own or by oldest time of creation")
	while True:
		decision = input("Which method you want?\n1. Manual selection\n2. Delete the newer ones\n")
		
		if decision not in ['1','2']:
			print('You typed it wrong, try again...')
		else:
			break

	if decision == '1':
		for path in collisions.keys():
			origin = collisions[path]['origin']
			isDeleted = collisions[path]['isDeleted']

			if isDeleted:
				continue

			print(f'1. {path}\n2. {origin}')

			while True:
				decision = input('Which one you want to save? ')
				if decision not in ['1','2']:
					print('You typed it wrong, try again...')
				elif decision == '1':
					deleteList.append(origin)
					break
				elif decision == '2':
					deleteList.append(path)
					break
			
			collisions[path]['isDeleted'] = True
			print('\n')

	elif decision == '2':
		for path in collisions.keys():
			origin = collisions[path]['origin']
			isDeleted = collisions[path]['isDeleted']

			if isDeleted:
				continue

			deleteList.append(path)
			collisions[path]['isDeleted'] = True
			print(f'{path} deleted')

	return deleteList

def trashTime(deleteList):
	'''
	We do this just because send2trash can't send by path,
	only by name in current working directory
	'''
	for path in deleteList:
		dir = split(path)[0]
		name = split(path)[1]
		
		if getcwd() != dir:
			chdir(dir)

		send2trash(name)


if __name__ == '__main__':

	root_dir = input('Input path to directory of search: ')
	chdir(root_dir)

	print('Search started')
	all_files = get_files(root_dir)
	print('Search done')

	print('Hash calculation started')
	all_files = get_hash(all_files)
	print('Hash calculation done')

	print('Collisions processing...')
	collisions = find_collisions(all_files)

	if len(collisions) > 0:
		print('Found: ' + str(len(collisions)) + ' collisions')
		deleteList = decide(collisions)
		trashTime(deleteList)
		print('Files has been sent to trash bin.')
	else:
		print('No collisions.')