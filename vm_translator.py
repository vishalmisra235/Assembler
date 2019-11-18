import os
import re
import sys

ath_commands = ['add','sub','neg','and','or','not']
log_commands = ['eq','gt','lt']
mem_commands = ['push','pop']
branching_commands = ['label','goto','if-goto']
function_commands = ['function','call','return']
segment_map = {
    'local':'LCL','this':'THIS',
    'that':'THAT','argument':'ARG','temp':'TMP'
    }

ath_table = {
    'add' : '@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=D+M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n',
    'sub' : '@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=M-D\n@SP\nA=M\nM=D\n@SP\nM=M+1\n',
    'and' : '@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=D&M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n',
    'or' : '@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=D|M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n',
    'not' : '@SP\nM=M-1\nA=M\nM=!M\n@SP\nM=M+1\n',
    'neg' : '@SP\nM=M-1\nA=M\nM=-M\n@SP\nM=M+1\n',
}

log_table = {
    'eq':'JEQ',
    'gt':'JGT',
    'lt':'JLT'
}

def translator(commands):
    function_counter=0
    for line in commands:
        words = line.split(" ")
        command = []
        for i in words:
            if i!='':
                command.append(i)

        if command[0] in mem_commands:
            if command[0]=='push':
                if command[1]=='constant':
                    new_command = '@'+command[2]+'\nD=A\n'
                    new_command += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                    hackfile.write(new_command)
                elif command[1]=='local' or command[1]=='argument' or command[1]=='this' or command[1]=='that':
                    new_command = '@'+segment_map.get(command[1])+'\nD=A\n@'+command[2]+'\nD=D+A\nA=D\nD=M\n'
                    new_command += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                    hackfile.write(new_command)
                elif command[1]=='temp':
                    new_command = '@5\nD=A\n@'+command[2]+'\nD=D+A\nA=D\nD=M\n'
                    new_command += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                    hackfile.write(new_command)
            elif command[0]=='pop':
                if command[1]=='local' or command[1]=='argument' or command[1]=='this' or command[1]=='that':
                    new_command = '@'+segment_map.get(command[1])+'\nD=A\n@'+command[2]+'\nD=D+A\nA=D\nD=M\n'
                    new_command += '@SP\nM=M-1\n@SP\nA=M\nM=D\n'
                    hackfile.write(new_command)
                elif command[1]=='temp':
                    new_command = '@5\nD=A\n@'+command[2]+'\nD=D+A\nA=D\nD=M\n'
                    new_command += '@SP\nM=M-1\n@SP\nA=M\nM=D\n'
                    hackfile.write(new_command)

        elif command[0] in ath_commands:
            hackfile.write(ath_table.get(command[0]))

        elif command[0] in log_commands:
            new_command = '@SP\nAM=M-1\nD=M\n@15\nM=D\n@SP\nAM=M-1\nD=M\n@18M=D\n'
            new_command += '@15\nD=M\n@18\nD=D-M\n'
            new_command += '@FUNC_'+str(function_counter)
            new_command += '\nD;'+log_table.get(command[0])
            new_command += '\nD=0\n'
            new_command += '@END_'+str(function_counter)
            new_command += '\n0;JMP\n'
            new_command += '(FUNC_'+str(function_counter)+')'
            new_command += '\nD=1\n'
            new_command += '(END_'+str(function_counter)+')'
            new_command += '\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
            function_counter += 1
            hackfile.write(new_command)
    
        elif command[0] == 'label':
            new_command = '('+command[1]+')\n'
            hackfile.write(new_command)
            
        elif command[0] == 'goto:':
            new_command = '@'+command[1]+'\n0;JMP\n'
            hackfile.write(new_command)
            
        elif command[0] == 'if-goto':
            new_command = '@SP\nAM=M-1\nD=M\n@'+command[1]+'\nD;JNE\n'
            hackfile.write(new_command)

argumentList = sys.argv
fname = sys.argv[1].rstrip()

x = re.findall(".vm$", fname)
if len(x)==0:
    print ("Incorrect file name")

asmfile = open(fname, "r")
all_lines = asmfile.readlines()

hackfile = open(fname.replace('.vm','.asm'),"w+")

commands = []
for lines in all_lines:
    new_line = (lines.replace('\n','')).replace('\t','')
    new_line=re.sub('//.*','',str(new_line))
    if new_line!='':
        commands.append(new_line)

translator(commands)
