import numpy as np 
import pandas as pd

# Content based recommender proof of concept 2

merged_fp = 'Task2/merged_dataframe.csv' #TODO change file path
merged_df= pd.read_csv(merged_fp, index_col="User_id")
merged_df=merged_df.dropna()

inputUsrVctr = merged_df.loc[["A3UH4UZ4RSVO82"],["review/score"]].to_numpy() 
userGnrMtrx = merged_df.loc[["A3UH4UZ4RSVO82"],["categories"]]

def encode_and_bind(original_dataframe, feature_to_encode):
    dummies = pd.get_dummies(original_dataframe[[feature_to_encode]])
    res = pd.concat([original_dataframe, dummies], axis=1)
    res = res.drop([feature_to_encode], axis=1)
    return(res) 

userGnrMtrx = encode_and_bind(userGnrMtrx, 'categories')
userGnrMtrx = userGnrMtrx.to_numpy(dtype=int)

weightedGnrMtrx = np.multiply(inputUsrVctr,userGnrMtrx)  
interestGnrVctr = weightedGnrMtrx.sum(axis=0)  
interestGnrVctr = interestGnrVctr/np.linalg.norm(interestGnrVctr)

print("User Genre Matrix",userGnrMtrx,"Weighted Genre Matrix",weightedGnrMtrx,"Interest Genre Vector",interestGnrVctr, sep="\n")




#
#candidateMvMtrx = np.array([[1,0,0],[0,1,0],[0,0,1],[1,0,1],[0,1,1],[1,1,0],[1,1,1]])   # height = number of candidate books, lenght = max user genre
#
## select 7 books where not in reviews from user but same genre and ratingcount 
#
#
#weightedCnddtGnrMtrx = np.multiply(interestGnrVctr,candidateMvMtrx)                     # multiplication of the interest vector and the candidate matrix
#weightedAvrg = weightedCnddtGnrMtrx.sum(axis=1)                                         # aggregation of the candidate result 
#sortedAvrg = np.sort( weightedAvrg, kind='mergesort')[::-1]                             # sort the average in a inverse order
#
#
#
#
## Issues
## The genres and books needs to be indentified at any moment somehow, in this prove of concept is easy until the sort execution
## This method is not optimized for SIMD
## This method doesnt have multiple user in mind


























