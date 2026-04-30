"""MinIO 对象存储客户端"""

import io
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinioClient:
    """MinIO 客户端封装"""
    
    def __init__(self):
        endpoint = settings.minio_endpoint
        secure = settings.minio_secure
        
        self.client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )
        self.bucket_name = settings.minio_bucket
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """确保 bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error:
            pass
    
    def upload_file(
        self,
        object_name: str,
        data: BinaryIO | bytes,
        length: int,
        content_type: str = "application/octet-stream",
    ) -> str:
        """上传文件"""
        if isinstance(data, bytes):
            data = io.BytesIO(data)
        
        self.client.put_object(
            self.bucket_name,
            object_name,
            data,
            length,
            content_type=content_type,
        )
        return object_name
    
    def download_file(self, object_name: str) -> bytes:
        """下载文件"""
        response = self.client.get_object(self.bucket_name, object_name)
        return response.read()
    
    def delete_file(self, object_name: str) -> bool:
        """删除文件"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """获取文件访问 URL"""
        from datetime import timedelta
        return self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=timedelta(seconds=expires),
        )


# 全局实例
minio_client = MinioClient()