from minio import Minio

if __name__ == '__main__':
    client = Minio(
        endpoint="localhost:9000",
        secure=False,
        access_key="QqffiDFXTX7fd1LLXLaX",
        secret_key="Z4EOfzTV0Xd1rUQeNt6BMunOmXv1yXdBL5UnRQpV",
    )
    print(client.list_buckets())
    client.make_bucket("new-bucket")
    print(client.bucket_exists("new-bucket"))
    print(client.list_buckets())
    client.remove_bucket("new-bucket")
    print(client.bucket_exists("new-bucket"))
