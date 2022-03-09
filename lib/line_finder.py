# Looking for the first line with $search_key in it
def line_finder(file, search_key):
	iterator = 0
	found_line = None

	for line in file:
		found = line.find(search_key)
		iterator += 1
		# if current line does not contain search_key, found == -1
		if not found == -1:
			found_line = file[iterator].split()
			break
		
	if found_line == None:
		iterator = None
	return [iterator, found_line]
