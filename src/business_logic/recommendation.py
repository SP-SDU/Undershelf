import numpy as np 
import pandas as pd

# Content based recommender proof of concept 2

merged_fp = 'merged_dataframe.csv' 
merged_df= pd.read_csv(merged_fp, index_col="User_id")
merged_df=merged_df.dropna()

rng = np.random.default_rng(None)
indexRandom = rng.integers(low=0, high=len(merged_df.index), size=1)
indexRandom = indexRandom[0]
userid = merged_df.iloc[indexRandom]
userid = userid.name

userCtg = merged_df.loc[[userid],["categories"]]
ctgLen = len(userCtg["categories"].unique())

if  ctgLen ==  1:
    rng = np.random.default_rng(None)
    indexRandom = rng.integers(low=0, high=len(merged_df.index), size=1)
    indexRandom = indexRandom[0]
    userid = merged_df.iloc[indexRandom]
    userid = userid.name
    userCtg = merged_df.loc[[userid],["categories"]]
    ctgLen = len(userCtg["categories"].unique())

print("User: ",userid)

inputUsrVctr = merged_df.loc[[userid],["review/score"]].to_numpy() 
userGnrMtrx = merged_df.loc[[userid],["categories"]]

def encode_and_bind(original_dataframe, feature_to_encode):
    dummies = pd.get_dummies(original_dataframe[[feature_to_encode]])
    res = pd.concat([original_dataframe, dummies], axis=1)
    res = res.drop([feature_to_encode], axis=1)
    return(res) 

userGnrMtrx = encode_and_bind(userGnrMtrx, 'categories')
test1 = userGnrMtrx
userGnrMtrx = userGnrMtrx.to_numpy(dtype=int)

weightedGnrMtrx = np.multiply(inputUsrVctr,userGnrMtrx)  
interestGnrVctr = weightedGnrMtrx.sum(axis=0)  
interestGnrVctr = interestGnrVctr/np.linalg.norm(interestGnrVctr)

titleindex_df = merged_df.set_index('Title')

booklistMatch = titleindex_df['categories'].isin(userCtg.loc[:,'categories'])
booklistMatch = titleindex_df[booklistMatch]
candidateMtrx = booklistMatch

candidateMtrx = encode_and_bind(candidateMtrx, "categories")
candidateMtrx = candidateMtrx.drop(['Id', 'review/score', 'description', 'authors', 'image', 'publisher', 'publishedDate', 'ratingsCount'], axis=1)

candidatetest = candidateMtrx

candidateMtrx = candidateMtrx.to_numpy(dtype=int)
weightedCnddtGnrMtrx = np.multiply(interestGnrVctr,candidateMtrx)           
weightedAvrg = weightedCnddtGnrMtrx.sum(axis=1) 


dimensions = candidateMtrx.shape
rows, columns = dimensions


print("User Categories: ", userCtg["categories"].unique(), sep="\n")

print("Candidate Rows:", rows)
print("Candidate Columns:", columns)

dimensions = userGnrMtrx.shape
rows, columns = dimensions

print("UserGnr Rows: ", rows)
print("UserGnr Columns: ", columns)
print("RESULT :",weightedAvrg, sep="\n")
print("Candidate Genre log: ",list(candidatetest), sep="\n")

# TODO Test proof. Identify error when max genre = 1




























