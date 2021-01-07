# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 22:41:52 2020

@author: jujuc
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import csv

from selenium.webdriver.chrome.options import Options
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe", chrome_options = chrome_options)

class Scrapper:
    
    links = []
    reviews_links = []
    content = {
        "name": [],
        "adress": [],
        "totalReviews": [],
        "score": [],
        "description": [],
        "categories": [],
        "equipments": [],
        "roomFeats": [],
        "roomTypes": [],
        "img": [],
        "url":links
        }
    reviews = {
        "hotelName": [],
        "hotelAdress":[],
        "username": [],
        "rating": [],
        "title": [],
        "comment": [],
        "profile": []
        }
    
    
    def __init__(self, url, nb_pages):
        self.extract_links(url, nb_pages)
        print({i:self.links.count(i) for i in self.links})
        self.fetch_links()

        
    def extract_links(self, url, nb_pages):
        driver.get(url)
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]').click()
        for i in range(0, nb_pages):
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            for link in soup.findAll('a', {'property_title','price'}):
                hotel_link = 'https://www.tripadvisor.com' + link.get('href')
                self.links.append(hotel_link)
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="taplc_main_pagination_bar_dusty_hotels_resp_0"]/div/div/div/span[2]').click()
        driver.close()
        

    def fetch_links(self):
        i=0
        for link in self.links:
            i += 1
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            self.extract_content(soup)
            
            #Décision arbitraire : 10 commentaires par hotels
            url = link.split('-Reviews')
            self.reviews_links += [url[0] + '-Reviews-or' + str(x) for x in range(1,10,5)]
            print('Extract content : ', round(i/len(self.links)*100, 2), '%')  
        
        i=0
        for review_link in self.reviews_links:
            i += 1
            data_rev = requests.get(review_link).text
            soup_rev = BeautifulSoup(data_rev, 'lxml')
            self.extract_reviews(soup_rev)
            print('Extract reviews : ', round(i/len(self.reviews_links)*100, 2), '%')  
                  
    def extract_content(self, soup):
        
        components = soup.findAll('div', {"class": "_1nAmDotd"})
        images = soup.findAll('div', {"class":"ZVAUHZqh"})

        try:
            self.content["name"] += [soup.find('h1', id='HEADING').text]
        except:
            print(soup)
        self.content["adress"] += [soup.find('span', {"class": "_3ErVArsu jke2_wbp"}).text]
        try:
            self.content["totalReviews"] += [soup.find('span', {"class": "_33O9dg0j"}).text.replace("&nbsp;", "").replace(" avis", "")]
        except:
            self.content["totalReviews"] += [np.nan]
        self.content["score"] += [soup.find('span', {"class": "_3cjYfwwQ"}).text] 
        self.content["description"] += [soup.find('div', {"class": "cPQsENeY"}).text]
        try:
            self.content["categories"] += [soup.find('svg', {"class": "_2aZlo29m"}).get('title').replace(".0 of 5 bubbles", "").replace(" of 5 bubbles", "")]
        except:
            self.content["categories"] += [np.nan]
        try:
            self.content["equipments"] += ['|'.join(list(map(lambda eq : eq.text, components[0].findAll('div', {"class": "_2rdvbNSg"}))))]
        except:
            self.content["equipments"] += [np.nan]
        try:    
            self.content["roomFeats"] += ['|'.join(list(map(lambda ft : ft.text, components[1].findAll('div', {"class": "_2rdvbNSg"}))))]
        except:
            self.content["roomFeats"] += [np.nan]
        try:
            self.content["roomTypes"] += ['|'.join(list(map(lambda ty : ty.text if len(ty)>0 else None, components[2].findAll('div', {"class": "_2rdvbNSg"}))))]
        except:
            self.content["roomTypes"] += [np.nan]
            
        try:
            self.content["img"] += list(map(lambda img : img.get('src'), images[0].findAll('img', {"class": "_1a4WY7aS"})))
        except:
            self.content["img"] += [np.nan]
            

    def extract_reviews(self, soup):
    
        self.reviews["hotelName"] += [soup.find('h1', id='HEADING').text]*len(soup.findAll('a', class_="ui_header_link _1r_My98y"))
        self.reviews["hotelAdress"] += [soup.find('span', {"class": "_3ErVArsu jke2_wbp"}).text]*len(soup.findAll('a', class_="ui_header_link _1r_My98y"))
        self.reviews["username"] += list(map(lambda cat : cat.text, soup.findAll('a', class_="ui_header_link _1r_My98y")))
        self.reviews["rating"] += list(map(lambda rat : rat.find('span').get('class')[1].replace("bubble_", "").replace("0", ""), soup.findAll('div', {"class": "nf9vGX55"})))
        self.reviews["title"] += list(map(lambda title : title.text, soup.findAll('div', {"class": "glasR4aX"}))) 
        self.reviews["comment"] += list(map(lambda com : com.text, soup.findAll('q', {"class": "IRsGHoPm"})))
        self.reviews["profile"] += list(map(lambda pro : pro.get('href'), soup.findAll('a', class_="ui_header_link _1r_My98y")))
        
        
    def get_reviews(self):
        return self.reviews
    
    
    def get_hotel(self):
        return self.content
    
    def get_reviews_url(self):
        return self.reviews_links