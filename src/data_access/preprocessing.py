import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
df = pd.read_csv("merged_dataframe.csv")

# Display first 5 rows
print(df.head())

# Remove Duplicates
df.drop_duplicates(subset=['Id'], inplace=True)

# Handle Missing Values
df.fillna({'authors': 'Unknown', 'categories': 'Unknown', 'ratingsCount': df['ratingsCount'].mean(), 'description': ''}, inplace=True)

# Standardize Text Formats
df['Title'] = df['Title'].str.lower().str.strip()
df['authors'] = df['authors'].str.lower().str.strip()

# Tokenization & Stopword Removal
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokens = word_tokenize(text.lower())  # Convert to lowercase and tokenize
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return " ".join(tokens)

df['processed_Title'] = df['Title'].apply(preprocess_text)
df['processed_description'] = df['description'].apply(lambda x: preprocess_text(str(x)))

# Preserve Genre Information
df['processed_genres'] = df['categories'].apply(lambda x: preprocess_text(str(x)))

# Ensure no NaN values in processed_description
df['processed_description'] = df['processed_description'].fillna('')

# TF-IDF Vectorization
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['processed_description'])

print(tfidf_matrix.shape)  # Should match the number of books and features

# Save Processed Data for Faster Access
df.to_csv("processed_books.csv", index=False)
