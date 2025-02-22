# -*- coding: utf-8 -*-
"""Code Merge Dataset

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LkitFv3O9o8PyJw_8O8o7PUHUoaVwrAD

#MERGE DATASET X
"""

import pandas as pd

# Baca file CSV
data_awal_x = pd.read_csv('/content/data-awal-tweet.csv', delimiter=';')  # file awal
data_tambahan_x_1 = pd.read_csv('/content/data-tambahan1-tweet.csv', delimiter=',')  # file tambahan 1
data_tambahan_x_2 = pd.read_csv('/content/data-tambahan2-tweet.csv', delimiter=',')  # file tambahan 2

# Merge seluruh dataset menjadi 1
data_x = pd.concat([data_awal_x, data_tambahan_x_1,data_tambahan_x_2], ignore_index=True)

# Tampilan DataFrame hasil gabungan
data_x.head()

data_x.info()

# Menyimpan dataset
data_x.to_csv('dataset_x.csv', index=False)

"""#MERGE DATASET COMMENT-YOUTUBE"""

# Baca file
data_awal_youtube = pd.read_excel('/content/data-awal-youtube-comments.xlsx')  # file awal

data_tambahan_youtube_1_cnn = pd.read_csv('/content/youtube-comments-CNN.csv', delimiter=',',encoding='utf-8')  # file tambahan 1
data_tambahan_youtube_2_kompascom = pd.read_csv('/content/youtube-comments-Kompas.com.csv', delimiter=',',encoding='utf-8')  # file tambahan 2
data_tambahan_youtube_3_kompastv = pd.read_csv('/content/youtube-comments-KompasTV.csv', delimiter=',',encoding='utf-8')  # file tambahan 3
data_tambahan_youtube_4_metrotv = pd.read_csv('/content/youtube-comments-MetroTV.csv', delimiter=',',encoding='utf-8')  # file tambahan 4

# Merge seluruh dataset menjadi 1
data_youtube = pd.concat([
    data_awal_youtube,
    data_tambahan_youtube_1_cnn,
    data_tambahan_youtube_2_kompascom,
    data_tambahan_youtube_3_kompastv,
    data_tambahan_youtube_4_metrotv], ignore_index=True)

data_youtube

data_youtube.info()

# Menyimpan dataset
data_youtube.to_csv('dataset_youtube.csv', index=False)

"""#MERGE DATASET COMMENT-INSTAGRAM

"""

# Baca file
data_awal_instagram = pd.read_csv('//content/data-awal-instagram-comment.csv',delimiter=';')  # file awal

data_tambahan_instagram_1_cnn = pd.read_csv('/content/instagram-cnnid.csv', delimiter=',',encoding='utf-8')  # file tambahan 1
data_tambahan_instagram_2_kompascom = pd.read_csv('/content/instagram-comment-kompascom.csv', delimiter=',',encoding='utf-8')  # file tambahan 2
data_tambahan_instagram_3_suaradotcom = pd.read_csv('/content/instagram-comment-suaradotcom.csv', delimiter=',',encoding='utf-8')  # file tambahan 3
data_tambahan_instagram_4_terasinfobkn = pd.read_csv('/content/instagram-comment-terasinfobkn.csv', delimiter=',',encoding='utf-8')  # file tambahan 4
data_tambahan_instagram_5_detikcom = pd.read_csv('/content/instagram-comment-detikcom.csv', delimiter=',',encoding='utf-8')  # file tambahan 5

# Merge seluruh dataset menjadi 1
data_instagram = pd.concat([
    data_awal_instagram,
    data_tambahan_instagram_1_cnn,
    data_tambahan_instagram_2_kompascom,
    data_tambahan_instagram_3_suaradotcom,
    data_tambahan_instagram_4_terasinfobkn,
    data_tambahan_instagram_5_detikcom], ignore_index=True)

data_instagram

data_instagram.info()

# Menyimpan dataset
data_instagram.to_csv('dataset_instagram.csv', index=False)

"""#MERGE ALL DATASET"""

#upload dataset

data_x = pd.read_csv('/content/dataset_x.csv')
data_youtube = pd.read_csv('/content/dataset_youtube.csv')
data_instagram = pd.read_csv('/content/dataset_instagram.csv')

"""dataset X"""

#baca tiap dataset
data_x

data_x.info()

#menyisakan bagian tweet dari data X , yaitu kolom full_text
data_x = data_x[['full_text']]
data_x

"""dataset Youtube"""

data_youtube

data_youtube.info()

#menyisakan bagian comment dari data youtube , yaitu kolom textDisplay
data_youtube = data_youtube[['textDisplay']]
data_youtube

"""dataset instagram"""

data_instagram

data_instagram.info()

#menyisakan bagian comment dari data instagram , yaitu kolom comment
data_instagram = data_instagram[['comment']]
data_instagram

"""Menggabungkan seluruh data"""

Dataset = pd.concat([data_x,
                     data_youtube.rename(columns={'textDisplay': 'full_text'}),
                     data_instagram.rename(columns={'comment': 'full_text'})], ignore_index=True)

Dataset

#menghapus baris yang NaN dan mereset indeks
Dataset.dropna(inplace=True)
Dataset.reset_index(drop=True, inplace=True)
Dataset

"""#Menyimpan Keseluruhan Dataset"""

# Menyimpan dataset
Dataset.to_csv('Dataset.csv', index=False)