from __future__ import print_function

import os
import sys
import subprocess
import tester.helper as helper

def _format(output):
    output = output.split("\n")
    while output.count(''):
        output.remove('')

    for i in range(len(output)):
        j=len(output[i])-1
        while output[i][j]==' ':
            j-=1
        output[i] = output[i][0:j+1]

    return output

def cmd_maker(fname):
    cmd = []
    fext = os.path.splitext(os.path.basename(fname))[1]
    
    if fext == '.py':
        cmd = ['python', fname]
        return cmd

    if fext == '.cpp':
        os.system("gcc " + fname + " -o ./pl")
        cmd = ['./pl']
        return cmd

    print("Error: Invalid file extension. Expected .cpp or .py")
    return cmd

def test(fname, inputFile, outputFile):

    cmd = cmd_maker(fname)
    p = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True)
    
    input_ = open(inputFile).read()
    expected_output = open(outputFile).read()
    # input_ = open(helper.get_input_file(file_name)).read()
    # expected_output = open(helper.get_expected_output_file(file_name)).read()
    
    print(input_, file=p.stdin)
    user_output = p.stdout.read()

    user_output = _format(user_output)
    expected_output = _format(expected_output)
            
    result = helper.mark_program(user_output, expected_output, fname)
    
    print('-'*50)
    print(result)
    print('-'*50)
    
    with open("grades.txt", 'w') as file:
        file.write(result)

    res = {
        'result': result
    }

    return res
