#!/usr/bin/python3
# -*- coding: utf-8 -*-

import click
from pprint import pprint
import random
import copy
import math

def proc_literal(name):
    lit = int(name)
    return (abs(lit), lit<0)

def load_input(input_file):
    SAT = {'var_cnt': 0, 'clause_cnt': 0, 'clauses': [], 'comments': [], 'var_weight': []}
    with open(input_file, 'r') as inf:
        for line in inf:
            data = line.split(' ')
            if line[0:2] == 'c ':
                SAT['comments'].append(line[2:-1])
            elif line[0:2] == 'p ':
                # data = line.split(' ')
                SAT['var_cnt'] = int(data[2])
                SAT['clause_cnt'] = int(data[3])
            elif line[0:2] == 'w ':
                SAT['weights'] = list(map(int, data[1:]))
            else:
                # data = line.split(' ')
                # SAT['clauses'].append(list(map(proc_literal, data[:-1])))
                SAT['clauses'].append(list(map(int, data[:-1])))
    return SAT

def make_individual(size):
    return { 'dna': [ random.random() < 0.5 for i in range(size) ] }

def var_to_cla_map(SAT):
    var_to_cla = {}
    for i in range(1, SAT['var_cnt']+1):
        var_to_cla[i] = set()
        var_to_cla[-1*i] = set()
    for i in range(SAT['clause_cnt']):
        for v in SAT['clauses'][i]:
            var_to_cla[v].add(i)
    return var_to_cla

def fill_properties(SAT, individual):
    clauses = set()
    weight = 0
    for i in range(SAT['var_cnt']):
        if individual['dna'][i] == True:
            clauses |= SAT['var_to_cla'][i+1]
            weight += SAT['weights'][i]
        else:
            clauses |= SAT['var_to_cla'][-1*(i+1)]
    individual['clauses'] = len(clauses)
    individual['weight'] = weight

def population_sort(population):
    # The sort() method is guaranteed to be stable -> radix sort
    population.sort(key=lambda x: x['weight'], reverse=True)
    population.sort(key=lambda x: x['clauses'], reverse=True)

def init_population(SAT, pop_size):
    size = SAT['var_cnt']
    population = []
    for i in range(pop_size):
        individual = make_individual(size)
        fill_properties(SAT, individual)
        population.append(individual)
    return population

def crossover(SAT, population, pop_size, cross_f):
    child_cnt = int(pop_size*cross_f)
    size = SAT['var_cnt']
    for i in range(child_cnt):
        a = random.randint(0, pop_size-1)
        b = random.randint(0, pop_size-1)
        while a==b:
            b = random.randint(0, pop_size-1)
        d = random.randint(0, size)
        # print(a, b, d)
        individual = { 'dna': [ population[a]['dna'][i] if (i < d) else population[b]['dna'][i] for i in range(size) ] }
        fill_properties(SAT, individual)
        # repair_individual(SAT, individual)
        # pprint(individual)
        population.append(individual)
    # return population

def mutation(SAT, population, elites, mut_f, mut_s):
    # print(mut_f, mut_s)
    pop_size = len(population)
    mutants_cnt = math.ceil(pop_size*mut_f)
    size = SAT['var_cnt']
    for i in range(mutants_cnt):
        a = random.randint(0, pop_size-1)
        for j in range(math.ceil(mut_s*size)):
            k = random.randint(0, size-1)
            population[a]['dna'][k] = not population[a]['dna'][k]
        fill_properties(SAT, population[a])
        if a < len(elites):
            elites[a][1] = True

def deduplication(SAT, population):
    population_sort(population)
    clause_cnt = SAT['clause_cnt']
    pattern = 0
    for i in range(1, len(population)):
        if population[i] == population[pattern]:
            population[i]['clauses'] -= clause_cnt
        else:
            pattern = i

def evolution(SAT, pop_size, gen_cnt, cross_factor):
    population = init_population(SAT, pop_size)
    population_sort(population)
    elite_cnt = 1
    # cross_factor = 0.6
    mutation_f = 0.1
    mutation_size = 0.25
    dna_degradation = 0
    dna_d_delta = 0.02
    # pprint(population)
    for g in range(gen_cnt):
        elites = []
        for i in range(elite_cnt):
            elites.append([copy.deepcopy(population[i]),False])
        # mutate
        mutation(SAT, population, elites, mutation_f+dna_degradation, mutation_size+(0.4*dna_degradation))
        # cross
        crossover(SAT, population, pop_size, cross_factor)
        for ind in elites:
            if ind[1]:
                population.append(ind[0])
        # deduplicate
        deduplication(SAT, population)
        population_sort(population)
        if population[0]['dna'] == elites[0][0]['dna'] and dna_degradation+mutation_f<0.75:
            # if dna_degradation+mutation_f<0.6:
            dna_degradation += dna_d_delta
        else:
            dna_degradation = 0
        population = population[:pop_size]
        # print('{}: {}, {}, {}, {}, {}, {}'.format(
        print('{};{};{};{};{};{};{}'.format(
            g+1, population[0]['clauses'], population[0]['weight'],
            population[pop_size//2]['clauses'], population[pop_size//2]['weight'],
            population[-1]['clauses'], population[-1]['weight']
        ))
        # if population[0]['clauses'] == SAT['clause_cnt']:
            # break;

@click.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
    help='path to file with input', prompt='Enter path to file with input'
)
@click.option(
    '--population', '-p', default=100, type=click.IntRange(1, 1000000),
    help='size of population'
)
@click.option(
    '--generations', '-g', default=100, type=click.IntRange(1, 1000000),
    help='number of generations'
)
@click.option(
	'--cross-factor', '-c', default=0.75, type=click.FLOAT,
	help='how many children are born in each generation, CROSS-FACTOR*POPULATION_SIZE'
)
def main(input_file, population, generations, cross_factor):
    SAT = load_input(input_file)
    SAT['var_to_cla'] = var_to_cla_map(SAT)
    evolution(SAT, population, generations, cross_factor)
    # ind1 = make_individual(SAT['var_cnt'])
    # ind2 = make_individual(SAT['var_cnt'])
    # ind3 = copy.deepcopy(ind1)
    # print(ind1)
    # print(ind2)
    # print(ind3)
    # print(ind1 == ind2)
    # print(ind1 == ind3)
    # population = init_population(SAT, 10)
    # population_sort(population)
    # pprint(population)

    return 0

if __name__ == '__main__':
    main()
