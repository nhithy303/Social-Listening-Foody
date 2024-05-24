import os
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from bs4 import BeautifulSoup
from variables import *
import time
import pandas as pd

class FoodyScraper:
    def __init__(self):
        self.browser = None

    def __open_browser(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.browser = webdriver.Chrome(options=options)

    def __login(self):
        self.browser.get(get_urls('login', category=food_categories[3]))
        # username
        input_username = self.browser.find_element(By.ID, 'Email')
        input_username.send_keys(my_account['username'])
        # password
        input_password = self.browser.find_element(By.ID, 'Password')
        input_password.send_keys(my_account['password'])
        # submit
        btn_login = self.browser.find_element(By.ID, 'bt_submit')
        btn_login.click()

    def __get_restaurant_list(self, n_pages=1):
        # scroll to show more
        for i in range(n_pages):
            btn_showmore = None
            try:
                btn_showmore = WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='scrollLoadingPage']/a"))
                )
            except Exception as e:
                print(f'=== ERROR: {e}')
            else:
                if btn_showmore is not None:
                    btn_showmore.click()

        # extract html
        content = self.browser.page_source
        soup = BeautifulSoup(content, 'html.parser')

        # get list of restaurants
        res_list = []
        restaurants = soup.find_all('div', class_='resname')
        for res in restaurants:
            res_name = res.a['href']
            if 'thuong-hieu' in res_name:
                self.browser.get(get_urls('restaurant', res_name=res_name)[0])
                sub_content = self.browser.page_source
                soup = BeautifulSoup(sub_content, 'html.parser')
                branches = soup.find_all('div', class_='ldc-item-h-name')
                [res_list.append(br.a['href']) for br in branches]
            else:
                res_list.append(res_name)
        return res_list
        
    def __get_restaurant_data(self, res_name):
        res_urls = get_urls('restaurant', res_name=res_name)

        """
        COMMON INFORMATION & REVIEWS
        """
        self.browser.get(res_urls[0])

        # scroll to the end of page
        prev_height = -1
        max_scrolls = 100
        scroll_counts = 0        
        while (scroll_counts < max_scrolls):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == prev_height:
                break
            scroll_counts += 1
            prev_height = new_height

        WebDriverWait(self.browser, 20).until(
            lambda wd: wd.execute_script('return document.readyState') == 'complete'
        )

        # show all comments
        # while (1):
        #     btn_showmore = None
        #     try:
        #         btn_showmore = WebDriverWait(self.browser, 10).until(
        #             # EC.element_to_be_clickable((By.XPATH, "//div[@class='list-reviews']//a[@class='fd-btn-more']"))
        #             # EC.presence_of_all_elements_located((By.CLASS_NAME, 'fd-btn-more'))
        #             # EC.visibility_of_element_located((By.XPATH, "//div[@class='list-reviews']//a[@class='fd-btn-more']"))
        #             EC.visibility_of_all_elements_located((By.CLASS_NAME, 'fd-btn-more'))
        #         )
        #     except exceptions.NoSuchElementException:
        #         print('ALERT'.center(20, '='))
        #         btn_showmore = None
        #         break
        #     except exceptions.TimeoutException:
        #         print('ALERT'.center(20, '='))
        #         btn_showmore = None
        #         break
        #     except exceptions.ElementNotInteractableException:
        #         print('ALERT'.center(20, '='))
        #         btn_showmore = None
        #         break
        #     except exceptions.StaleElementReferenceException:
        #         print('ALERT'.center(20, '='))
        #         btn_showmore = None
        #         break
        #     else:
        #         btn_showmore = self.browser.find_elements(By.CLASS_NAME, 'fd-btn-more')
        #         if btn_showmore is not None and len(btn_showmore) > 1:
        #             btn_showmore[1].click()
        #         else:
        #             break

        # extract html
        content = self.browser.page_source
        soup = BeautifulSoup(content, 'html.parser')

        # get common info
        common_info = soup.find('div', class_='res-common')
        district = common_info.find_all('span', attrs={'itemprop': 'itemListElement'})[1].a.span.string
        fullname = common_info.find('div', class_='main-info-title').h1.string
        rating = common_info.find('div', class_='microsite-point-avg').string.strip()
        review_counts = common_info.find('div', class_='microsite-review-count').string

        bonus_info = soup.find_all('div', class_='new-detail-info-area')
        # print(f'=== BONUS INFO ===\n{bonus_info}')
        categories_container = bonus_info[-2].find_all('div')[-1].find_all('a')[:-1]
        categories = '+'.join([ctg.string.strip() for ctg in categories_container])
        cuisine_container = bonus_info[-4].find_all('div')[-1].find_all('a')[:-1]
        cuisine = '+'.join([csn.string.strip() for csn in cuisine_container])

        print('\n=== COMMON INFO ===')
        print(f'{district} | {fullname} | {rating} | {review_counts} | {categories} | {cuisine}')

        # get reviews
        # reviews_containers = soup.find_all('li', class_='review-item')
        # reviews = []
        # for rv in reviews_containers:
        #     reviews.append({
        #         'comment': rv.find('div', class_='rd-des').span.string,
        #         'rating': rv.find('div', class_='review-points').span.string
        #     })

        """
        MENU DETAIL
        """
        self.browser.get(res_urls[1])

        WebDriverWait(self.browser, 20).until(
            lambda wd: wd.execute_script('return document.readyState') == 'complete'
        )

        # turn off outside-of-service-hours modal
        # self.browser.switch_to.active_element
        # btn_okay = None
        # try:
        #     btn_okay = WebDriverWait(self.browser, 10).until(
        #         # EC.presence_of_all_elements_located((By.XPATH, "//div[@class='is-active']//button"))
        #         EC.visibility_of_element_located((By.XPATH, "//div[@class='is-active']//button"))
        #         # EC.presence_of_all_elements_located((By.CLASS_NAME, 'close'))
        #     )
        # except exceptions.NoSuchElementException:
        #     btn_okay = None
        #     print('ALERT'.center(20, '='))
        # except exceptions.TimeoutException:
        #     btn_okay = None
        #     print('ALERT'.center(20, '='))
        # except exceptions.ElementNotInteractableException:
        #     btn_okay = None
        #     print('ALERT'.center(20, '='))
        # except exceptions.StaleElementReferenceException:
        #     btn_okay = None
        #     print('ALERT'.center(20, '='))
        # else:
        #     for b in btn_okay:
        #         print(f'=== BUTTON OKAY: {b}\n')
        #     # btn_okay = self.browser.find_elements(By.XPATH, "//div[@class='is-active']//button")
        #     if btn_okay is not None and len(btn_okay) > 0:
        #         # btn_okay[0].click()
        #         self.browser.execute_script("arguments[0].click();", btn_okay[0])
        # self.browser.switch_to.default_content()

        # scroll to the end of page while scraping dishes
        prev_height = -1
        max_scrolls = 100
        scroll_counts = 0
        menu = []
        
        while (1):
            # extract html
            content = self.browser.page_source
            soup = BeautifulSoup(content, 'html.parser')

            # get menu
            menu_containers = soup.find_all('h2', class_='item-restaurant-name')
            menu.extend([dish.string for dish in menu_containers if dish not in menu])

            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            scroll_counts += 1
            if new_height == prev_height or scroll_counts >= max_scrolls:
                break
            prev_height = new_height

        print('=== MENU ===')
        print(menu)
        
        # # extract html
        # content = self.browser.page_source
        # soup = BeautifulSoup(content, 'html.parser')

        # # get menu
        # menu_containers = soup.find_all('h2', class_='item-restaurant-name')
        # menu = [dish.string for dish in menu_containers]
        # print('\n=== MENU ===')
        # print(menu)

        return {
            'href': res_name,
            'fullname': fullname,
            'district': district,
            'rating': rating,
            'review_counts': review_counts,
            'menu': menu,
            'categories': categories,
            'cuisine': cuisine
            # 'reviews': reviews
        }
    
    def __construct_dataframe(self, data):
        # common dataframe
        df_common = pd.DataFrame(data, columns=['href', 'fullname', 'district', 'rating', 'review_counts', 'categories', 'cuisine'])
        
        # menu dataframe
        href_list = []
        menu_list = []
        for item in data:
            href_list.extend([item['href']] * len(item['menu']))
            menu_list.extend(item['menu'])
        df_menu = pd.DataFrame({'href': href_list, 'menu': menu_list})

        # reviews dataframe
        # href_list = []
        # reviews_list = []
        # for item in data:
        #     href_list.extend([item['href']] * len(item['reviews']))
        #     reviews_list.extend(item['reviews'])
        # df_reviews = pd.concat([
        #     pd.DataFrame({'href': href_list}),
        #     pd.DataFrame(reviews_list)
        # ], axis=1)

        # return df_common, df_menu, df_reviews
        return df_common, df_menu
    
    def __save_into_csv(self, df, filename):
        filepath = f"data/{filename}.csv"
        df.to_csv(filepath, index=False)
        print(f'=== Successfully saved {filename}.csv')

    def __read_data(self, filename):
        filepath = f"data/{filename}.csv"
        if os.path.isfile(filepath):
            return pd.read_csv(filepath)
        return None
    
    def process_pipeline(self, **kwargs):
        self.__open_browser()
        self.__login()

        if kwargs['action'] == 'get_restaurant_list':
            res_list = self.__get_restaurant_list(kwargs['n_pages'])
            df_restaurants = pd.DataFrame({'href': res_list})
            df_restaurants_old =  self.__read_data('restaurants')
            if df_restaurants_old is not None:
                if len(df_restaurants) <= len(df_restaurants_old):
                    print('=== ALERT: Shorter list!')
                    return
            self.__save_into_csv(df_restaurants, 'restaurants')
            
        elif kwargs['action'] == 'get_restaurant_data':
            df_restaurants = self.__read_data('restaurants')
            if df_restaurants is None or kwargs['from_idx'] >= len(df_restaurants):
                return
            
            res_data = []
            to_idx = min(kwargs['to_idx'], len(df_restaurants))
            for i in range(kwargs['from_idx'], to_idx):
                res_data.append(self.__get_restaurant_data(df_restaurants['href'].iloc[i]))

            # df_common, df_menu, df_reviews = self.__construct_dataframe(res_data)
            df_common, df_menu = self.__construct_dataframe(res_data)
            
            df_common_old = self.__read_data('common_info')
            df_common_new = pd.concat([df_common_old, df_common], axis=0)
            self.__save_into_csv(df_common_new, 'common_info')

            df_menu_old = self.__read_data('menu')
            df_menu_new = pd.concat([df_menu_old, df_menu], axis=0)
            self.__save_into_csv(df_menu_new, 'menu')

            # df_reviews_old = self.__read_data('reviews')
            # df_reviews_new = pd.concat([df_reviews_old, df_reviews], axis=0)
            # self.__save_into_csv(df_reviews_new, 'reviews')

# initialize
scraper = FoodyScraper()

# get list of restaurants
# scraper.process_pipeline(action='get_restaurant_list', n_pages=100)

# get data of restaurants
missed_rounds = []
for round in range(70, 78):
    try:
        scraper.process_pipeline(action='get_restaurant_data', from_idx=round*10, to_idx=(round+1)*10)
    except:
        pass
    finally:
        missed_rounds.append(round)