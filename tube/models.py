from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator

import uuid


#TIPS:usersモデルを外部キーとして指定する時は、必ずsettings.pyに書いてあるAUTH_USER_MODELを指定する。(usersアプリのmodelsのクラスを直importしてはならない)
#参照:https://stackoverflow.com/questions/34305805/django-foreignkeyuser-in-models


class Category(models.Model):

    class Meta:
        db_table = "category"

    # TIPS:数値型の主キーではPostgreSQLなど一部のDBでエラーを起こす。それだけでなく予測がされやすく衝突しやすいので、UUID型の主キーに仕立てる。
    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    name   = models.CharField(verbose_name="カテゴリ名", max_length=20)

    def __str__(self):
        return self.name


class Video(models.Model):

    class Meta:

        db_table = "video"

    id       = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    category = models.ForeignKey(Category, verbose_name="カテゴリ", on_delete=models.PROTECT)
    dt       = models.DateTimeField(verbose_name="投稿日", default=timezone.now)

    title        = models.CharField(verbose_name="タイトル", max_length=50)
    description  = models.CharField(verbose_name="動画説明文", max_length=300)
    movie        = models.FileField(verbose_name="動画", upload_to="tube/movie", blank=True)
    thumbnail    = models.ImageField(verbose_name="サムネイル", upload_to="tube/thumbnail/", null=True)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    edited       = models.BooleanField(default=False)
    mime         = models.TextField(verbose_name="MIMEタイプ", null=True)
    views        = models.IntegerField(verbose_name="再生回数", default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title


class VideoComment(models.Model):

    class Meta:
        db_table = "comment"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    content = models.CharField(verbose_name="コメント文", max_length=500)
    target  = models.ForeignKey(Video, verbose_name="コメント先の動画", on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class History(models.Model):

    class Meta:
        db_table     = "history"

    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt     = models.DateTimeField(verbose_name="視聴日時", default=timezone.now)
    target = models.ForeignKey(Video, verbose_name="視聴した動画", on_delete=models.CASCADE)
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="視聴したユーザー", on_delete=models.CASCADE)
    views  = models.IntegerField(verbose_name="視聴回数", default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.target.title


class MyList(models.Model):

    class Meta:
        db_table    = "mylist"

    id       = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt       = models.DateTimeField(verbose_name="登録日時", default=timezone.now)
    target   = models.ForeignKey(Video, verbose_name="マイリスト動画", on_delete=models.CASCADE)
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="登録したユーザー", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.title


class Notify(models.Model):

    class Meta:
        db_table     = "notify"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt      = models.DateTimeField(verbose_name="通知日時", default=timezone.now)
    content = models.CharField(verbose_name="通知内容", max_length=200)

    def __str__(self):
        return self.content


class GoodVideo(models.Model):

    class Meta:
        db_table    = "good_video"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt      = models.DateTimeField(verbose_name="評価日時", default=timezone.now)
    target  = models.ForeignKey(Video, verbose_name="対象動画", on_delete=models.CASCADE)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="高評価したユーザー", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.title


class BadVideo(models.Model):

    class Meta:
        db_table = "bad_video"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt      = models.DateTimeField(verbose_name="評価日時", default=timezone.now)
    target  = models.ForeignKey(Video, verbose_name="対象動画", on_delete=models.CASCADE)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="低評価したユーザー", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.title


