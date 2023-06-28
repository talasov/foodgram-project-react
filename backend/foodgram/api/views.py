from django.contrib.auth import update_session_auth_hash
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Tag, Recipe, Favorite,
                            ShoppingCart, IngredientInRecipe,
                            Ingredient)
from users.models import User, Subscription
from .filters import RecipeFilter, IngredientFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeGetSerializer, FavoriteSerializer,
                          RecipePostSerializer, RecipeShortSerializer,
                          ShoppingCartSerializer, UserGetSerializer,
                          UserPostSerializer, SubscriptionSerializer,
                          UserWithRecipesSerializer)


def post_and_delete_action(self,
                           request,
                           model1,
                           model2,
                           serializer,
                           **kwargs):
    """ Добавление и удаление рецепта, подписки на пользователя """

    obj = get_object_or_404(model1, id=kwargs['pk'])
    data = request.data.copy()

    if model1 == Recipe:
        data.update({'recipe': obj.id})
    elif model1 == User:
        data.update(
            {'author': obj.id}
        )
    serializer = serializer(
        data=data, context={'request': request}
    )

    if request.method == "POST":
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data=self.get_serializer(obj).data
        )

    elif request.method == "DELETE" and model1 == Recipe:
        object = model2.objects.filter(
            recipe=obj, user=request.user
        )
        if not object.exists():
            return Response(
                {'errors': 'В избранном нет этого рецепта.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == "DELETE" and model1 == User:
        object = model2.objects.filter(
            author=obj, user=request.user
        )
        if not object.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ Управление пользователями и подписками """

    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):

        if self.action in ['subscriptions', 'subscribe']:

            return UserWithRecipesSerializer

        elif self.request.method == 'GET':

            return UserGetSerializer

        elif self.request.method == 'POST':

            return UserPostSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, ]

        return super(self.__class__, self).get_permissions()

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance

        return self.retrieve(request, *args, **kwargs)

    @action(
        ["POST"],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        update_session_auth_hash(self.request, self.request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        users = User.objects.filter(
            following__user=request.user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(users)

        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True,
                context={'request': request})

            return self.get_paginated_response(serializer.data)

        serializer = UserWithRecipesSerializer(
            users, many=True, context={'request': request}
        )

        return Response(serializer.data)

    @action(
        ["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthorOrAdminOrReadOnly],
    )
    def subscribe(self, request, **kwargs):
        return post_and_delete_action(
            self, request, User, Subscription, SubscriptionSerializer, **kwargs
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Получение списка всех ингредиентов ,
        Получение ингредиента по id """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Получение списка всех тэгов """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ Получение списка всех рецептов """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.action in ['favorite', 'shopping_cart', ]:
            return RecipeShortSerializer

        return RecipePostSerializer

    @action(["POST", "DELETE"], detail=True)
    def favorite(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            Favorite,
            FavoriteSerializer,
            **kwargs
        )

    @action(["POST", "DELETE"], detail=True)
    def shopping_cart(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            ShoppingCart,
            ShoppingCartSerializer,
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'Shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
