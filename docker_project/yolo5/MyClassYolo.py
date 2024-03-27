from pymongo import MongoClient


class MyClassYolo:
    def __init__(self):
        print(f"obj yolo created")

    ## attributes

    ## methods
    def download_from_s3(self, bucket_name, img_name):
        print("downloading from s3")
        print("return original image path")
        return "original img path"

    def upload_to_s3(self, predicted_img_path):
        print("uploading to s3")

    def get_s3_bucket_name(self):
        print("fetching bucket name from os ENV")
        return "my-s3-bucket-name"

    def store_in_mongodb(self, prediction_sum,cluster_uri,database_name,collection_name,time):
        print("store the prediction summary in mongodb")
        # Create a MongoDB client
        client = MongoClient(cluster_uri)

        # Select the database and collection
        db = client[database_name]
        collection = db[collection_name]

        # Create a prediction summary
        prediction_id = "123"
        original_img_path = "/path/to/original/image.jpg"
        predicted_img_path = "/path/to/predicted/image.jpg"
        labels = ["label1", "label2"]
        timestamp = time.time()

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': original_img_path,
            'predicted_img_path': predicted_img_path,
            'labels': labels,
            'time': timestamp
        }

        # Insert the prediction summary into the MongoDB collection
        collection.insert_one(prediction_summary)

        # Close the MongoDB connection
        client.close()







