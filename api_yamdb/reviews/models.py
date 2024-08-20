from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    """Категории (типы) произведений."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['id']


class Comment(models.Model):
    """Комментарии к отзывам."""

    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['id']


class Genre(models.Model):
    """Категории жанров."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['id']


class Review(models.Model):
    """Отзывы."""

    text = models.TextField()
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_relationships'
            ),
        ]

    def __str__(self):
        return self.text


class Title(models.Model):
    """Произведения, к которым пишут отзывы (определённый фильм, книга или
    песенка)."""

    name = models.CharField(max_length=256)
    description = models.TextField()
    year = models.PositiveSmallIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    rating = models.IntegerField(null=True)

    class Meta:
        ordering = ['id']


class GenreTitle(models.Model):

    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
