#!/usr/bin/python3
# -*- coding: utf-8 -*-

import click
from pprint import pprint

def proc_literal(name):
    lit = int(name)
    return (abs(lit), lit<0)

def load_input(input_file):
    SAT = {'var_cnt': 0, 'clause_cnt': 0, 'clauses': [], 'comments': [], 'var_weight': []}
    with open(input_file, 'r') as inf:
        for line in inf:
            # data = line.split(' ')
            if line[0:2] == 'c ':
                SAT['comments'].append(line[2:-1])
            elif line[0:2] == 'p ':
                data = line.split(' ')
                SAT['var_cnt'] = int(data[2])
                SAT['clause_cnt'] = int(data[3])
                SAT['var_weight'] = list(map(int, data[4:]))
            else:
                data = line.split(' ')
                SAT['clauses'].append(list(map(proc_literal, data[:-1])))
    return SAT

@click.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
    help='path to file with input', prompt='Enter path to file with input'
)
def main(input_file):
    SAT = load_input(input_file)
    pprint(SAT)

    return 0

if __name__ == '__main__':
    main()
