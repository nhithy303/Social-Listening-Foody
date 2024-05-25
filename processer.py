import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
from underthesea import word_tokenize
from wordcloud import WordCloud
import random

colors = ['lavender', 'mediumslateblue', 'mediumpurple', 'thistle', 'indigo', 'lavenderblush',
          'bisque', 'oldlace', 'skyblue', 'lightcoral', 'peachpuff', 'seashell', 'azure']

colormaps = ['coolwarm', 'Purples', 'Blues', 'Pastel1', 'PuBu', 'Paired']

# sentiments: [{'negative': 0, 'neural': 0, 'positive': 0}]
category_reviews = {'category': [], 'avg_rating': [], 'sentiments': [], 'review_counts': []}
cuisine_reviews = {'cuisine': [], 'avg_rating': [], 'sentiments': [], 'review_counts': []}

# thresholds to determine sentiments if lower than defined values
sentiment_thresholds = {'negative': 5, 'neural': 7, 'positive': 10}

filepath_charts = 'static/charts/'

def pick_random_colors(n_colors):
    picked_colors = []
    for i in range(len(n_colors)):
        color_idx = random.randint(0, len(colors) - 1)
        picked_colors.append(colors[color_idx])
    return picked_colors

def read_data(filename):
    filepath = f'data/{filename}.csv'
    df = pd.read_csv(filepath)
    return df

def preprocess_text(text):
    result = text.lower()
    result = re.sub(r'<.*?>', ' ', result)
    result = re.sub(r'[\d\W_]+', ' ', result)
    result = re.sub(r'\s+', ' ', result)
    fixed_words = ['trà sữa', 'bánh mì', 'bánh tráng', 'mì cay', 'phô mai', 'trân châu',
                   'cơm tấm', 'bún bò', 'hủ tiếu', 'gà rán', 'bánh canh', 'gỏi cuốn', 'bánh cuốn']
    result = word_tokenize(result, format='text', fixed_words=fixed_words)
    return result

def preprocess_data(row):
  row = row.apply(preprocess_text)
  return row

def classify_sentiment(rating):
    if rating <= sentiment_thresholds['negative']:
        return 'negative'
    if rating <= sentiment_thresholds['neural']:
        return 'neural'
    return 'positive'

def process_common_info(row):
    # categories
    if isinstance(row['categories'], str):
        categories = row['categories'].split('+')
        for ctg in categories:
            found = False
            sent = classify_sentiment(row['rating'])
            for i, saved_ctg in enumerate(category_reviews['category']):
                if ctg == saved_ctg:
                    category_reviews['avg_rating'][i] = round(((category_reviews['avg_rating'][i] + row['rating']) / 2), 1)
                    category_reviews['sentiments'][i][sent] += 1
                    category_reviews['review_counts'][i] += row['review_counts']
                    found = True
                    break
            if not found:
                category_reviews['category'].append(ctg)
                category_reviews['avg_rating'].append(row['rating'])
                category_reviews['sentiments'].append({
                    'negative': 0,
                    'neural': 0,
                    'positive': 0
                })
                category_reviews['sentiments'][len(category_reviews['category']) - 1][sent] += 1
                category_reviews['review_counts'].append(row['review_counts'])
    
    # cuisine
    if isinstance(row['cuisine'], str):
        cuisine = row['cuisine'].split('+')
        for csn in cuisine:
            found = False
            sent = classify_sentiment(row['rating'])
            for i, saved_csn in enumerate(cuisine_reviews['cuisine']):
                if csn == saved_csn:
                    cuisine_reviews['avg_rating'][i] = round(((cuisine_reviews['avg_rating'][i] + row['rating']) / 2), 1)
                    cuisine_reviews['sentiments'][i][sent] += 1
                    cuisine_reviews['review_counts'][i] += row['review_counts']
                    found = True
                    break
            if not found:
                cuisine_reviews['cuisine'].append(csn)
                cuisine_reviews['avg_rating'].append(row['rating'])
                cuisine_reviews['sentiments'].append({
                    'negative': 0,
                    'neural': 0,
                    'positive': 0
                })
                cuisine_reviews['sentiments'][len(cuisine_reviews['cuisine']) - 1][sent] += 1
                cuisine_reviews['review_counts'].append(row['review_counts'])

def calculate_percentage(row):
    total = row['negative'] + row['neural'] + row['positive']
    row['negative'] = row['negative'] / total * 100
    row['neural'] = row['neural'] / total * 100
    row['positive'] = row['positive'] / total * 100
    return row

def plot_food_category_sentiments():
    n_categories = len(category_reviews['category'])
    n_bars = 10
    n_charts = 0
    start_idx = 0
    end_idx = 0
    while end_idx < n_categories:
        start_idx = n_charts * n_bars
        end_idx = start_idx + n_bars
        end_idx = n_categories if end_idx > n_categories else end_idx

        df_sentiments = pd.concat([
            pd.DataFrame({'category': category_reviews['category'][start_idx:end_idx]}),
            pd.DataFrame(category_reviews['sentiments'][start_idx:end_idx])
        ], axis=1)
        df_sentiments = df_sentiments.apply(calculate_percentage, axis=1)
        plt.figure(figsize=(12, 7))
        df_sentiments.plot(
            x='category',
            kind='barh',
            stacked=True,
            xlabel='Percentage (%)',
            ylabel='Category',
            fontsize=10,
            colormap=colormaps[random.randint(0, len(colormaps) - 1)]
        )
        plt.legend(loc='upper right')
        plt.savefig(filepath_charts + f'food_category_sentiments_{n_charts}.png')

        n_charts += 1
    return n_charts

def plot_cuisine_sentiments():
    n_cuisine = len(cuisine_reviews['cuisine'])
    n_bars = 10
    n_charts = 0
    start_idx = 0
    end_idx = 0
    while end_idx < n_cuisine:
        start_idx = n_charts * n_bars
        end_idx = start_idx + n_bars
        end_idx = n_cuisine if end_idx > n_cuisine else end_idx

        df_sentiments = pd.concat([
            pd.DataFrame({'cuisine': cuisine_reviews['cuisine'][start_idx:end_idx]}),
            pd.DataFrame(cuisine_reviews['sentiments'][start_idx:end_idx])
        ], axis=1)
        df_sentiments = df_sentiments.apply(calculate_percentage, axis=1)
        plt.figure(figsize=(12, 7))
        df_sentiments.plot(
            x='cuisine',
            kind='barh',
            stacked=True,
            xlabel='Percentage (%)',
            ylabel='Cuisine',
            fontsize=10,
            colormap=colormaps[random.randint(0, len(colormaps) - 1)]
        )
        plt.legend(loc='upper right')
        plt.savefig(filepath_charts + f'cuisine_sentiments_{n_charts}.png')

        n_charts += 1
    return n_charts

def distribution_district(df):
    district_counts = df['district'].value_counts()
    picked_colors = pick_random_colors(district_counts)
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
    plt.savefig(filepath_charts + 'distribution_district.png')

def distribution_category(df):
    pass
    
def most_common_food_wordcloud(fullname, menu):
    text_column = ' '.join(fullname) + ' '.join(menu)
    wordcloud2 = WordCloud().generate(text_column)
    plt.imshow(wordcloud2)
    plt.axis("off")
    # plt.show()
    plt.savefig(filepath_charts + 'most_common_food_wordcloud.png')

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
    # plt.show()
    plt.savefig(filepath_charts + 'most_common_food_plot.png')

def fetch_data():
    # df_restaurants = read_data('restaurants')
    df_common = read_data('common_info')
    df_menu = read_data('menu')

    df_common['processed_name'] = preprocess_data(df_common['fullname'])
    df_menu['processed_menu'] = preprocess_data(df_menu['menu'])
    df_common.apply(process_common_info, axis=1)

    most_common_food_wordcloud(df_common['processed_name'], df_menu['processed_menu'])
    most_common_food_plot(df_common['processed_name'], df_menu['processed_menu'], 20)
    distribution_district(df_common)
    n_category_charts = plot_food_category_sentiments()
    n_cuisine_charts = plot_cuisine_sentiments()

    total_stores = len(df_common)
    total_reviews = df_common['review_counts'].sum()

    df_processed = read_data('processed_info')
    new_data = {
        'fetch_counts': [df_processed['fetch_counts'].iloc[0] + 1],
        'total_stores': [total_stores],
        'total_categories': [len(category_reviews['category'])],
        'total_cuisine': [len(cuisine_reviews['cuisine'])],
        'total_reviews': [total_reviews],
        'n_category_charts': [n_category_charts],
        'n_cuisine_charts': [n_cuisine_charts]
    }
    pd.DataFrame(new_data).to_csv(f'data/processed_info.csv', index=False)
    return new_data

def get_avalaible_data():
    df_processed = read_data('processed_info')
    return df_processed.to_dict('list')

fetch_data()