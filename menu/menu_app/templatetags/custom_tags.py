from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from django import template
from django.db.models import QuerySet
from django.template.context import RequestContext

from ..models import MenuItem

register = template.Library()


@dataclass
class MenuItemNode:
    """Узел пункта меню."""

    value: "MenuItem"
    children: List["MenuItemNode"] = field(default_factory=list)

    def add_child(self, menu_item: "MenuItemNode") -> None:
        """Метод для добавления дочернего узла."""

        self.children.append(menu_item)

    def delete_children(self) -> None:
        """Метод для удаления всех дочерних узлов."""

        self.children.clear()


@dataclass
class Menu:
    """Класс для работы с меню."""

    name: str = None
    count_menu_item: int = 0
    menu_tree: "MenuItemNode" = None

    def build_menu_tree(self, nodes: Dict, root_node: "MenuItemNode") -> None:
        """Метод для построения дерева."""

        children: Optional[List] = nodes.get(root_node.value)
        if children:
            for child in children:
                child_node = MenuItemNode(child)
                root_node.add_child(child_node)
                self.build_menu_tree(nodes, child_node)
        else:
            return

    def get_full_menu_tree(self, menu_name: str) -> None:
        """
        Метод для получения полного дерева меню из данных БД.

        Дерево добавляется в словарь для хранения во избежание повторных запросов в БД.
        """

        queryset: QuerySet = MenuItem.objects.filter(menu__name=menu_name).all()
        if queryset:
            nodes: Dict['MenuItem', List['MenuItem']] = dict()
            for menu_item in queryset:
                parent = menu_item.parent
                nodes.setdefault(parent, list()).append(menu_item)
            root_node_value: 'MenuItem' = nodes.get(None)[0]
            root_node = MenuItemNode(root_node_value)
            self.build_menu_tree(nodes, root_node)
            self.name = menu_name
            self.count_menu_item = len(queryset)
            self.menu_tree = root_node

    def cut_menu_tree(
        self,
        node: "MenuItemNode",
        link: str,
        root_parents: List['MenuItemNode'] = None,
        root_parent: 'MenuItemNode' = None,
    ) -> Literal[True]:
        """
        Метод изменения дерева меню исходя из значения url (активный пункт меню).

        Используется полное дерево меню, удаляются ненужные узлы.
        """

        self.count_menu_item += 1

        if self.is_active_node(node, link):
            return True

        neighbor_nodes = node.children
        active_node: List['MenuItem'] = list(
            filter(lambda x: self.is_active_node(x, link), neighbor_nodes)
        )
        if active_node:
            for neighbor in neighbor_nodes:
                if neighbor != active_node[0]:
                    neighbor.delete_children()
            if root_parents:
                for node_parent in root_parents:
                    if node_parent != root_parent:
                        node_parent.delete_children()
            return True

        if not root_parents:
            root_parents = neighbor_nodes
        for node in neighbor_nodes:
            parent = node if not root_parent else root_parent
            self.cut_menu_tree(node, link, root_parents, parent)

    @staticmethod
    def is_active_node(node: "MenuItemNode", link: str) -> bool:
        """
        Метод для определения, является ли узел активным.

        Если является - редактируются дочерние узлы.
        """
        if node.value.url == link:
            for child in node.children:
                child.delete_children()
            return True
        return False


@register.inclusion_tag("draw_menu.html", takes_context=True)
def draw_menu(context: RequestContext, menu_name: str) -> Dict:
    """Тег для формирования меню."""

    full_menu = Menu()
    full_menu.get_full_menu_tree(menu_name)

    if not full_menu.menu_tree:
        return {}

    active_menu_item_link = context.get("request").path

    current_menu = Menu(menu_tree=deepcopy(full_menu.menu_tree))
    current_menu.cut_menu_tree(current_menu.menu_tree, active_menu_item_link)
    if current_menu.count_menu_item == full_menu.count_menu_item:
        current_menu.menu_tree.delete_children()

    return {"menu": current_menu.menu_tree, "active_link": active_menu_item_link}
