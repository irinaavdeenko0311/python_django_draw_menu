from django.http import HttpRequest
from django.template import RequestContext, Template
from django.test import Client, TestCase

from .models import Menu, MenuItem

menus = [
    Menu(name="menu_1"),
    Menu(name="menu_2"),
    Menu(name="menu_3"),
]

menu_items = [
    MenuItem(id=1, name="root", url="/root", parent_id=None, menu_id=1),
    MenuItem(id=2, name="item_1", url="/item_1", parent_id=1, menu_id=1),
    MenuItem(id=3, name="item_2", url="/item_2", parent_id=1, menu_id=1),
    MenuItem(id=4, name="item_3", url="/item_3", parent_id=1, menu_id=1),
    MenuItem(id=5, name="item_4", url="/item_4", parent_id=1, menu_id=1),
    MenuItem(id=6, name="item_1_1", url="/item_1_1", parent_id=2, menu_id=1),
    MenuItem(id=7, name="item_1_2", url="/item_1_2", parent_id=2, menu_id=1),
    MenuItem(id=8, name="item_3_1", url="/item_3_1", parent_id=3, menu_id=1),
    MenuItem(id=9, name="item_3_2", url="/item_3_2", parent_id=3, menu_id=1),
    MenuItem(id=10, name="item_1_2_1", url="/item_1_2_1", parent_id=7, menu_id=1),
    MenuItem(id=11, name="item_1_2_2", url="/item_1_2_2", parent_id=7, menu_id=1),
    MenuItem(id=12, name="item_1_2_3", url="/item_1_2_3", parent_id=7, menu_id=1),
    MenuItem(id=13, name="item_1_2_1_1", url="/item_1_2_1_1", parent_id=10, menu_id=1),
]


class TestMenu(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Menu.objects.bulk_create(menus)
        MenuItem.objects.bulk_create(menu_items)
        cls.client = Client()

    def test_model_menu(self):
        menu_name = "menu_2"
        menu_obj = Menu.objects.filter(name=menu_name)
        self.assertEqual(menu_obj[0].id, 2)

    def test_model_menu_item(self):
        menu_name = "menu_1"
        menu_item_obj = MenuItem.objects.filter(menu__name=menu_name)
        self.assertEqual(len(menu_item_obj), 13)

    def test_tag_draw_menu(self):
        request = HttpRequest()

        request.path = "/"
        context = RequestContext(request=request)
        template = Template("{% load custom_tags %}{% draw_menu 'menu_1' %}")
        response = template.render(context)
        self.assertIn("root", response)
        self.assertNotIn("item_1", response)
        self.assertNotIn("border-color", response)

        request.path = "/item_1_2"
        context = RequestContext(request=request)
        template = Template("{% load custom_tags %}{% draw_menu 'menu_1' %}")
        response = template.render(context)
        self.assertIn("item_1_2", response)
        self.assertNotIn("item_3_1", response)
        self.assertNotIn("item_1_2_1_1", response)
