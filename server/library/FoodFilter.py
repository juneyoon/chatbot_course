import json
import os
import re
import pickle
import random

import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
sentence_encoder_model = hub.load(module_url)
food_data = None
filter_encodings = None


class FoodFilterClass:
    def __init__(self):
        global food_data, filter_encodings
        if food_data is None:
            food_data = self.initialize_food_data()
        if filter_encodings is None:
            filter_encodings = self.initialize_filter_encodings()
        self.f_categories = []
        self.f_countries = []
        self.f_specials = []
        self.f_names = []

    def initialize_food_data(self):
        df = pd.read_csv("data/food_data.csv")
        data = df.to_json(orient='records')
        data = json.loads(data)
        for d in data:
            if d['special']:
                specials = d['special'].split(',')
                d['special'] = []
                for special in specials:
                    d['special'].append(special.strip())
            else:
                d['special'] = []
        return data

    def initialize_filter_encodings(self):
        file_pi = open('data/filter_encodings.obj', 'rb')
        return pickle.load(file_pi)

    def extract_filters(self, interpreted):
        for entity in interpreted['entities']:
            entity_result = self.find_entity(entity['value'])
            if entity_result:
                self.add_filter(entity_result)

        results = self.search(search_keys=[entity['value'] for entity in interpreted['entities']])
        return results

    def get_similarity(self, e1, e2):
        return np.inner(e1, e2)

    def reset_filters(self):
        self.f_categories = []
        self.f_countries = []
        self.f_specials = []
        self.f_names = []

    def find_entity(self, entity, ignore_names=True):
        global food_data, filter_encodings, sentence_encoder_model
        entity_result = None
        entity_embedding = sentence_encoder_model([entity])[0]
        max_entity_value = None
        max_entity_score = 0
        max_entity_type = None
        for f_type in filter_encodings:
            if ignore_names and f_type == "names":
                continue
            for k in filter_encodings[f_type]:
                sim_score = self.get_similarity(entity_embedding, filter_encodings[f_type][k])
                if sim_score > max_entity_score:
                    max_entity_score = sim_score
                    max_entity_type = f_type
                    max_entity_value = k
        print("Searching Entity for '{}'".format(entity))
        print(max_entity_score, max_entity_type, max_entity_value)
        if max_entity_score >= 0.6:
            entity_result = {
                'score': max_entity_score,
                'type': max_entity_type,
                'value': max_entity_value
            }
        return entity_result

    def add_filter(self, entity_result):
        if entity_result['type'] == "categories":
            self.f_categories.append(entity_result['value'])
        if entity_result['type'] == "countries":
            self.f_countries.append(entity_result['value'])
        if entity_result['type'] == "specials":
            self.f_specials.append(entity_result['value'])
        if entity_result['type'] == "names":
            self.f_names.append(entity_result['value'])

    def search(self, search_keys=None):
        global food_data
        filter_data = food_data.copy()
        results = food_data.copy()
        filtered = False
        if self.f_categories:
            new_results = []
            for food in results:
                if food['category'] in self.f_categories:
                    new_results.append(food)
            filtered = True
            results = new_results

        if self.f_countries:
            new_results = []
            for food in results:
                if food['country'] in self.f_countries:
                    new_results.append(food)
            filtered = True
            results = new_results

        if self.f_specials:
            new_results = []
            for food in results:
                for special in food['special']:
                    if special in self.f_specials:
                        new_results.append(food)
                        break
            filtered = True
            results = new_results

        if filtered is False:
            results = []

        if self.f_names:
            for food in filter_data:
                if food['name'] in self.f_names:
                    if food['id'] not in [f['id'] for f in results]:
                        results.append(food)

        if search_keys:
            for food in filter_data:
                for search_key in search_keys:
                    if food['name'].lower().find(search_key.lower())>=0:
                        if food['id'] not in [f['id'] for f in results]:
                            results.append(food)

        return results

    def generate_specials(self, user_state):
        global food_data
        sweets = []
        meals = []
        #soups = []
        for f in food_data:
            if f['category'] == "sweet":
                sweets.append(f)
            else:
                meals.append(f)
        sweet = random.choice(sweets)
        meal = random.choice(meals)
        specials = [meal, sweet]
        user_state['specials'] = specials

        return " and ".join([s['name'] for s in specials])

    def similarity_sentences(self, sentences, sentence):
        global sentence_encoder_model
        sentence_embedding = sentence_encoder_model([sentence])[0]
        sentences_embeddings = sentence_encoder_model(sentences)
        scores = np.inner(sentence_embedding, sentences_embeddings)
        return scores
