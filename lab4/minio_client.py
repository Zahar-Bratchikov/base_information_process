import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import mimetypes

from minio import Minio
from minio.error import S3Error, MinioException
from minio.datatypes import Bucket, Object


class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint="localhost:9000",
            access_key="Gaw4yD9zK1z69PlSWCY4",
            secret_key="Q1H3rA5OtTDF3jNSb2nBzruRWz2fztJXNyJvYKgJ",
            secure=False
        )

    def create_bucket(self, bucket_name: str, location: str = "us-east-1") -> bool:
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name, location=location)
                print(f"Bucket {bucket_name} created")
                return True
            else:
                print(f"Bucket {bucket_name} already exists")
                return False
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            return False

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        try:
            if force:
                objects = self.client.list_objects(bucket_name, recursive=True)
                for obj in objects:
                    self.client.remove_object(bucket_name, obj.object_name)
                print(f"Deleted objects: {sum(1 for _ in self.client.list_objects(bucket_name, recursive=True))}")
            self.client.remove_bucket(bucket_name)
            print(f"Bucket {bucket_name} deleted")
            return True
        except S3Error as e:
            print(f"Error deleting bucket: {e}")
            return False

    def list_buckets(self) -> list[Bucket]:
        """Getting list of all buckets"""
        try:
            buckets = self.client.list_buckets()
            print(f"Available buckets ({len(buckets)}):")
            print("-" * 60)
            for bucket in buckets:
                created = bucket.creation_date.strftime("%Y-%m-%d %H:%M:%S")
                print(f" * {bucket.name:30} created: {created}")
            print("-" * 60)
            return buckets
        except S3Error as e:
            print(f"Error listing buckets: {e}")
            return []

    def list_objects(self, bucket_name: str, prefix: str = "", recursive: bool = False) -> list[Object]:
        """Listing objects in bucket"""
        try:
            if not self.client.bucket_exists(bucket_name):
                print(f"Bucket '{bucket_name}' does not exist")
                return []
            objects = list(self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive))
            print(f"\nObjects in '{bucket_name}' (prefix: '{prefix}'):")
            print("-" * 80)
            print(f"{'NAME':<50} {'SIZE':>12} {'LAST MODIFIED':<20}")
            print("-" * 80)
            for obj in objects:
                size = f"{obj.size:,} B" if obj.size < 1024*1024 else f"{obj.size/1024/1024:.2f} MB"
                modified = obj.last_modified.strftime("%Y-%m-%d %H:%M") if obj.last_modified else "N/A"
                display_name = obj.object_name if len(obj.object_name) <= 47 else obj.object_name[:44] + "..."
                print(f"{display_name:<50} {size:>12} {modified:<20}")
            print("-" * 80)
            print(f"Total objects: {len(objects)}")
            return objects
        except S3Error as e:
            print(f"Error listing objects: {e}")
            return []

    def get_object_info(self, bucket_name: str, object_name: str) -> Optional[dict]:
        """Getting meta information about object"""
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            print(f"Meta information about object '{object_name}':")
            print("-" * 50)
            print(f"Bucket:        {bucket_name}")
            print(f"Object Name:   {stat.object_name}")
            print(f"Size:          {stat.size:,} bytes ({stat.size/1024/1024:.2f} MB)")
            print(f"Last Modified: {stat.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"ETag:          {stat.etag}")
            print(f"Content-Type:  {stat.content_type}")
            if stat.metadata:
                print(f"Metadata:")
                for key, value in stat.metadata.items():
                    print(f"  {key}: {value}")
            print("-" * 50)
            return {
                "bucket": bucket_name,
                "object_name": stat.object_name,
                "size": stat.size,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "metadata": dict(stat.metadata) if stat.metadata else {}
            }
        except S3Error as e:
            print(f"Error getting object info: {e}")
            return None

    def get_bucket_info(self, bucket_name: str) -> Optional[dict]:
        """Getting meta information about bucket"""
        try:
            if not self.client.bucket_exists(bucket_name):
                print(f"Bucket '{bucket_name}' does not exist")
                return None
            objects = list(self.client.list_objects(bucket_name, recursive=True))
            total_size = sum(obj.size for obj in objects)
            print(f"\nMeta information about bucket '{bucket_name}':")
            print("-" * 50)
            print(f"Name:              {bucket_name}")
            print(f"Exists:            Yes")
            print(f"Total Objects:     {len(objects)}")
            print(f"Total Size:        {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
            if objects:
                print(f"First Object:      {objects[0].object_name}")
                print(f"Last Modified:     {objects[-1].last_modified.strftime('%Y-%m-%d %H:%M:%S') if objects[-1].last_modified else 'N/A'}")
            print("-" * 50)
            return {
                "name": bucket_name,
                "exists": True,
                "object_count": len(objects),
                "total_size": total_size
            }
        except S3Error as e:
            print(f"Error getting bucket info: {e}")
            return None

    def upload_object(self, bucket_name: str, file_path: str, 
                     object_name: Optional[str] = None,
                     content_type: Optional[str] = None) -> bool:
        """Uploading object to bucket"""
        try:
            if not self.client.bucket_exists(bucket_name):
                print(f"Bucket '{bucket_name}' does not exist")
                return False
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"File '{file_path}' not found")
                return False
            if object_name is None:
                object_name = file_path.name
            if content_type is None:
                content_type, _ = mimetypes.guess_type(str(file_path))
                content_type = content_type or "application/octet-stream"
            file_size = file_path.stat().st_size
            print(f"Uploading: {file_path} -> {bucket_name}/{object_name}")
            print(f"   Size: {file_size:,} bytes | Content-Type: {content_type}")
            result = self.client.fput_object(
                bucket_name, 
                object_name, 
                str(file_path),
                content_type=content_type
            )
            print(f"Object successfully uploaded (ETag: {result.etag})")
            return True
        except S3Error as e:
            print(f"Error uploading object: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def download_object(self, bucket_name: str, object_name: str, 
                       destination_path: Optional[str] = None) -> bool:
        """Downloading object from bucket"""
        try:
            if not self.client.bucket_exists(bucket_name):
                print(f"Bucket '{bucket_name}' does not exist")
                return False
            try:
                stat = self.client.stat_object(bucket_name, object_name)
            except S3Error:
                print(f"Object '{object_name}' not found in bucket '{bucket_name}'")
                return False
            if destination_path is None:
                destination_path = Path(object_name).name
            dest_path = Path(destination_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Downloading: {bucket_name}/{object_name} -> {destination_path}")
            print(f"   Size: {stat.size:,} bytes")
            self.client.fget_object(bucket_name, object_name, str(dest_path))
            print(f"Object successfully downloaded")
            return True
        except S3Error as e:
            print(f"Error downloading object: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """Deleting object (additional useful operation)"""
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"Object '{object_name}' deleted from bucket '{bucket_name}'")
            return True
        except S3Error as e:
            print(f"Error deleting object: {e}")
            return False


def create_parser() -> argparse.ArgumentParser:
    """Creating parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description="S3 Console Client for MinIO/S3-compatible storages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of usage:
  # Creating bucket
  %(prog)s bucket create my-bucket
  
  # Uploading file
  %(prog)s object upload my-bucket ./file.txt
  
  # Downloading file
  %(prog)s object download my-bucket file.txt ./downloaded.txt
  
  # Viewing objects
  %(prog)s object list my-bucket --prefix docs/
  
  # Meta information
  %(prog)s info object my-bucket file.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # === Bucket commands ===
    bucket_parser = subparsers.add_parser('bucket', help='Operations with bucket')
    bucket_sub = bucket_parser.add_subparsers(dest='bucket_action')
    
    bucket_create = bucket_sub.add_parser('create', help='Create bucket')
    bucket_create.add_argument('name', help='Name of bucket')
    bucket_create.add_argument('--location', '-l', default='us-east-1',
                              help='Region (default: us-east-1)')
    
    bucket_delete = bucket_sub.add_parser('delete', help='Delete bucket')
    bucket_delete.add_argument('name', help='Name of bucket')
    bucket_delete.add_argument('--force', '-f', action='store_true',
                              help='Force delete all objects before deleting bucket')
    
    bucket_sub.add_parser('list', help='List all buckets')
    
    # === Object commands ===
    object_parser = subparsers.add_parser('object', help='Operations with objects')
    object_sub = object_parser.add_subparsers(dest='object_action')
    
    object_list = object_sub.add_parser('list', help='List of objects in bucket')
    object_list.add_argument('bucket', help='Name of bucket')
    object_list.add_argument('--prefix', '-p', default='', help='Prefix for filtering')
    object_list.add_argument('--recursive', '-r', action='store_true', 
                            help='Recursive list (including subfolders)')
    
    object_upload = object_sub.add_parser('upload', help='Upload object')
    object_upload.add_argument('bucket', help='Name of bucket')
    object_upload.add_argument('file', help='Path to local file')
    object_upload.add_argument('--object-name', '-o', help='Name of object in S3 (default: file name)')
    object_upload.add_argument('--content-type', '-t', help='Content-Type of file')
    
    object_download = object_sub.add_parser('download', help='Download object')
    object_download.add_argument('bucket', help='Name of bucket')
    object_download.add_argument('object', help='Name of object in S3')
    object_download.add_argument('--output', '-O', help='Local path for saving')
    
    object_delete = object_sub.add_parser('delete', help='Delete object')
    object_delete.add_argument('bucket', help='Name of bucket')
    object_delete.add_argument('object', help='Name of object in S3')
    
    # === Info commands ===
    info_parser = subparsers.add_parser('info', help='Getting meta information')
    info_sub = info_parser.add_subparsers(dest='info_action')
    
    info_bucket = info_sub.add_parser('bucket', help='Information about bucket')
    info_bucket.add_argument('name', help='Name of bucket')
    
    info_object = info_sub.add_parser('object', help='Information about object')
    info_object.add_argument('bucket', help='Name of bucket')
    info_object.add_argument('object', help='Name of object')
    
    return parser


def main():
    """Entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = MinioClient()
    except Exception as e:
        print(f"Error connecting: {e}")
        sys.exit(1)
    
    try:
        if args.command == 'bucket':
            if args.bucket_action == 'create':
                client.create_bucket(args.name, args.location)
            elif args.bucket_action == 'delete':
                client.delete_bucket(args.name, force=args.force)
            elif args.bucket_action == 'list':
                client.list_buckets()
            else:
                parser.parse_args(['bucket', '-h'])
        
        elif args.command == 'object':
            if args.object_action == 'list':
                client.list_objects(args.bucket, args.prefix, args.recursive)
            elif args.object_action == 'upload':
                client.upload_object(args.bucket, args.file, args.object_name, args.content_type)
            elif args.object_action == 'download':
                client.download_object(args.bucket, args.object, args.output)
            elif args.object_action == 'delete':
                client.delete_object(args.bucket, args.object)
            else:
                parser.parse_args(['object', '-h'])
        
        elif args.command == 'info':
            if args.info_action == 'bucket':
                client.get_bucket_info(args.name)
            elif args.info_action == 'object':
                client.get_object_info(args.bucket, args.object)
            else:
                parser.parse_args(['info', '-h'])
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()