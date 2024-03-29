from django.conf import settings
from django.db.models import Q
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = (
            "id",
            "text",
            "author",
            "pub_date",
        )
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для жанров."""

    class Meta:
        fields = ("name", "slug")
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        fields = ("name", "slug")
        model = Category


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания произведений."""

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = ("id", "name", "year", "description", "genre", "category")
        model = Title
        read_only_fields = ("title",)

    def to_representation(self, instance):
        serializer = TitleGETSerializer(instance)
        return serializer.data


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    title = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date", "title")
        model = Review

    def validate(self, data):
        """
        Проверяет количество отзывов на произведение
        от одного пользователя.
        """
        request = self.context["request"]
        if request.method == "POST":
            author = request.user
            title_id = self.context["view"].kwargs.get("title_id")
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError("Нельзя добавить больше 1 комментария")
        return data

    def validate_score(self, score):
        """Проверяет, что оценка произведения в рамках допустимых значений."""
        if score not in range(11):
            raise serializers.ValidationError(
                "Рейтинг произведения должен быть от 1 до 10"
            )
        return score


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей и выдачи токенов"""

    email = serializers.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
    )
    username = serializers.SlugField(
        max_length=settings.MAX_LENGTH_USERNAME,
    )

    class Meta:
        fields = ("username", "email")
        model = User

    def validate(self, data):
        email = data["email"]
        username = data["username"]
        if username != "me":
            if User.objects.filter(
                Q(username=username) | Q(email=email)
            ).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким именем или email уже существует"
                )
            return data
        raise serializers.ValidationError("Недопустимое имя пользователя")


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор получения JWT-токена"""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class AdminSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.
    Права доступа: Администратор.
    """

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User
