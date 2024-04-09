import boto3


class S3Client:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def upload_file(self, file_name, object_name):
        self.s3.upload_file(file_name, self.bucket_name, object_name)

    def download_file(self, object_name, file_name):
        self.s3.download_file(self.bucket_name, object_name, file_name)

    def delete_file(self, object_name):
        self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)

    def list_files(self):
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        return [content['Key'] for content in response['Contents']]

    def get_file(self, object_name):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=object_name)
        return response['Body'].read().decode('utf-8')