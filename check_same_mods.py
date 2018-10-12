import requests
import pickle

# getting necessary info to access ivle
def get_token():
	# returns a tuple of key and token
	try:
		return read_from_file("./token.pkl")
	except FileNotFoundError:
		key = input("Key in your LAPI Key: ")
		print("Log in and copy your token from " + "https://ivle.nus.edu.sg/api/login/?apikey=%s" % key + "\n")

		token = input("Key in your LAPI token: ")
		token_comb = (key, token)
		with open("./token.pkl", "wb") as f:
				pickle.dump(token_comb, f)
		return token_comb


def get_and_save(api_get, filename):
    # takes in the API call URL, and write the content to the file
    f = open(filename, "wb")
    r = requests.get(api_get)
    pickle.dump(r.json(), f)
    f.close()


def read_from_file(filename):
    # return the content from the file
    with open(filename, "rb") as f:
        return pickle.load(f)

def api_get_request(api_get, filename):
	try:
		return read_from_file(filename)
	except FileNotFoundError:
		get_and_save(api_get, filename)
		return read_from_file(filename)

def clear_up_module(raw_module):
	# return a list of dictionaries that contains mod info
    module = []
    for i in range(len(raw_module['Results'])):
        module.append({'Code': raw_module['Results'][i]['CourseCode'], 
                       'Name': raw_module['Results'][i]['CourseName'], 
                       'ID': raw_module['Results'][i]['ID']})
    return module

def namelist_of_mod(module):
    namelist = []
    for i in range(len(module['Results'])):
        namelist.append(module['Results'][i]['Name'])
    return namelist


# Execute
# initialising
key = get_token()[0]
token = get_token()[1]


# getting a list of mods i'm taking
module_call = "https://ivle.nus.edu.sg/api/Lapi.svc/Modules?APIKey=%s&AuthToken=%s&Duration=%s&IncludeAllInfo=%s" % (key, token, "10", "false")
module_content = api_get_request(module_call, "./module.pkl")

list_of_id = list(map(lambda course: course['ID'], clear_up_module(module_content)))
list_of_codes = list(map(lambda course: course['Code'], clear_up_module(module_content)))

# determine which mods to check
print("Your current modules: \n")
for i in range(len(list_of_codes)):
	print(str(i) + ": " + list_of_codes[i])
print("\n")
choice = input("Key in the index numbers of the mods that you wish to check, seperated by space: \n")

def select_mods(mod_list, choice):
	choice_of_codes = []
	for i in list(map(lambda string: int(string), choice.split())):
		choice_of_codes.append(mod_list[i])
	return choice_of_codes

choice_of_codes = select_mods(list_of_codes, choice)
choice_of_id = select_mods(list_of_id, choice)

print("Your choice of modules: \n" + str(choice_of_codes) + "\n")

# getting the namelists of mods of choice
class_roster_call = lambda course_id: "https://ivle.nus.edu.sg/API/Lapi.svc/Class_Roster?APIKey=%s&AuthToken=%s&CourseID=%s" % (key, token, course_id)
namelist_of_index = lambda i: namelist_of_mod(api_get_request(class_roster_call(choice_of_id[i]), "./" + choice_of_id[i] + ".pkl"))

def find_intersection(choice_of_id):
	result = set(namelist_of_index(0))
	for i in range(1, len(choice_of_id)):
		result.intersection_update(namelist_of_index(i))
	return print("Your course mates are: \n" + str(result))

find_intersection(choice_of_id)

