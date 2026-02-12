import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

settings = get_settings()

# 로컬 개발용 저장소 경로
LOCAL_STORAGE_PATH = Path("uploads")
LOCAL_STORAGE_PATH.mkdir(exist_ok=True)


def _get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )


def generate_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4().hex}{ext}"


async def save_video(file_content: bytes, filename: str) -> str:
    """영상 파일 저장. S3 설정이 없으면 로컬 저장."""
    storage_key = f"videos/{filename}"

    if settings.aws_access_key_id:
        client = _get_s3_client()
        try:
            client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=storage_key,
                Body=file_content,
                ContentType="video/mp4",
            )
            return f"s3://{settings.s3_bucket_name}/{storage_key}"
        except ClientError as e:
            raise RuntimeError(f"S3 업로드 실패: {e}")
    else:
        local_path = LOCAL_STORAGE_PATH / filename
        local_path.write_bytes(file_content)
        return str(local_path)


async def get_video_url(storage_path: str) -> str:
    """저장된 영상의 접근 URL 반환."""
    if storage_path.startswith("s3://"):
        bucket, key = storage_path.replace("s3://", "").split("/", 1)
        client = _get_s3_client()
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
        return url
    else:
        return f"/static/{storage_path}"
