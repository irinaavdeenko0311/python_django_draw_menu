from django.contrib import admin

from .models import Menu, MenuItem


class BaseMenuItemInline(admin.TabularInline):
    """ Базовая модель административной панели, представляющая связанные модели. """

    model = MenuItem
    show_change_link = True


class MenuInline(BaseMenuItemInline):
    """ Модель административной панели, представляющая пункты меню. """

    verbose_name = "menu_item"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """ Модель административной панели, представляющая меню. """

    list_display = "id", "name"
    list_display_links = "id", "name"
    inlines = [MenuInline]


class MenuItemInline(BaseMenuItemInline):
    """ Модель административной панели, представляющая дочерние пункты меню. """

    verbose_name = "child"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """ Модель административной панели, представляющая пункт меню. """

    list_display = "id", "name", "url"
    list_display_links = "id", "name"
    inlines = [MenuItemInline]
