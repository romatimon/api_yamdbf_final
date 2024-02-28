from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from api.v1.mixins import CreateListDestroyViewSet
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly,
)
from .serializers import (
    AdminSerializer, CategorySerializer, CommentSerializer,
    ConfirmationCodeSerializer, GenreSerializer, ReviewSerializer,
    SignUpSerializer, TitleCreateSerializer, TitleGETSerializer,
)
from reviews.models import Category, Genre, Review, Title
from users.models import User


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """Получение кода подтверждения на email"""

    serializer = SignUpSerializer(data=request.data)
    username = request.data.get("username")
    email = request.data.get("email")
    user = User.objects.filter(username=username, email=email).first()
    if user:
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="Регистрация YaMDb",
            message=(
                f"Код подтверждения для {user.username}:{confirmation_code}."
            ),
            from_email=None,
            recipient_list=[user.email],
        )
        message = (
            "Данный пользователь уже зарегистрирован."
            "Сообщение с кодом отправлено на почту."
        )
        return Response(message, status=status.HTTP_200_OK)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    username = serializer.validated_data["username"]
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="Регистрация YaMDb",
        message=(
            f"Код подтверждения для {user.username}:{confirmation_code}."
        ),
        from_email=None,
        recipient_list=[user.email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def token(request):
    """Получение JWT-токена."""
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )

    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Получение всех пользователей, добавление пользователя администратором.
    Получение, изменение и удаление пользователя по username администратором.
    Получение и изменение данных своей учетной записи пользователем.
    """

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = [
        "username",
    ]
    lookup_field = "username"
    http_method_names = ["get", "post", "patch", "delete", "head"]

    @action(
        url_path="me",
        methods=["get", "patch"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def show_user_profile(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        else:
            serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options',
                         'trace']

    queryset = (
        Title.objects.select_related("category")
        .prefetch_related("genre")
        .annotate(rating=Avg("reviews__score")).order_by("rating")
    )
    serializer_class = TitleGETSerializer
    pagination_class = LimitOffsetPagination
    filter_class = filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """
        Метод для определения типа сериализатора.
        """
        if self.request.method in (
            "POST",
            "PATCH",
        ):
            return TitleCreateSerializer
        return TitleGETSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options',
                         'trace']

    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    serializer_class = CommentSerializer

    def get_review(self):
        """Служебная. Полчает отзыв."""
        return get_object_or_404(Review,
                                 title_id=self.kwargs.get('title_id'),
                                 id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Получает все комментарии к отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает новый комментарий к отзыву."""
        return serializer.save(author=self.request.user,
                               review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options',
                         'trace']

    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly)
    serializer_class = ReviewSerializer

    def get_title(self):
        """Служебная. Полчает произведение."""
        return get_object_or_404(Title,
                                 id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получаем все отзовы к произведениям."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создаем новый отзыв."""
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )
