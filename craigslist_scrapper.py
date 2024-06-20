from bs4 import BeautifulSoup #Webscraping
import requests #http requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import time
import random
from alive_progress import alive_bar

def level1_page(l1_url):
    car_details = ['N/A','N/A','N/A','N/A','N/A','N/A']
    car_attributes = []
    not_important = 0
    l1r = requests.get(l1_url)
    l1_html_page = l1r.text

    l1_soup = BeautifulSoup(l1_html_page, "lxml")

    l1_item = l1_soup.find_all('p', class_= 'attrgroup')[1]
    for span in l1_item.find_all('span'):
        car_attributes = span.text.split(':')
        if(car_attributes[0] == 'condition'):
            car_details[0] = car_attributes[1]
            continue
        elif(car_attributes[0] == 'drive'):
            car_details[1] = car_attributes[1]
            continue
        elif(car_attributes[0] == 'odometer'):
            car_details[2] = car_attributes[1]
            continue
        elif(car_attributes[0] == 'title status'):
            car_details[3] = car_attributes[1]
            continue
        elif(car_attributes[0] == 'transmission'):
            car_details[4] = car_attributes[1]
            continue
        elif(car_attributes[0] == 'type'):
            car_details[5] = car_attributes[1]
            continue
        else:
            not_important = 1

    return car_details

def craigs_list(locations, min_price, max_price, min_year, max_year):
    
    dfs = []
    master = []

    for location in locations:
        
        s = 0

        url = "https://"+ str(location) + ".craigslist.org/search/cta?s=" + str(s) + "&min_price=" + str(min_price) + "&max_price=" + str(max_price) + "&min_auto_year=" + str(min_year) +"&max_auto_year=" + str(max_year)
        r  = requests.get(url)
        html_page = r.text
        soup = BeautifulSoup(html_page, "lxml")
        total = str(soup.findAll("span", {"class": "totalcount"})[0].contents)[2:-2]
        count = int(total)/120
        while(count > 0):
            url = "https://"+ str(location) + ".craigslist.org/search/cta?s=" + str(s) + "&min_price=" + str(min_price) + "&max_price=" + str(max_price) + "&min_auto_year=" + str(min_year) +"&max_auto_year=" + str(max_year)
            print(url)
            r  = requests.get(url)
            if(r.status_code !=200):
                print(r.status_code)
            html_page = r.text
            soup = BeautifulSoup(html_page, "lxml")
            values = add_to_df(soup)
            s = s + 120
            count = count - 1
            craig_df = pd.DataFrame(np.column_stack([values[0], values[1], values[2],values[3], values[4],values[5], values[6], values[7],values[8], values[9],values[10]]),
                columns = ["Price", "Location","Title","Link", "Date","condition", "drive", "odometer", "title_status", "transmission", "car_type"])
            # craig_df = craig_df.dropna()
        
            dfs.append(craig_df)
            craig_df = 0
            pd.concat(dfs).to_csv("before_crash_{}_{}_minprice_{}_maxprice_{}_year_{}_{}.csv".format(count,location,min_price,max_price,min_year,max_year))
            x = random.randint(10, 30)
            time.sleep(x)
        #concat all dfs here
        d = pd.concat(dfs)
        master.append(d)
        d=[]
        dfs = []
    
    return master

def graph_cars(df):
    df2 = df.iloc[:, :2].copy()
    df2['Price'] = df2['Price'].str[1:]
    df2['Price'] = df2['Price'].str.replace(',', '').astype(int)
    df2.plot(kind='hist', y = "Price")
    plt.show()
	
	
def add_to_df(soup):
    link_list = []
    listing_price = []
    prices = []
    hoods = []
    titles = []
    make_model = []
    year = []
    miles = []
    date = []
    condition= []
    drive=[]
    odometer = []
    title_status = []
    transmission=[] 
    car_type=[]
    car_details = []
    p_b = 0

    with alive_bar(int(120), ctrl_c=True, title=f'Download {p_b}') as bar:
        for car in soup.find_all('li', class_= 'result-row'):
            bar()
            p_b = p_b + 1
            try:
                location = str(car.find(class_ = "result-hood").contents)
                hoods.append(location[4:-3])
            except:
                hoods.append('N/A')
                    
            try:
                prices.append(car.find(class_ = "result-price").contents)
            except:
                #not possible
                prices.append('N/A')
                    
            try:
                titles.append(car.find(class_ = "result-title hdrlnk").contents)
            except:
                titles.append('N/A')
                    
            try:
                date.append(car.find(class_ = "result-date").contents)
            except:
                date.append('N/A')
            
            try:
                level_1_url = car.find("a", {"class": "result-title hdrlnk"}).get("href")
                # x = random.randint(10, 30)
                # time.sleep(x)
                car_details = level1_page(level_1_url)
                condition.append(car_details[0])
                drive.append(car_details[1])
                odometer.append(car_details[2])
                title_status.append(car_details[3])
                transmission.append(car_details[4])
                car_type.append(car_details[5])
                link_list.append(level_1_url)
            except:
                link_list.append('N/A')

        
    return [prices, hoods, titles,link_list, date, condition, drive, odometer, title_status, transmission, car_type]
	
	
	
locations = ["vancouver", "toronto"]
# locations = ["vancouver"]
min_price = 15000
max_price= 25000
min_year = 2010
max_year = 2023
df = craigs_list(locations, min_price, max_price, min_year, max_year)

# Save the dataframes into csv files
df[0].to_csv("Vancouver.csv")
df[1].to_csv("Toronto.csv")

print("Vancouver")
# graph_cars(df[0])
print("Toronto")
# graph_cars(df[1])