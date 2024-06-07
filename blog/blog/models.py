from io import BytesIO
from pathlib import Path
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from PIL import Image

from utils.models import TimestampModel

User = get_user_model()


class Blog(TimestampModel):
    CATEGORY_CHOICES = (
        ("free", "자유"),
        ("travel", "여행"),
        ("cat", "고양이"),
        ("dog", "강아지"),
    )
    category = models.CharField(
        "카테고리", max_length=10, choices=CATEGORY_CHOICES, default="free"
    )
    title = models.CharField("제목", max_length=100)
    content = models.TextField("본문")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # models.CASCADE => 같이 삭제
    # models.PROTECT => 삭제가 불가능함 (유저를 삭제하려고할때 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => 널값을 넣습니다. => 유저 삭제시 블로그의 author가 null이 됨

    image = models.ImageField(
        "이미지", null=True, blank=True, upload_to="blog/%Y/%m/%d"
    )
    thumbnail = models.ImageField(
        "썸네일", null=True, blank=True, upload_to="blog/%Y/%m/%d/thumbnail"
    )

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"blog_pk": self.pk})

    class Meta:
        verbose_name = "블로그"
        verbose_name_plural = "블로그 목록"

    def save(self, *args, **kwargs):
        if not self.image:
            return super().save(*args, **kwargs)

        image = Image.open(self.image)
        image.thumbnail((300, 300))
        image_path = Path(self.image.name)

        thumbnail_name = image_path.stem
        thumbnail_extension = image_path.suffix.lower()

        thumbnail_filename = f"{thumbnail_name}_thumb{thumbnail_extension}"

        file_type = "UNKNOWN"
        match thumbnail_extension:
            case ".jpg" | ".jpeg":
                file_type = "JPEG"
            case ".gif":
                file_type = "GIF"
            case ".png":
                file_type = "PNG"
            case _:
                return super().save(*args, **kwargs)

        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        self.thumbnail.save(thumbnail_filename, temp_thumb, save=False)
        temp_thumb.close()

        return super().save(*args, **kwargs)

    # category update
    # Blog.objects.filter(category='').update(category='free')

    def get_thumbnail_image_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image:
            return self.image.url
        return None


# 제목
# 본문
# 작성일자
# 수정일자
# 카테고리

# 작성자 => 패스(추후 업데이트)


class Comment(TimestampModel):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.CharField("본문", max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.blog.title} 댓글"

    class Meta:
        verbose_name = "댓글"
        verbose_name_plural = "댓글 목록"
        ordering = ("-created_at", "-id")

    # blog
    # 댓글 내용
    # 작성자
    # 작성일자
    # 수정일자
