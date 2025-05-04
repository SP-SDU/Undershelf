import numpy as np 
import pandas as pd


from data_access.models import Book
from data_access.models import Review





class BookRecommender:
        @staticmethod

        # Encode a feature into binary categorization
        def encode_and_bind(original_dataframe, feature_to_encode):
            dummies = pd.get_dummies(original_dataframe[[feature_to_encode]])
            res = pd.concat([original_dataframe, dummies], axis=1)
            res = res.drop([feature_to_encode], axis=1)
            return(res) 


        def get_cbf_list(userid, n_recommendations=10):
            # Read dataframe to use pandas
            merged_fp = 'processed_books.csv' 
            # DO put Django models reference instead of pandas dataframe
            merged_df= pd.read_csv(merged_fp, index_col="User_id")

            # userid = userid.name
            userid = Review.user_id

            userCtg = merged_df.loc[[Review.user_id],["categories"]]

            # inputUsrVctr is a list with the review score of the user
            inputUsrVctr = merged_df.loc[[userid],["review/score"]].to_numpy() 
            userGnrMtrx = merged_df.loc[[userid],["categories"]]

            # encode genres of the user 
            userGnrMtrx = encode_and_bind(userGnrMtrx, 'categories')
            userGnrMtrx = userGnrMtrx.to_numpy(dtype=int)

            # weight the encode and normalize it into a weight vector
            weightedGnrMtrx = np.multiply(inputUsrVctr,userGnrMtrx)  
            interestGnrVctr = weightedGnrMtrx.sum(axis=0)  
            interestGnrVctr = interestGnrVctr/np.linalg.norm(interestGnrVctr)

            # change pandas base index tobe the title 
            titleindex_df = merged_df.set_index('Title')

            # Candidate selection
            booklistMatch = titleindex_df['categories'].isin(userCtg.loc[:,'categories'])
            booklistMatch = titleindex_df[booklistMatch]
            candidateMtrx = booklistMatch

            candidateMtrx = encode_and_bind(candidateMtrx, "categories")
            candidateMtrx = candidateMtrx.drop(['Id', 'review/score', 'description', 'authors', 'image', 'publisher', 'publishedDate', 'processed_Title', 'processed_description',  'ratingsCount'], axis=1)

            # Result calculation
            candidateMtrx = candidateMtrx.to_numpy(dtype=int)
            weightedCnddtGnrMtrx = np.multiply(interestGnrVctr,candidateMtrx)           
            weightedAvrg = weightedCnddtGnrMtrx.sum(axis=1)

            booklistMatch.insert(0, "result", weightedAvrg)
            booklistMatch = booklistMatch[~booklistMatch.index.duplicated(keep='first')]
            booklistMatch = booklistMatch.sort_values(by= ['result'], ascending=False, kind="mergesort")
            result = booklistMatch.result[:n_recommendations]

            return result



             










            