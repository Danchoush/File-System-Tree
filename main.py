import sys
import subprocess
import re
import pathlib

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QComboBox

sorting_variants = ["Не сортировать", "Сортировка по именам", "Сортировка по времени", "Сортировка по размеру"]   #Список типов сортировки


def create_tree(path, keys):
    result = subprocess.run(['ls', keys, '--group-directories-first', path],stdout=subprocess.PIPE)   # Вызов системной команды ls, считывающая данные из директорий
    if result.returncode == 0:
        output = result.stdout.decode("utf-8")
        blocks = re.split(r'\n\n+', output)  # Разделение блоков

        # Создание структуры данных для дерева
        tree =QTreeWidgetItem()
        current_node = tree

        # Цикл разбиения данных внутри блоков
        for block in blocks:
            lines = block.strip().split('\n')
            parse_block(current_node, lines)
        return tree
    else:
        print("Ошибка выполнения 'ls':", result.stderr)
    return None


# Обновление всего дерева при изменении типа сортировки
def update_tree():
    selected_sorting = sorting_line.currentText()
    if selected_sorting == sorting_variants[0]: #None
        keys = "-RLlhaU"
    if selected_sorting == sorting_variants[1]: #Имя
        keys = "-RLlhaX"
    if selected_sorting == sorting_variants[2]: #Время
        keys = "-RLlhat"
    if selected_sorting == sorting_variants[3]: #Размер
        keys = "-RLlhaS"
    tree.clear()
    _path = str(pathlib.Path.home())
    tree_data = create_tree(_path, keys)
    tree.addTopLevelItem(tree_data)


# Заполенение данных внутри папки
def fill_folder(lines, full_path, parent_item):
    sub_items = [line.strip() for line in lines[2:]]

    for item in sub_items:
        # Разделение данных на имя, размер и время измениения файла
        item_data = item.split()
        item_name = item_data[-1]
        item_size = item_data[4]
        item_time = ' '.join(item_data[-4:-1])

        item_path = full_path.copy()
        item_path.append(item_name)
        item_path = '/'.join(item_path)

        if item_name != '.' and item_name != "..":  # Избавляемся от ненужных ссылок на прошлые каталоги
            file_item = QTreeWidgetItem()
            file_item.setText(0, item_name)
            file_item.setText(1, item_path)
            file_item.setText(2, item_size)
            file_item.setText(3, item_time)
            file_item.setIcon(0, QIcon("icons/file_ico.png"))

            parent_item.addChild(file_item)
            parent_item.setIcon(0, QIcon("icons/folder_ico.png"))


def who_parent(possible_parent,true_child_path):
    if possible_parent.text(1) == true_child_path:
        return possible_parent

    for child_index in range(possible_parent.childCount()):
        parent = who_parent(possible_parent.child(child_index), true_child_path)    # Рекурсивная функция поиска родительской папки
        if parent:
            return parent

    return None


def parse_block(parent_item, lines):
    if not lines:
        return []

    full_path = re.split('/', lines[0].strip(':'))
    full_path_str = full_path.copy()
    full_path_str = '/'.join(full_path_str)
    if full_path_str != str(pathlib.Path.home()):
        parent_item = who_parent(parent_item, full_path_str)
    # Заполнение первого блока, где нет ссылки на родителя
    else:
        full_path = re.split('/', lines[0].strip(':'))
        parent_item.setText(0, full_path[-1])
        full_path_str = full_path.copy()
        full_path_str = '/'.join(full_path_str)
        parent_item.setText(1, full_path_str)
    fill_folder(lines, full_path, parent_item) # Запуск функции, заполняющей ветвь дерева


if __name__ == '__main__':
    # Приложение Qt
    app = QApplication([])

    # Окно для дерева
    window = QMainWindow()
    tree = QTreeWidget()
    tree.setHeaderLabels(['Название','Полный путь', 'Размер', 'Дата изменения'])
    tree.setColumnCount(4)
    tree.header().setSectionResizeMode(True)

    # Получение дерева из файловой системы
    _path = str(pathlib.Path.home())
    tree_data = create_tree(_path, "-RLlha")
    tree.addTopLevelItem(tree_data)

    sorting_line = QComboBox()
    sorting_line.addItems(sorting_variants)
    sorting_line.currentIndexChanged.connect(update_tree)

    # Создаем вертикальный макет для добавления QTreeWidget и QLineEdit
    layout = QVBoxLayout()
    layout.addWidget(sorting_line)
    layout.addWidget(tree)

    main_widget = QWidget()
    main_widget.setLayout(layout)

    # Настройка окна
    window.setCentralWidget(main_widget)
    window.setWindowTitle("Файловая система")
    window.resize(900,700)
    window.show()

    # Запуск приложения
    sys.exit(app.exec_())

