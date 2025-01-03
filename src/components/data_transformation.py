import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd
# column transformer used to create pipeline
from sklearn.compose import _column_transformer, ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from src.exception import CustomException
from src.logger import logging
import os
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts',"preprocessor.pkl")

class DataTransformation():
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_data_transformer_object(self):
        try:
            numerical_columns=["writing score","reading score"]
            categorical_columns=[
                "gender",
                "race/ethnicity",
                "parental level of education",
                "lunch",
                "test preparation course"
            ]

            num_pipeline= Pipeline(
                # handle missing values and do standard scaling
                steps=[
                    ("imputer",SimpleImputer(strategy="median")),  # handle missing values
                    ("scaler",StandardScaler()) # handle standard scaling
                ]
            )
            cat_pipeline=Pipeline(
                steps=[("imputer",SimpleImputer(strategy="most_frequent")),  # replace missing values with the help of mode
                        ("one hot_encoder",OneHotEncoder()),
                        ("scaler",StandardScaler(with_mean=False))
                    ]
                )

            logging.info("Numerical columns standard scaling completed")

            logging.info("Categorical columns encoding completed")

            # combine numerical pipeline with categorical pipeline
            preprocessor=ColumnTransformer(
                [
                    ("num_pipeline",num_pipeline,numerical_columns),
                    ("cat_pipeline", cat_pipeline, categorical_columns)

                ]
            )

            return preprocessor
        except Exception as e:
            raise CustomException(e,sys)

    def initiate_data_transformation(self,train_path,test_path):
        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)
            print(train_df.head())

            print(train_df.columns)

            logging.info("read train and test completed")

            logging.info("obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()

            target_column_name="math score"
            numerical_columns=["writing score","reading score"]


            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]
            print(input_feature_train_df.columns)
            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            # The fit(data) method is used to compute the mean and std dev for a given feature to be used further for scaling.
            # The transform(data) method is used to perform scaling using mean and std dev calculated using the .fit() method.
            # The fit_transform() method does both fits and transform.
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
            train_arr=np.c_[
                input_feature_train_arr,np.array(target_feature_train_df)
            ]
            test_arr=np.c_[input_feature_test_arr,np.array(target_feature_test_df)]
            logging.info(f"Saving preprocessing object")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            raise CustomException(e,sys)
