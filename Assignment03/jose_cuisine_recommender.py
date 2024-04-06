#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:52:04 2024

@author: josemuniz
"""

import numpy as np
import pandas as pd
import os
from apyori import apriori

class CuisineRecommender: 
    # Load recipes json and normalize the cuisine names    
    def __init__(self):
        base_path = os.getcwd()
        self.data = pd.read_json(os.path.join(base_path, 'recipes.json'))
        # Normalize cuisine directly in the DataFrame
        self.data['cuisine'] = self.data['cuisine'].str.lower().str.strip()
        self.cuisine_types = self.data['cuisine'].unique()
    
    # generate the statistics            
    def data_analysis_report(self):
            print(f'Total number of recipe instances: {len(self.data)}')
            print(f'Number of cuisines available: {len(self.cuisine_types)}')
            cuisine_counts = self.data['cuisine'].value_counts().reset_index()
            cuisine_counts.columns = ['Cuisine Type', 'Number of Recipes']
            print(cuisine_counts)

    # returns a list of recipes for a given cuisine 
    def get_recipes_by_cuisine(self, cuisine):
        criteria = cuisine.lower().strip()
        if criteria not in self.cuisine_types:
            print(f'>> We don\'t have recommendations for: {criteria}')
            input('Type any key to continue')
            return pd.Series(dtype='object')  # Return an empty series
        return self.data.loc[self.data['cuisine'] == criteria, 'ingredients']

            
    # Calculate rules for a set of recipes using apriori algorithm        
    def calculate_rules(self, recipes):
        if recipes.empty:
            return []
        support = 100 / len(recipes)
        return list(apriori(recipes, min_support=support, min_confidence=0.5, min_lift=1.0, max_length=None))
    
    # transform rows of association_rules in a rules map.
    def translate_rules(self, association_rules):
        rules_map = {}
        for item in association_rules:
            if len(item.items) < 2:
                continue
            base_item_key = tuple(sorted(item.items))
            for rule_set in item.ordered_statistics:
                rule_items = list(rule_set.items_base) or list(rule_set.items_add)
                lift = rule_set.lift
                rules_map.setdefault(base_item_key, []).append((rule_items, lift))
        return rules_map
    
    # returnes recommendation based on given cuisine 
    def recommend(self, cuisine):
        recipes = self.get_recipes_by_cuisine(cuisine)    
        association_rules = self.calculate_rules(recipes)
        rules_map = self.translate_rules(association_rules)
        
        ingredients = set()
        high_lifts = []
        for rule_key, rules in rules_map.items():
            ingredients.update(rule_key)
            for rule in rules:
                if rule[1] > 2.0:
                    high_lifts.append((rule_key, rule))
        
        return ingredients, high_lifts
                


        
# MAIN PROGRAM EXECUTION
reco = CuisineRecommender()
cuisine = ''

reco.data_analysis_report()


while True:
    
    # Clear console for better readability
    os.system('clear')
    
    print('Type a cuisine type for recommendations (i.e Italian)')
    print('Cuisine Types: ')
    print(reco.cuisine_types)
    print()
    cuisine = input('(Type "Exit" to finish or cuisine) << : ')
    
    # Exit condition
    if str(cuisine).lower().strip() == 'exit':
        break
    
    ingredients, high_lifts = reco.recommend(cuisine)

    if len(ingredients) > 0:
        print(f'TOP INGREDIENTS FOR {str.upper(cuisine)} CUISINE')
        print(ingredients)

    if len(high_lifts) > 0:
        print()
        print()
        print('ITEMS MOST LIKELY TO BE BOUGHT TOGETHER: ')
        for rule in high_lifts:
            print(f'{rule[0]} -> {rule[1][0]} ({rule[1][1]})')
            
    input(f'Type any key to continue')
    
print('END OF PROGRAM')

