from django.db import models


class Menu(models.Model):
    """ Модель, представляющая меню. """

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """ Модель, представляющая пункт меню. """

    name = models.CharField(max_length=50)
    url = models.CharField(max_length=300)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_items")

    def __str__(self):
        return self.name
