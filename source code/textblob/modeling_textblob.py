# -*- coding: utf-8 -*-
"""Modeling Textblob.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_BClouWWYIIvJALm2gWwAk-W8q-PEws-

# Import and install required Librarie/Packages**
"""

# Package/Library for stemming Bahasa
!pip install Sastrawi
# Package/Library for use model transformers
!pip install transformers

!pip install googletrans==3.1.0a0

# Commented out IPython magic to ensure Python compatibility.
# NLP
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import string
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from wordcloud import WordCloud, STOPWORDS

# Data Manipulation
import os
import csv
import pandas as pd
import io
import numpy as np
import itertools
import statistics
import time
import datetime

# Ignore Warning Error
import warnings
warnings.filterwarnings("ignore")

# Model IndoBERT
import random
import transformers
import torch
import torch.nn.functional as F
from torch import optim
from tqdm import tqdm
from transformers import BertForSequenceClassification, BertConfig, BertTokenizer, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import Dataset, DataLoader,TensorDataset, random_split, RandomSampler, SequentialSampler
from pylab import rcParams

# Splitting
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# Evaluation
from sklearn.metrics import classification_report, confusion_matrix
from collections import defaultdict
from textwrap import wrap

# Vizualization
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc

# Pengaturan visualisasi
# %matplotlib inline
# %config InlineBackend.figure_format='retina'
sns.set(style='darkgrid', palette='bright', font_scale=1.5)

# Definisi palet warna khusus
MY_CUSTOM_PALETTE = ["#2ECC71", "#3498DB", "#E74C3C", "#9B59B6", "#F1C40F", "#E67E22"]
sns.set_palette(sns.color_palette(MY_CUSTOM_PALETTE))
rcParams['figure.figsize'] = 8, 5

#check GPU availability
if torch.cuda.is_available():
    device = torch.device("cuda")
    num_gpus = torch.cuda.device_count()
    gpu_name = torch.cuda.get_device_name(0)
    print(f'There are {num_gpus} GPU(s) available.')
    print(f'We will use the GPU: {gpu_name}')
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

"""#Load DATASET

"""

#read dataset
data = pd.read_csv('/content/dataset(final).csv')
data

"""##WORDCLOUD"""

from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from collections import Counter

# Gabungkan teks dari kolom 'full_text'
df = ' '.join(data['full_text'].tolist())

# Tentukan stopwords
stopwords = set(STOPWORDS)
stopwords.update(['https', 'co', 'RT', '...', 'amp'])

# Hitung frekuensi kata
word_counts = Counter(df.split())

# Buat WordCloud
wc = WordCloud(stopwords=stopwords, background_color="black", max_words=500, width=800, height=400)
wc.generate_from_frequencies(word_counts)

# Tampilkan WordCloud
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

import pandas as pd
import seaborn as sns
from collections import Counter

# Gabungkan teks dari kolom 'full_text'
text = " ".join(data["full_text"])

# Tokenisasi teks dan hitung frekuensi kata
tokens = text.split()
word_counts = Counter(tokens)

# Ambil 10 kata yang paling sering muncul
top_words = word_counts.most_common(10)
df_top_words = pd.DataFrame(top_words, columns=['word', 'count'])

# Visualisasi dengan seaborn
plt.figure(figsize=(10, 6))
sns.barplot(x='word', y='count', data=df_top_words, palette="Paired")
plt.xlabel("Kata")
plt.ylabel("Frekuensi")
plt.title("Kata-Kata yang Sering Muncul")
plt.xticks(rotation=45)

# Tambahkan label frekuensi di atas batang
for index, row in df_top_words.iterrows():
    plt.text(index, row['count'] + 1, row['count'], color='black', ha="center")

plt.show()

"""#  Preprocessing Text

##Case Folding/Lowercase
"""

#lowercase
data['Case Folding'] = data['full_text'].str.lower()
data.head(10)

"""##CLEANING"""

# Remove special text
def remove_text_special(text):
    if isinstance(text, str):
        text = re.sub(r'[^\x00-\x7f]',r' ', text)   # Remove non-ascii characters from the string
        text = re.sub(r'\.{2,}', ' ', text)   # Replace 2+ dots with space
        text = re.sub('@[^\s]+',' ',text)   # Remove @username
        text = re.sub(r'^RT[\s]+', ' ', text)  # Remove old style retweet text "RT"
        text = text.replace("\\n", " ")  # Remove newline
        text = re.sub(r'#', '', text)   # Remove hashtags
        text = re.sub(r"\b[a-zA-Z]\b", " ", text)  # Remove single character
        text = re.sub('[0-9]+', ' ', text)   # Remove number
        text = re.sub(r"http\S+", " ", text)   # Remove url
        text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
        text = text.strip(' "\' ')   # Strip space, " and ' from tweet
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'\s+$', '', text)  # Remove trailing space
        return re.sub(r'(.)\1{2,}', r'\1', text)  # Remove repeated characters
        return text.replace("http://", " ").replace("https://", " ")   # Remove url uncomplete
    else:
        return text

# Remove emoticon
def remove_emoji(text):
    if isinstance(text, str):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # chinese char
                                   u"\U00002702-\U000027B0"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\U00010000-\U0010ffff"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u200d"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\ufe0f"  # dingbats
                                   u"\u3030"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    else:
        return text

# Mengganti huruf yang berulang lebih dari dua kali dengan dua kali saja
def remove_repeated_characters(text):
    text = re.sub(r'(.)\1+', r'\1\1', text)
    return text

data['cleaning'] = data['Case Folding'].apply(remove_text_special)
data['cleaning'] = data['cleaning'].apply(remove_emoji)
data['cleaning'] = data['cleaning'].apply(remove_repeated_characters)
data.head(10)

"""##Tokenizing"""

# Tokenizing
def word_tokenize_wrapper(text):
    if isinstance(text, str):
        return word_tokenize(text)
    else:
        return text

data['Tokenize'] = data['cleaning'].apply(word_tokenize_wrapper)

data.head(10)

"""##NEGATION HANDLING"""

def negation_handling(content):
    if isinstance(content, float):
        return content
    else:
        negation_content = []
        negation_words = ['tiada','tidak pernah' ,'tidak mungkin','tidak', 'jangan', 'tanpa', 'nggak', 'ga', 'kurang', 'tak']

        for i in range(len(content)):
            word = content[i]
            if i > 0 and content[i-1] in negation_words:
                word = "%s_%s" % (content[i-1], word)

            negation_content.append(word)

        return negation_content

data['Negation_Handling'] = data['normal'].apply(negation_handling)


data

"""##Mengembalikan ke bentuk asli"""

# Mengembalikan data ke bentuk asli
def join_text_list(text):
    return ' '.join(text) if isinstance(text, list) else text if isinstance(text, str) else ''

data['text_clean'] = data['Stemming'].map(lambda x: join_text_list(x))
print(data['text_clean'].head(10))

"""#WORDCLOUD AFTER PREPROCESSING"""

from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from collections import Counter

# Gabungkan teks dari kolom 'full_text'
df = ' '.join(data['text_clean'].tolist())

# Tentukan stopwords
stopwords = set(STOPWORDS)
stopwords.update(['https', 'co', 'RT', '...', 'amp'])

# Hitung frekuensi kata
word_counts = Counter(df.split())

# Buat WordCloud
wc = WordCloud(stopwords=stopwords, background_color="black", max_words=500, width=800, height=400)
wc.generate_from_frequencies(word_counts)

# Tampilkan WordCloud
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

import pandas as pd
import seaborn as sns
from collections import Counter

# Gabungkan teks dari kolom 'full_text'
text = " ".join(data["text_clean"])

# Tokenisasi teks dan hitung frekuensi kata
tokens = text.split()
word_counts = Counter(tokens)

# Ambil 10 kata yang paling sering muncul
top_words = word_counts.most_common(10)
df_top_words = pd.DataFrame(top_words, columns=['word', 'count'])

# Visualisasi dengan seaborn
plt.figure(figsize=(10, 6))
sns.barplot(x='word', y='count', data=df_top_words, palette="Paired")
plt.xlabel("Kata")
plt.ylabel("Frekuensi")
plt.title("Kata-Kata yang Sering Muncul")
plt.xticks(rotation=45)

# Tambahkan label frekuensi di atas batang
for index, row in df_top_words.iterrows():
    plt.text(index, row['count'] + 1, row['count'], color='black', ha="center")

plt.show()

"""#Translate ID to Eng"""

import googletrans
from googletrans import Translator

# untuk translate text dari bahasa indonesia ke bahasa inggris

df = pd.DataFrame(data.text_clean)
translator = Translator()
translations = {}
for column in df.columns:
  #unique elements dari kolom
  unique_elements = df[column].unique()
  for element in unique_elements:
    #memasukkan terjemahan ke kamus
    translations[element] = translator.translate(element).text

#memasukkkan hasil translate ke kolom baru
data['translated_text'] = df.replace(translations)

data.head()

"""#Menyimpan preprocessing"""

#  Menyimpan Hasil Preprocessing
data.to_csv('Hasil-Preprocessing-1.csv', index=False)

"""#LABELING MENGGUNAKAN TEXTBLOP"""

#read dataset
data = pd.read_csv('/content/Hasil-Preprocessing-1.csv', delimiter=',')
data

# Checking if the dataset has a value of Null/NaN
is_NaN = data.isnull()
row_has_NaN = is_NaN.any(axis=1)
rows_with_NaN = data[row_has_NaN]
rows_with_NaN

# Remove data that have NAN value in column text_clean
data.dropna(subset=['text_clean'], inplace = True)

# mereset indeks ketika data dengan nilai NAN dihapus agar penomoran indeks sesuai
data = data.reset_index(drop = True)
data

#import textblob
import textblob
from textblob import TextBlob

def subjektivitas(tr_text):
  return TextBlob(tr_text).sentiment.subjectivity

def polaritas(tr_text):
  return TextBlob(tr_text).sentiment.polarity

def hasilSentimen(nilai):
  if nilai < 0:
    return 'negatif'
  elif nilai == 0:
    return 'netral'
  else:
    return 'positif'

# Konversi NaN ke string kosong dan semua nilai ke string
data['translated_text'] = data['translated_text'].fillna('').astype(str)

data['subjektivitas'] = data['translated_text'].apply(subjektivitas)
data['polaritas'] = data['translated_text'].apply(polaritas)
data['sentimen'] = data['polaritas'].apply(hasilSentimen)

data.head()

#menghitung jumlah tiap sentimen
data['sentimen'].value_counts()

diagram = data['sentimen'].value_counts().rename_axis('nilai_sentimen').reset_index(name='jumlah')
label = diagram.nilai_sentimen
nilai = diagram.jumlah

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis = ('equal')


ax.pie(nilai, labels = label, autopct='%1.2f%%' )
ax.set_title("Presentase Labeling Textblob")

"""##FINISH LABELING TEXTBLOP

"""

data.to_csv('labeling_data_textblob.csv', encoding='utf8', index=False)

#  Menyimpan Hasil Preprocessing
data.to_csv('Preprocessing_dan_Labeling_Textblob.csv', index=False)

"""#  Convert String To Integer Based On Column "sentimen"
"""

# Convert String To Integer Based On Column "sentimen"
def string_to_integer(sentimen):
    if sentimen == 'negatif':
      return 0
    elif sentimen == 'positif':
      return 1
    else:
      return 2

data['sentiment'] = data.sentimen.apply(string_to_integer)
data

"""# Menyimpan Dataset setelah Preprocessing"""

# Menyimpan dataset
data.to_csv('dataset-preprocessing-Final.csv', index=False)

"""# Exploratory Data Analysis"""

# Read result of final dataset
data = pd.read_csv("/content/dataset-preprocessing-Final.csv")
data

# Convert String To Integer Based On Column "sentimen"
def string_to_integer(sentimen):
    if sentimen == 'negatif':
      return 0
    elif sentimen == 'positif':
      return 1
    else:
      return 2

data['sentiment'] = data.sentimen.apply(string_to_integer)

sentiment_count = data['sentimen'].value_counts()

# Set style plot seaborn
sns.set_style('whitegrid')

# Membuat figure dan axes
fig, ax = plt.subplots(figsize=(6, 4))

# Membuat barplot
sns.barplot(x=sentiment_count.index, y=sentiment_count.values, palette='pastel', ax=ax)

# Menambahkan judul dan label sumbu
plt.title('Textblob\n\n', fontsize=14, pad=20)
plt.xlabel('Sentiment', fontsize=12)
# plt.ylabel('Jumlah', fontsize=12)

# Menghitung total sentimen
total = len(data['sentiment'])

# Menambahkan anotasi pada setiap bar
for i, count in enumerate(sentiment_count.values):
    percentage = f'{100 * count / total:.2f}%'
    ax.text(i, count + 0.10, f'{count}\n({percentage})', ha='center', va='bottom')

# Menampilkan plot
plt.show()

# menyisakan kolom yang diperlukan
data = data[['text_clean', 'sentiment']]
data

"""# Handling Missing Value"""

# Checking if the dataset has a value of Null/NaN
is_NaN = data.isnull()
row_has_NaN = is_NaN.any(axis=1)
rows_with_NaN = data[row_has_NaN]
rows_with_NaN

# Remove data that have NAN value in column text_clean
data.dropna(subset=['text_clean'], inplace = True)

# mereset indeks ketika data dengan nilai NAN dihapus agar penomoran indeks sesuai
data = data.reset_index(drop = True)
data

def count_words(text):
    return len(text.split())

# Menghitung jumlah kata dari setiap kalimat
word_counts = data['text_clean'].apply(count_words)

# Mendapatkan kalimat terpanjang dan jumlah katanya
longest_sentence = data['text_clean'].iloc[word_counts.idxmax()]
longest_word_count = word_counts.max()

# Menampilkan kalimat terpanjang dan jumlah katanya

print("Jumlah Kata Terbanyak:", longest_word_count)

"""# Prepare For BERT Sentiment Analysis

##Tokenize Dataset
"""

# Dict mapping
label_to_num = {'negatif': 0, 'positif': 1, 'netral':2}
num_to_label = {0: 'negatif', 1: 'positif', 2: 'netral'}

print('Loading BERT tokenizer...')
# Load BertTokenizer
tokenizer = BertTokenizer.from_pretrained('indobenchmark/indobert-base-p1', do_lower_case=True)

"""## Membagi Dataset menjadi Training,Validation,Testing"""

from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Asumsikan 'data' adalah DataFrame Anda yang sudah ada

# Langkah 1: Pengacakan data (jika belum dilakukan)
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

# Langkah 2: Stratified Sampling untuk membagi dataset
X = data['text_clean']
y = data['sentiment']

# Pertama, pisahkan 10% untuk test set
X_trainval, X_test, y_trainval, y_test = train_test_split(
    X, y, test_size=0.1, stratify=y, random_state=42
)

# Kemudian, dari sisa 90%, ambil 8/9 (sekitar 88.89%) untuk train set
# Ini akan menghasilkan 80% dari total data untuk train set
X_train, X_val, y_train, y_val = train_test_split(
    X_trainval, y_trainval, test_size=1/9, stratify=y_trainval, random_state=42
)

# Membuat DataFrame untuk setiap set data
train_data = pd.DataFrame({'text_clean': X_train, 'sentiment': y_train})
val_data = pd.DataFrame({'text_clean': X_val, 'sentiment': y_val})
test_data = pd.DataFrame({'text_clean': X_test, 'sentiment': y_test})

# Menampilkan jumlah dan persentase data
total_data = len(data)
print(f"Jumlah data train: {len(train_data)} ({len(train_data)/total_data:.2%})")
print(f"Jumlah data val: {len(val_data)} ({len(val_data)/total_data:.2%})")
print(f"Jumlah data test: {len(test_data)} ({len(test_data)/total_data:.2%})")

# Ekstraksi sentences dan labels
train_sentences = train_data['text_clean'].values
train_labels = train_data['sentiment'].values

val_sentences = val_data['text_clean'].values
val_labels = val_data['sentiment'].values

test_sentences = test_data['text_clean'].values
test_labels = test_data['sentiment'].values

# Verifikasi distribusi sentimen
print("\nDistribusi Sentimen:")
print("Train:", train_data['sentiment'].value_counts(normalize=True))
print("Validation:", val_data['sentiment'].value_counts(normalize=True))
print("Test:", test_data['sentiment'].value_counts(normalize=True))

# Menampilkan jumlah dan persentase data
total_data = len(data)
print(f"Jumlah data train: {len(train_data)} ({len(train_data)/total_data:.1%})")
print(f"Jumlah data val: {len(val_data)} ({len(val_data)/total_data:.1%})")
print(f"Jumlah data test: {len(test_data)} ({len(test_data)/total_data:.1%})")

# Verifikasi distribusi sentimen
print("\nDistribusi Sentimen:")
print("Train:\n", train_data['sentiment'].value_counts().to_frame(name='Jumlah').assign(
    Persentase=lambda x: (x['Jumlah'] / len(train_data) * 100).round(2)))
print("Validation:\n", val_data['sentiment'].value_counts().to_frame(name='Jumlah').assign(
    Persentase=lambda x: (x['Jumlah'] / len(val_data) * 100).round(2)))
print("Test:\n", test_data['sentiment'].value_counts().to_frame(name='Jumlah').assign(
    Persentase=lambda x: (x['Jumlah'] / len(test_data) * 100).round(2)))

#TRAIN DATA model BERT

# Menguraikan semua kalimat dan memetakan token-token tersebut ke dalam IDs.
input_ids_train = []
attention_masks_train = []

# kalimat dalam data pelatihan
for sent in train_sentences:
    if pd.notnull(sent):  # cek apakah kalimat tidak bernilai null
        encoded_dict = tokenizer.encode_plus(
            sent,                        # Sentence to encode.
            add_special_tokens=True,     # menambah '[CLS]' dan '[SEP]'
            max_length=64,              # Pad & truncate all sentences.
            pad_to_max_length=True,
            truncation=True,
            return_attention_mask=True,  # membuat attention masks.
            return_tensors='pt'          # mengembalikan PyTorch tensors.
        )
        # Lanjutkan dengan pemrosesan selanjutnya setelah encoding
    else:
        print("Found 'nan' value in the dataset. Skipping this sentence.")

    input_ids_train.append(encoded_dict['input_ids'])
    attention_masks_train.append(encoded_dict['attention_mask'])

# menggabungkan menjadi satu tensor besar
input_ids_train = torch.cat(input_ids_train, dim=0)
attention_masks_train = torch.cat(attention_masks_train, dim=0)
labels_train = torch.tensor(train_labels)

# Print
print('Original: ', train_sentences[3])
print('Token IDs:', input_ids_train[3])

# Validation data  model BERT
input_ids_val = []
attention_masks_val = []

# kalimat dalam data val
for sent in val_sentences:
    if pd.notnull(sent):  # cek apakah kalimat tidak bernilai null
        encoded_dict = tokenizer.encode_plus(
            sent,                        # Sentence to encode.
            add_special_tokens=True,     # menambah '[CLS]' dan '[SEP]'
            max_length=64,              # Pad & truncate all sentences.
            pad_to_max_length=True,
            return_attention_mask=True,  # membuat attention masks.
            return_tensors='pt',         # mengambalikan PyTorch tensors.
            truncation=True
        )
        # Lanjutkan dengan pemrosesan selanjutnya setelah encoding
    else:
        print("Found 'nan' value in the dataset. Skipping this sentence.")

    input_ids_val.append(encoded_dict['input_ids'])
    attention_masks_val.append(encoded_dict['attention_mask'])

# menggabungkan menjadi satu tensor besar
input_ids_val = torch.cat(input_ids_val, dim=0)
attention_masks_val = torch.cat(attention_masks_val, dim=0)
labels_val = torch.tensor(val_labels)


# Print
print('Original: ', val_sentences[2])
print('Token IDs:', input_ids_val[2])

# menggabungkan data input pelatihan dan validasi menjadi objek TensorDataset
train_dataset = TensorDataset(input_ids_train, attention_masks_train, labels_train)
val_dataset = TensorDataset(input_ids_val, attention_masks_val, labels_val)

# menentukan jumlah bacth size
batch_size = 32

# mengambil sampel data pelatihan secara acak/random
train_dataloader = DataLoader(train_dataset,
                              sampler = RandomSampler(train_dataset), # memilih secara acak data latih
                              num_workers=4,
                              batch_size = batch_size # menggunakan batch size yang sudah di inisiasi
                             )

# dataloader validation tidak secara acak
validation_dataloader = DataLoader(val_dataset,
                                   sampler = SequentialSampler(val_dataset),
                                   num_workers=4,
                                   batch_size = batch_size
                                  )

"""## BertForSequenceClassification"""

from transformers import BertForSequenceClassification, BertConfig, BertTokenizer
import torch

# Memuat konfigurasi model BERT
config = BertConfig.from_pretrained('indobenchmark/indobert-base-p1')

# Mengubah parameter dropout
config.hidden_dropout_prob = 0.3  # Probabilitas dropout untuk hidden states
config.attention_probs_dropout_prob = 0.3  # Probabilitas dropout untuk attention

# Load pre-trained BERT model
model = BertForSequenceClassification.from_pretrained(
    'indobenchmark/indobert-base-p1', # Menggunakan model bert yang sudah dilatih dan memiliki 12 layer dengan vocab IndoBERT
    num_labels=3,                    # Jumlah label atau kelas yang akan diprediksi
    output_attentions=False,
    output_hidden_states=False,
    ignore_mismatched_sizes=True     # Menambahkan parameter ini
)
bert_model = model.bert

# jalankan model menggunakan GPU
# Memastikan model menggunakan GPU jika tersedia
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

if next(model.parameters()).is_cuda:
    print('Model menggunakan GPU.')
else:
    print('Model menggunakan CPU.')

# Jumlah layer baru dari 12 ke 6
num_layers_to_keep = 9

# Potong model menjadi jumlah layer yang diinginkan
bert_model.encoder.layer = bert_model.encoder.layer[:num_layers_to_keep]

# Update konfigurasi model
model.config.num_hidden_layers = num_layers_to_keep

# Mengambil semua parameter model dalam bentuk daftar tuple
params = list(model.named_parameters())

# Menampilkan jumlah total parameter yang dinamai dalam model BERT
print(f'Model BERT memiliki {len(params)} parameter yang berbeda.\n')


# Menampilkan jumlah lapisan encoder dalam model BERT
num_layers = model.config.num_hidden_layers
print(f'\nModel BERT sekarang memiliki {num_layers} lapisan encoder.')

"""## Optimizer & Learning Rate Scheduler

"""

#  Optimizer
optimizer = AdamW(model.parameters(),lr = 1e-5, eps = 1e-5,weight_decay=0.001)
# jumlah Epochs
epochs = 10

print('Jumlah batch :', len(train_dataloader))
total_steps = len(train_dataloader) * epochs
# Maximum norm for gradient clipping
max_grad_norm = 1.0

# membuat learning rate scheduler.
scheduler = get_linear_schedule_with_warmup(optimizer,
                                            num_warmup_steps = 0, # default dari run_glue.py
                                            num_training_steps = total_steps)

# menghitung akurasi dari prediksi

#menghitung akurasi dari prediksi model
def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

#mengonversi waktu dalam detik ke format string
def format_time(elapsed):
    '''
    Takes a time in seconds and returns a string hh:mm:ss
    '''

    elapsed_rounded = int(round((elapsed)))

    # Format as hh:mm:ss
    return str(datetime.timedelta(seconds=elapsed_rounded))

"""#  Training and Validation Model BERT"""

import time
import numpy as np
import torch

# Lis variabel untuk train dan validation loss, validation accuracy, and timings.
training_stats = []

# waktu pelatihan
total_t0 = time.time()

# Implementing Early Stopping
best_val_loss = float('inf')  # Inisialisasi dengan nilai yang sangat besar
patience = 3  # Jumlah epoch yang harus ditunggu sebelum menghentikan training jika tidak ada perbaikan
trigger_times = 0  # Counter untuk mengecek jika tidak ada perbaikan

# untuk setiap epoch.
for epoch_i in range(0, epochs):

    # ========================================
    #               Training
    # ========================================
    print("")
    print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, epochs))
    print('Training...')

    # lama waktu training epoch
    t0 = time.time()

    # Reset total loss untuk setiap epoch.
    total_train_loss = 0
    total_train_correct = 0

    # simpan model ke model train
    model.train()

    # untuk setiap batch dalam training data
    for step, batch in enumerate(train_dataloader):
        # update progress setiap 20 batch
        if step % 20 == 0 and not step == 0:
            elapsed = format_time(time.time() - t0)
            # Report progress.
            print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

        b_input_ids = batch[0].to(device)   #input IDS
        b_input_mask = batch[1].to(device)  # attention masks
        b_labels = batch[2].to(device)      # labels

        # hapus any previously calculated gradients before performing a backward pass
        model.zero_grad()

        outputs = model(b_input_ids,              #tabahkan   torch.randn(32, 10)
                       token_type_ids=None,
                       attention_mask=b_input_mask,
                       labels=b_labels)

        loss = outputs[0]
        logits = outputs[1]

        # akumulasi training loss dari seluruh batch
        total_train_loss += loss.item()

        # Menghitung prediksi
        _, predicted_labels = torch.max(logits, 1)
        total_train_correct += (predicted_labels == b_labels).sum().item()

        # backward pass untuk menghitung the gradients.
        loss.backward()


        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)

        # Update parameters and take a step using the computed gradient.
        optimizer.step()

        # Update the learning rate.
        scheduler.step()

    # menghitung rata-rata loss over dari seluruh bacth.
    train_loss = total_train_loss / len(train_dataloader)

    # menghitung rata-rata training accuracy
    train_accuracy = total_train_correct / len(train_dataloader.dataset)

    # memastikan berapa lama waktu
    training_time = format_time(time.time() - t0)

    print("")
    print("  Average training loss: {0:.2f}".format(train_loss))
    print("  Training Accuracy: {0:.2f}".format(train_accuracy))
    print("  Training epoch took: {:}".format(training_time))

    # ========================================
    #               Validation
    # ========================================

    print("")
    print("Running Validation...")

    t0 = time.time()

    # mode evaluasi (batchnorm, dropout disable)
    model.eval()

    # Tracking variables
    total_eval_accuracy = 0
    total_eval_loss = 0

    # Evaluate data for one epoch
    for batch in validation_dataloader:

        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        with torch.no_grad():

            # Forward pass, calculate logit predictions.
            outputs = model(b_input_ids,
                            token_type_ids=None,
                            attention_mask=b_input_mask,
                            labels=b_labels)

            loss = outputs[0]
            logits = outputs[1]

        # akumulasi validation loss.
        total_eval_loss += loss.item()

        # Move logits and labels to CPU
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()

        # menghitung akurasi
        total_eval_accuracy += flat_accuracy(logits, label_ids)

    # final accuracy for this validation run.
    val_accuracy = total_eval_accuracy / len(validation_dataloader)

    # menghitung rata rata loss over dari semua batch
    val_loss = total_eval_loss / len(validation_dataloader)

    # memastikan berapa lama waktu
    validation_time = format_time(time.time() - t0)

    print("  Validation accuracy: {0:.2f}".format(val_accuracy))
    print("  Validation Loss: {0:.2f}".format(val_loss))
    print("  Validation took: {:}".format(validation_time))

    # statistik dari setiap epoch
    training_stats.append(
        {
            'Epoch': epoch_i + 1,
            'Training Loss': train_loss,
            'Validation Loss': val_loss,
            'Training Accuracy': train_accuracy,
            'Validation Accuracy': val_accuracy,
            'Training Time': training_time,
            'Validation Time': validation_time
        }
    )

    # Early Stopping condition
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        trigger_times = 0  # Reset counter jika ada perbaikan
        torch.save(model.state_dict(), 'best_model.pt')  # Simpan model terbaik
    else:
        trigger_times += 1
        if trigger_times >= patience:
            print('Early stopping triggered!')
            break

print("")
print("Training complete!")

print("Total training took {:} (h:mm:ss)".format(format_time(time.time()-total_t0)))

# Create a DataFrame from our training statistics.
df_stats = pd.DataFrame(data=training_stats)

# Use the 'epoch' as the row index.
df_stats = df_stats.set_index('Epoch')

# Display the table.
df_stats

# Grafik Training & Validation Loss
plt.figure(figsize=(6,4))
plt.plot(df_stats['Training Loss'], label='Training Loss')
plt.plot(df_stats['Validation Loss'], label='Validation Loss')
plt.title('Training & Validation Loss History')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()

# # Grafik Training & Validation akurasi
plt.figure(figsize=(6,4))
plt.plot(df_stats['Training Accuracy'], label='Training Accuracy')
plt.plot(df_stats['Validation Accuracy'], label='Validation Accuracy')
plt.title('Training & Validation Accuracy History')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.show()

"""#Evaluation Model Bert and Prediction New Data"""

# Tokenize untuk seluruh kalimat dan map token tersebut ke IDs
input_ids_test = []
attention_masks_test = []

#
for sent in test_sentences:
    encoded_dict = tokenizer.encode_plus(sent,                           # kalimat.
                                         add_special_tokens = True,      # tambah '[CLS]' dan '[SEP]'
                                         max_length = 64,               # Pad & truncate all sentences.
                                         pad_to_max_length = True,
                                         return_attention_mask = True,   # buat attention mask
                                         return_tensors = 'pt',          # Return pytorch tensors.
                                         truncation = True
                                        )


    input_ids_test.append(encoded_dict['input_ids'])


    attention_masks_test.append(encoded_dict['attention_mask'])

# Convert the lists into tensors.
input_ids_test = torch.cat(input_ids_test, dim=0)
attention_masks_test = torch.cat(attention_masks_test, dim=0)
labels_test = torch.tensor(test_labels)

# set batch size
batch_size = 32

# Buat Rataloader.
prediction_data = TensorDataset(input_ids_test, attention_masks_test, labels_test)
prediction_sampler = SequentialSampler(prediction_data)
prediction_dataloader = DataLoader(prediction_data, sampler=prediction_sampler, batch_size=batch_size)

# Prediksi test
print(f'Predicting labels for {len(input_ids_test):,} test sentences...')

model.eval()

# Tracking variables
predictions, true_labels = [], []

# Prediksi
for batch in prediction_dataloader:
    # Move tensors to the device (GPU or CPU)
    b_input_ids, b_input_mask, b_labels = (t.to(device) for t in batch)

    with torch.no_grad():
        # Forward pass, calculate logit predictions
        outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)

    logits = outputs[0]

    # Move logits and labels to CPU and convert to numpy
    logits = logits.detach().cpu().numpy()
    label_ids = b_labels.cpu().numpy()

    # Append predictions and true labels
    predictions.append(logits)
    true_labels.append(label_ids)

print('DONE.')

# menghitung jumlah sampel pengujian
flat_pred = []
flat_true = []
for i in range(len(predictions)):
    for j in range(len(predictions[i])):
        flat_pred.append(predictions[i][j])
        flat_true.append(true_labels[i][j])

print(f"Jumlah sampel pengujian: {len(flat_pred)}")

# Classification report
class_names = ['Negatif', 'Positif', 'Netral']
print(classification_report(flat_true, np.argmax(flat_pred, axis=1), digits=4, target_names=class_names))

# confusion matrix
confusion_matrix_df = pd.DataFrame(confusion_matrix(flat_true, np.argmax(flat_pred, axis=1))).rename(columns=num_to_label, index=num_to_label)
sns.heatmap(confusion_matrix_df, annot=True, fmt='').set(title="confusion matrix", xlabel="Predicted Label", ylabel="True Label")
plt.show()

"""# **Saving Model**"""

# Save tokenizer
tokenizer.save_pretrained('SA-INDO-BERT-MODEL/')

# Save model Bert
model.save_pretrained('SA-INDO-BERT-MODEL/')

"""# Prediksi dengan Text Lain"""

text = """
Sampai saat ini kondisi politik dan pertumbuhan ekonomi Indonesia baik-baik saja
"""

# Encode text to subwords
subwords = torch.LongTensor([tokenizer.encode(text)])

# Create DataLoader for single batch processing
data_loader = torch.utils.data.DataLoader(subwords, batch_size=1)

for batch in data_loader:
    batch = batch.to(model.device)

    with torch.no_grad():
        logits = model(batch)[0]

    label = torch.argmax(logits, dim=-1).item()

# Print the result
print(f'Text: {text}\nLabel: {num_to_label[label]} ({F.softmax(logits, dim=-1).squeeze()[label] * 100:.3f}%)')

text = """
kecewa dengan rangkaian pemilu, tetapi saya tetap menghargai dan berdoa yang terbaik
"""

# Encode text to subwords
subwords = torch.LongTensor([tokenizer.encode(text)])

# Create DataLoader for single batch processing
data_loader = torch.utils.data.DataLoader(subwords, batch_size=1)

for batch in data_loader:
    batch = batch.to(model.device)

    with torch.no_grad():
        logits = model(batch)[0]

    label = torch.argmax(logits, dim=-1).item()

# Print the result
print(f'Text: {text}\nLabel: {num_to_label[label]} ({F.softmax(logits, dim=-1).squeeze()[label] * 100:.3f}%)')