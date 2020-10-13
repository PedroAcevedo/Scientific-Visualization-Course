# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 23:57:38 2020

@author: randyc
"""
import argparse

def readFromFile(name):
	information = list()
	with open(name, "r") as f:
		for line in f.readlines():
			li = line.strip()
			if not li.startswith("#"):
				var = line.split()
				if(len(var) == 1):
					information.extend([int(var[0])])
				else:
					information.append([int(i) for i in var])
	return information
