import os

def get_input_file(file_name):
    fname, ext = os.path.splitext(os.path.basename(file_name))
    prog_num = fname.split('_')[-1]

    if prog_num == "1":
        return "input_1.txt"

    if prog_num == "2":
        return "input_2.txt"

    return "invalid_prog_num"

def get_expected_output_file(file_name):
    fname, ext = os.path.splitext(os.path.basename(file_name))
    prog_num = fname.split('_')[-1]

    if prog_num=="1":
        return "expected_output_1.txt"

    if prog_num=="2":
        return "expected_output_2.txt"
        
    return "invalid_prog_num"

def mark_program(user_output, expected_output, file_name):
    ## user_output/expected_output is a list of different output lines
    
    fname, ext = os.path.splitext(os.path.basename(file_name))
    prog_num = fname.split('_')[-1]
    
    if prog_num == "1":
        ## let every line output be independent
        comp = zip(user_output, expected_output)
        cases_passed = 0
        for tup in comp:
            if tup[0] == tup[1]:
                cases_passed += 1

        return "{} passed {}/{}.".format(file_name, cases_passed, len(expected_output))

    if prog_num == "2":
        ## let this question be case dependent

        user_output_file = '\n'.join(user_output) + '\n'
        expected_output_file = '\n'.join(expected_output) + '\n'
        
        user_cases = user_output_file.split("Case #")
        expected_output_cases = expected_output_file.split("Case #")

        comp = zip(user_cases, expected_output_cases)
        
        cases_passed = 0
        for tup in comp[1:]:
            if tup[0] == tup[1]:
                cases_passed += 1
        
        return "{} passed {}/{}.".format(file_name, cases_passed, len(expected_output))
    
    return "Invalid prog_num ({}) for {}.".format(prog_num, file_name)
    