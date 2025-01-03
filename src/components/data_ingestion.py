import os
import sys
from src.exception import CustomException
from src.logger import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainerConfig
from src.components.model_trainer import ModelTrainer
from src.components.data_transformation import DataTransformationConfig
# there are certain inputs required by the data ingestion component, like where we have to save the train/test data
#use a decorator called dataclass
@dataclass()
class DataIngestionConfig:
    # initially we assign paths as inputs
    train_data_path: str=os.path.join('artifacts',"train.csv")
    test_data_path: str = os.path.join('artifacts', "test.csv")
    raw_data_path: str = os.path.join('artifacts', "data.csv")

class DataIngestion:
    def __init__(self):
        # the three paths will be saved in this variable
        self.ingestion_config=DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("entered data ingestion component")
        try:
            df=pd.read_csv('notebook/data/StudentsPerformance.csv')
            logging.info('Read dataset as dataframe')

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path,index=False,header=True)

            logging.info('train test set initiated')
            # test_size is given as 0.2 which means 20% of the data goes into the test sets
            # random_state controls the random number generator used to shuffle the data before splitting it
            train_set,test_set=train_test_split(df,test_size=0.2,random_state=42)
            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)
            logging.info('ingestion of data is completed')

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
                )
        except Exception as e:
            raise CustomException(e,sys)

if __name__=="__main__":
    obj=DataIngestion()
    train_data, test_data=obj.initiate_data_ingestion()
    data_transformation=DataTransformation()
    train_arr, test_arr,_=data_transformation.initiate_data_transformation(train_data,test_data)
    print(type(train_arr))
    model_trainer=ModelTrainer()
    print(model_trainer.initiate_model_trainer(train_arr, test_arr))


