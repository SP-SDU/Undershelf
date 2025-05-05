import numpy as np 
import pandas as pd



class BookRecommender:
        @staticmethod
        def get_cbf_list(userid, n_recommendations=10):
            # Read dataframe to use pandas
            merged_fp = 'processed_books.csv' 
            # DO put Django models reference instead of pandas dataframe
            merged_df= pd.read_csv(merged_fp, index_col="User_id")

            # rng = np.random.default_rng(None)
            # indexRandom = rng.integers(low=0, high=len(merged_df.index), size=1)
            # indexRandom = indexRandom[0]
            # userid = merged_df.iloc[indexRandom]
            # userid = userid.name
            
            # Originally this was the user id sttring or the rng result
            #userid = Review.user_id 

            user_categories = merged_df.loc[[userid],["categories"]]
            categories_len = len(user_categories["categories"].unique())
            
            if  categories_len ==  1:
                print("Recommendation wont be effective for one genre")
                #rng = np.random.default_rng(None)
                #index_random = rng.integers(low=0, high=len(merged_df.index), size=1)
                #index_random = index_random[0]
                #userid = merged_df.iloc[index_random]
                #userid = userid.name
                #user_categories = merged_df.loc[[userid],["categories"]]
                #categories_len = len(user_categories["categories"].unique())
            else:
                # inputUsrVctr is a list with the review score of the user
                input_user_vector = merged_df.loc[[userid],["review/score"]].to_numpy() 
                user_genre_matrix = merged_df.loc[[userid],["categories"]]


                # Encode a feature into binary categorization

                def encode_and_bind(original_dataframe, feature_to_encode):
                    dummies = pd.get_dummies(original_dataframe[[feature_to_encode]])
                    res = pd.concat([original_dataframe, dummies], axis=1)
                    res = res.drop([feature_to_encode], axis=1)
                    return(res) 


                # encode genres of the user 
                user_genre_matrix = encode_and_bind(user_genre_matrix, 'categories')
                user_genre_matrix = user_genre_matrix.to_numpy(dtype=int)

                # weight the encode and normalize it into a weight vector
                weighted_genre_matrix = np.multiply(input_user_vector,user_genre_matrix)  
                interest_genre_vector = weighted_genre_matrix.sum(axis=0)  
                interest_genre_vector = interest_genre_vector/np.linalg.norm(interest_genre_vector)

                # change pandas base index tobe the title 
                titleindex_df = merged_df.set_index('Title')

                # Candidate selection
                booklist_match = titleindex_df['categories'].isin(user_categories.loc[:,'categories'])
                booklist_match = titleindex_df[booklist_match]
                candidate_matrix = booklist_match

                candidate_matrix = encode_and_bind(candidate_matrix, "categories")
                candidate_matrix = candidate_matrix.drop(['Id', 'review/score', 'description', 'authors', 'image', 'publisher', 'publishedDate', 'processed_Title', 'processed_description',  'ratingsCount'], axis=1)

                # Result calculation
                candidate_matrix = candidate_matrix.to_numpy(dtype=int)
                weighted_candidate_genre_matrix = np.multiply(interest_genre_vector,candidate_matrix)           
                weighted_vrg = weighted_candidate_genre_matrix.sum(axis=1)

                booklist_match.insert(0, "result", weighted_vrg)
                booklist_match = booklist_match[~booklist_match.index.duplicated(keep='first')]
                booklist_match = booklist_match.sort_values(by= ['result'], ascending=False, kind="mergesort")
                result = booklist_match.result[:n_recommendations]
                print(result)

        
        get_cbf_list("A2F6NONFUDB6UK")



             










            