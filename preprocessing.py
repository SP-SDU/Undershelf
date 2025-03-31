import pandas as pd
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')  # In case stopwords are also missing
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


# Load dataset
df = pd.read_csv("merged_dataframe.csv")

# Display first 5 rows
print(df.head())
# Remove Duplicates:
df.drop_duplicates(subset=['Id'], inplace=True)
# Handle Missing Values:
df.fillna({'authors': 'Unknown', 'categories': 'Unknown', 'ratingsCount': df['ratingsCount'].mean()}, inplace=True)

# Standardize Text Formats:
df['Title'] = df['Title'].str.lower().str.strip()
df['authors'] = df['authors'].str.lower().str.strip()

# Tokenization & Stopword Removal
nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokens = word_tokenize(text.lower())  # Convert to lowercase and tokenize
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return " ".join(tokens)

df['processed_Title'] = df['Title'].apply(preprocess_text)
df['processed_description'] = df['description'].apply(lambda x: preprocess_text(str(x)))

#TF-IDF Vectorization
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['processed_description'])

print(tfidf_matrix.shape)  # (num_books, num_features)

#Save Processed Data for Faster Access
df.to_csv("processed_books.csv", index=False)
