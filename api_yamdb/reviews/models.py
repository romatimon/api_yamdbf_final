from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import max_value_current_year
from users.models import User

SLICES_LIMIT = 20


class BaseCategoryGenre(models.Model):
    """Абстрактная модель для категории и жанра."""

    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name="Название")
    slug = models.SlugField(
        unique=True, verbose_name="Слаг"
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self) -> str:
        return self.name[:SLICES_LIMIT]


class BaseReviewComment(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ['pub_date']

    def __str__(self) -> str:
        return self.text[:SLICES_LIMIT]


class Category(BaseCategoryGenre):
    """Категории произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(BaseCategoryGenre):
    """Жанры произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    """Произведение искусства."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name="Название произведения"
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год создания",
        validators=[max_value_current_year],
    )
    description = models.TextField(
        verbose_name="Описание произведения",
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreConnect",
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        ordering = ['name']
        default_related_name = 'titles'
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self) -> str:
        return self.name[:SLICES_LIMIT]


class GenreConnect(models.Model):
    """Модель связи произведения и жанра."""

    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')
    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE,
                              verbose_name='Жанр')

    def __str__(self) -> str:
        return f'{self.title} {self.genre}'


class Review(BaseReviewComment):
    """Класс отзывов."""

    score = models.PositiveSmallIntegerField(
        verbose_name="Oценка", validators=[MinValueValidator(1),
                                           MaxValueValidator(10)])
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="произведение",
        null=True,
    )

    class Meta(BaseReviewComment.Meta):
        default_related_name = 'reviews'
        verbose_name = "Отзыв"
        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            ),
        )


class Comment(BaseReviewComment):
    """Класс комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name="oтзыв",
    )

    class Meta(BaseReviewComment.Meta):
        default_related_name = 'comments'
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
