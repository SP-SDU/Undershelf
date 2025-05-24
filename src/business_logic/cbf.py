import numpy as np
import pandas as pd

from business_logic.aspects import (
    error_handler,
    input_validator,
    performance_monitor,
    simple_cache,
    validate_positive_int,
)
from data_access.models import Book, Review


class BookRecommender:
    @staticmethod
    @error_handler([])
    @input_validator(validate_positive_int)
    @performance_monitor
    @simple_cache(600)
    def get_cbf_list(userid, n_recommendations=10):
        # Build a DataFrame merging user reviews with their books
        user_reviews = Review.objects.filter(user_id=userid).select_related("book")
        if not user_reviews:
            return []

        records = []
        for rev in user_reviews:
            b = rev.book
            records.append(
                {
                    "Id": b.id,
                    "Title": b.title,
                    "User_id": rev.user_id,
                    "review/score": rev.review_score or 0.0,
                    "description": b.description,
                    "authors": b.authors,
                    "image": b.image,
                    "publisher": b.publisher,
                    "publishedDate": b.publishedDate,
                    "categories": b.categories or "",
                    "ratingsCount": b.ratingsCount,
                }
            )

        merged_df = pd.DataFrame(records).set_index("User_id")

        # deprecated. Used to pick a random user id from the dataframe
        # rng = np.random.default_rng(None)
        # indexRandom = rng.integers(low=0, high=len(merged_df.index), size=1)
        # indexRandom = indexRandom[0]
        # userid = merged_df.iloc[indexRandom]
        # userid = userid.name

        # Originally this was the user id string or the rng result
        # userid = Review.user_id

        user_categories = merged_df.loc[[userid], ["categories"]]
        categories_len = len(user_categories["categories"].unique())

        if categories_len == 1:
            # Recommendation wont be effective for one genre
            # rng = np.random.default_rng(None)
            # index_random = rng.integers(low=0, high=len(merged_df.index), size=1)
            # index_random = index_random[0]
            # userid = merged_df.iloc[index_random]
            # userid = userid.name
            # user_categories = merged_df.loc[[userid],["categories"]]
            # categories_len = len(user_categories["categories"].unique())
            return []

        # inputUsrVctr is a list with the review score of the user
        input_user_vector = merged_df.loc[[userid], ["review/score"]].to_numpy()
        user_genre_matrix = merged_df.loc[[userid], ["categories"]]

        # Encode a feature into binary categorization

        def encode_and_bind(original_dataframe, feature_to_encode):
            dummies = pd.get_dummies(original_dataframe[[feature_to_encode]])
            res = pd.concat([original_dataframe, dummies], axis=1)
            res = res.drop([feature_to_encode], axis=1)
            return res

        # encode genres of the user
        user_genre_matrix = encode_and_bind(user_genre_matrix, "categories")
        user_genre_matrix = user_genre_matrix.to_numpy(dtype=int)

        # weight the encode and normalize it into a weight vector
        weighted_genre_matrix = np.multiply(input_user_vector, user_genre_matrix)
        interest_genre_vector = weighted_genre_matrix.sum(axis=0)
        interest_genre_vector = interest_genre_vector / np.linalg.norm(
            interest_genre_vector
        )

        # change pandas base index tobe the title
        titleindex_df = merged_df.set_index("Title")

        # Candidate selection
        booklist_match = titleindex_df["categories"].isin(
            user_categories.loc[:, "categories"]
        )
        booklist_match = titleindex_df[booklist_match]
        candidate_matrix = booklist_match

        candidate_matrix = encode_and_bind(candidate_matrix, "categories")
        candidate_matrix = candidate_matrix.drop(
            [
                "Id",
                "review/score",
                "description",
                "authors",
                "image",
                "publisher",
                "publishedDate",
                "ratingsCount",
            ],
            axis=1,
        )

        # Result calculation
        candidate_matrix = candidate_matrix.to_numpy(dtype=int)
        weighted_candidate_genre_matrix = np.multiply(
            interest_genre_vector, candidate_matrix
        )
        weighted_vrg = weighted_candidate_genre_matrix.sum(axis=1)

        booklist_match.insert(0, "result", weighted_vrg)
        booklist_match = booklist_match[~booklist_match.index.duplicated(keep="first")]
        booklist_match = booklist_match.sort_values(
            by=["result"], ascending=False, kind="mergesort"
        )
        # keep top‑n scores
        result = booklist_match.result[:n_recommendations]
        # convert book IDs → Book instances (preserving order)
        book_ids = booklist_match.loc[result.index, "Id"].tolist()
        books = list(Book.objects.filter(id__in=book_ids))
        book_map = {b.id: b for b in books}
        return [book_map[book_id] for book_id in book_ids if book_id in book_map]
