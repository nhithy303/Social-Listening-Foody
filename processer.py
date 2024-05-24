from numpy import isin
import pandas as pd
import matplotlib.pyplot as plt
import re
from underthesea import word_tokenize
from wordcloud import WordCloud
import random

colors = ['lavender', 'mediumslateblue', 'mediumpurple', 'thistle', 'indigo', 'lavenderblush',
          'bisque', 'oldlace', 'skyblue', 'lightcoral', 'peachpuff', 'seashell', 'azure']

def read_data(filename):
    filepath = f'data/{filename}.csv'
    df = pd.read_csv(filepath)
    return df

def preprocess_text(text):
    result = text.lower()
    result = re.sub(r'<.*?>', ' ', result)
    result = re.sub(r'[\d\W_]+', ' ', result)
    result = re.sub(r'\s+', ' ', result)
    fixed_words = ['trà sữa', 'bánh mì', 'bánh tráng', 'mì cay', 'phô mai', 'trân châu', 'cơm tấm', 'bún bò', 'hủ tiếu', 'gà rán']
    result = word_tokenize(result, format='text', fixed_words=fixed_words)
    return result

def preprocess_data(row):
  row = row.apply(preprocess_text)
  return row

category_reviews = {'category': [], 'rating': [], 'review_counts': []}
cuisine_reviews = {'cuisine': [], 'rating': [], 'review_counts': []}

def process_common_info(row):
    # categories
    if isinstance(row['categories'], str):
        categories = row['categories'].split('+')
        for ctg in categories:
            found = False
            for i, saved_ctg in enumerate(category_reviews['category']):
                if ctg == saved_ctg:
                    category_reviews['rating'][i] = round(((category_reviews['rating'][i] + row['rating']) / 2), 1)
                    category_reviews['review_counts'][i] += row['review_counts']
                    found = True
                    break
            if not found:
                category_reviews['category'].append(ctg)
                category_reviews['rating'].append(row['rating'])
                category_reviews['review_counts'].append(row['review_counts'])
    
    # cuisine
    if isinstance(row['cuisine'], str):
        cuisine = row['cuisine'].split('+')
        for csn in cuisine:
            found = False
            for i, saved_csn in enumerate(cuisine_reviews['cuisine']):
                if csn == saved_csn:
                    cuisine_reviews['rating'][i] = round(((cuisine_reviews['rating'][i] + row['rating']) / 2), 1)
                    cuisine_reviews['review_counts'][i] += row['review_counts']
                    found = True
                    break
            if not found:
                cuisine_reviews['cuisine'].append(csn)
                cuisine_reviews['rating'].append(row['rating'])
                cuisine_reviews['review_counts'].append(row['review_counts'])

def distribution_district(df):
    district_counts = df['district'].value_counts()
    picked_colors = []
    for i in range(len(district_counts)):
        color_idx = random.randint(0, len(colors) - 1)
        picked_colors.append(colors[color_idx])
    fig, ax = plt.subplots(figsize=(16, 9))
    # Horizontal Bar Plot
    ax.barh(district_counts.index, district_counts, color=picked_colors)
    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    # Remove x, y ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)
    # Show top values 
    ax.invert_yaxis()
    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5, 
                str(round((i.get_width()), 2)),
                fontsize = 10, fontweight ='bold',
                color ='grey')
    # plt.show()
    plt.savefig('utils/distribution_district.png')

def distribution_category(df):
    pass
    
def most_common_food_wordcloud(fullname, menu):
    text_column = ' '.join(fullname) + ' '.join(menu)
    wordcloud2 = WordCloud().generate(text_column)
    plt.imshow(wordcloud2)
    plt.axis("off")
    # plt.show()
    plt.savefig('utils/most_common_food_wordcloud.png')

def most_common_food_plot(fullname, menu, n_words=20):
    word_counts = {}
    for food in fullname:
        for word in food.split():
            word_counts[word] = word_counts.get(word, 0) + 1
    for food in menu:
        for word in food.split():
            word_counts[word] = word_counts.get(word, 0) + 1
    most_common_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:n_words]

    words, counts = zip(*most_common_words)
    plt.figure(figsize=(16, 9))
    plt.bar(words, counts, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Words')
    plt.ylabel('Count')
    plt.tick_params(axis='x', labelrotation=45)
    # plt.title('Most 20 of Word Count of Each Word in Column Message of Dataframe df')
    # plt.show()
    plt.savefig('utils/most_common_food_plot.png')

# df_restaurants = read_data('restaurants')
df_common = read_data('common_info')
df_menu = read_data('menu')
df_common['processed_name'] = preprocess_data(df_common['fullname'])
df_menu['processed_menu'] = preprocess_data(df_menu['menu'])
most_common_food_wordcloud(df_common['processed_name'], df_menu['processed_menu'])
most_common_food_plot(df_common['processed_name'], df_menu['processed_menu'], 20)
distribution_district(df_common)
df_common.apply(process_common_info, axis=1)

total_stores = len(df_common)