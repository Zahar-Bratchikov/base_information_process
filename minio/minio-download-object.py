from minio import Minio

if __name__ == '__main__':
    client = Minio(
        endpoint="localhost:9000",
        secure=False,
        access_key="QqffiDFXTX7fd1LLXLaX",
        secret_key="Z4EOfzTV0Xd1rUQeNt6BMunOmXv1yXdBL5UnRQpV",
    )
    bucket_name = "python-test-bucket3"
    object_name = "test_object.png"
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    client.fput_object(bucket_name, object_name, "test-img.png")
    client.fget_object(bucket_name, object_name, "downloaded.png")
