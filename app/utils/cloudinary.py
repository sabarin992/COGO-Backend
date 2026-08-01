import cloudinary.uploader
from fastapi import UploadFile


def upload_multiple_images(images: list[UploadFile]) -> list[str]:
    image_urls = []

    for image in images:
        result = cloudinary.uploader.upload(
            image.file,
            folder="cogo/vehicles"
        )

        image_urls.append(result["secure_url"])

    return image_urls