#!/usr/local/bin/python3

from PyQt5 import QtGui as qtg, QtCore as qtc, QtWidgets as qtw
from typing import Optional, Union
import sys
from main import Game, Player


class MainWindow(qtw.QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.main_widget = qtw.QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(qtw.QVBoxLayout())
        
        self.create_start_settings()
        self.create_buttons()
        self.show()

    def create_buttons(self) -> None:
        """
        Создаёт кнопки для функционирования игры.
        """
        self.approve_button = qtw.QPushButton("Сравнить")
        self.approve_button.setShortcut(qtc.Qt.Key_Return)
        self.approve_button.clicked.connect(self.check_sequence)
        self.retry_button = qtw.QPushButton("Начать заново")
        self.retry_button.clicked.connect(self.new_game)
        self.button_widget = qtw.QWidget()
        self.button_widget.setLayout(qtw.QHBoxLayout())
        self.button_widget.layout().addWidget(self.approve_button)
        self.button_widget.layout().addWidget(self.retry_button)
        self.main_widget.layout().addWidget(self.button_widget)

    def draw_icons(self) -> None:
        """Отрисовывает кругляшки, в которых игрок будет затем цвета выбирать.
        Кругляшкам задаётся имя для дальнейшей идентификации.
        Также напротив ряда кругляшков задаётся метка, где будут выписаны все успехы игрока на 
        данном этапе.
        """
        for i in range(self.game.try_count + 1):
            self.icon_line_widget = qtw.QWidget()
            self.icon_line_widget.setLayout(qtw.QHBoxLayout())
            for j in range(self.game.peg_count):
                if i == 0:
                    round_icon = RoundLabel(colour=self.game_sequence[j], colours=tuple(self.game.COLOURS.values()))
                    # Закомментировать строку ниже, если есть необходимость увидеть закодированную последовательность.
                    round_icon.setHidden(True)
                else:
                    round_icon = RoundLabel(colours=tuple(self.game.COLOURS.values()))                    
                round_icon.setObjectName(f"icon{j}{i}")
                if i != 1:
                    round_icon.setDisabled(True)
                self.icon_line_widget.layout().addWidget(round_icon)
            if i > 0:
                info_label = qtw.QLabel("reds: _, whites: _")
                info_label.setObjectName(f'info{i}')
                self.icon_line_widget.layout().addWidget(info_label)
            self.main_widget.layout().addWidget(self.icon_line_widget)
        

    def check_sequence(self) -> qtw.QComboBox | None:
        """Производится сравнение последовательностей игры и игрока, уточняются результаты 
        (right и displaced), выводится либо сообщение об ошибке / о результатах игры, либо вызывается 
        смена строки.

        Returns:
            qtw.QComboBox | None: сообщение для игрока или ничего
        """
        icons_list = []
        for j in range(self.game.peg_count):
            child = self.findChild(RoundLabel, f'icon{j}{self.i}')
            if child.colour == 'gray':
                return qtw.QMessageBox.information(self, "Упс!", 
                                            "Выберите цвета в каждом кружке!", qtw.QMessageBox.Ok)
            else:
                icons_list.append(child.colour)
        else:
            right_pegs_count, displaced_pegs_count = self.game.row_analyse_result(icons_list, self.game_sequence)
            label = self.findChild(qtw.QLabel, f'info{self.i}')
            label.setText(f'reds: {right_pegs_count}, whites: {displaced_pegs_count}')
            if right_pegs_count == len(self.game_sequence):
                return self.show_info_box("Ура!!! Вы отгадали!")
            else:
                self.change_row()

    def show_info_box(self, info: str) -> qtw.QMessageBox:
        """Создаёт информационное окно с кнопками "Новая игра" и "Выход"

        Returns:
            qtw.QMessageBox: _description_
        """
        msg = qtw.QMessageBox()
        msg.setWindowTitle("Конец игры")
        msg.setText(info)
        retry_button = qtw.QMessageBox.addButton(msg, "Попробовать ещё раз", 
                                                 qtw.QMessageBox.ButtonRole.ActionRole)
        retry_button.clicked.connect(self.new_game)
        exit_button = qtw.QMessageBox.addButton(msg, "Выход", qtw.QMessageBox.ButtonRole.ActionRole)
        exit_button.clicked.connect(self.close)
        return msg.exec_()

    def new_game(self) -> None:
        """
        Запускает методы обнуления процесса для игры заново. 
        Создаётся новая игровая последовательность, кружки становятся серыми, лейблы без подсчёты.
        """
        self.game_sequence = self.create_game_sequence()
        self.make_elements_default_again()
        self.i = 1

    def create_start_settings(self) -> None:
        """
        Задаются новая игра, новая последовательность, рисуются кружки и лейблы к ним по умолчанию.
        """
        self.game = Game()
        self.game_sequence = self.create_game_sequence()
        self.draw_icons()
        self.i = 1
        
    def create_game_sequence(self) -> list:
        """
        Создаётся новая игровая последовательность с использованием метода класса Game.
        Returns:
            list: _description_
        """
        return [self.game.COLOURS[_] for _ in self.game.create_code_sequence()]

    def make_elements_default_again(self) -> None:
        """
        Все элементы откатываются к значению по умолчанию (кружки - серые, лейблы - без подсчёта).
        """
        for i in range(self.game.try_count + 1):
            for j in range(self.game.peg_count):
                icon = self.findChild(RoundLabel, f'icon{j}{i}')
                if i == 0:
                    icon.setColor(self.game_sequence[j])
                else:
                    icon.setColor("gray")
                if i == self.i:
                    icon.setDisabled(True)
                elif i == 1:
                    icon.setDisabled(False)
            info_label = self.findChild(qtw.QLabel, f'info{i}')
            if info_label:
                info_label.setText("reds: _, whites: _")

    def change_row(self) -> qtw.QMessageBox | None:
        """
        Сменяет строку (переходит на новую стадию игры), блокируя текущую строку и разблокируя следующую.
        Returns:
            qtw.QComboBox | None: сообщение для игрока о конце игры или ничего
        """
        if self.i < self.game.try_count:
                self.i += 1
        else:
            return self.show_info_box("Вы израсходовали все попытки! Попробуйте снова!")
        for j in range(self.game.peg_count):
            new_child = self.findChild(RoundLabel, f'icon{j}{self.i}')
            new_child.setDisabled(False)
            child = self.findChild(RoundLabel, f'icon{j}{self.i-1}')
            child.setDisabled(True)
            

class RoundLabel(qtw.QLabel):

    def __init__(self, colour: str = "gray", colours: tuple | None = None) -> None:
        super().__init__()
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
        self.radius = 10
        self.colour = colour
        self.colours = colours

        self.target = qtg.QPixmap(self.size())  
        self.target.fill(qtc.Qt.transparent) 

        self.main_pixmap = qtg.QPixmap(self.size())
        self.main_pixmap.fill(qtg.QColor(colour))
        self._create_round_shape()
        

    def _create_round_shape(self) -> None:
        """
        Создание кружков, способных реагировать на нажатие и менять цвет. Отрисовка залитого круга
        поверх прозрачного слоя.
        """
        painter = qtg.QPainter(self.target)
        painter.setRenderHint(qtg.QPainter.Antialiasing, True)
        painter.setRenderHint(qtg.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(qtg.QPainter.SmoothPixmapTransform, True)

        path = qtg.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.main_pixmap)
        self.setPixmap(self.target)

    def setColor(self, colour: str) -> None:
        """Задаёт новый цвет для кружка, а затем вызывает метод для его перерисовки.

        Args:
            colour (str): наименование цвета, берётся из настроек игры (класс Game)
        """
        self.main_pixmap.fill(qtg.QColor(colour))
        self.colour = colour
        self._create_round_shape()

    def mousePressEvent(self, ev: qtg.QMouseEvent) -> None:
        """Реализация реакции на нажатие со стороны объекта.

        Args:
            ev (qtg.QMouseEvent): сигнал нажатия клавиши мыши
        """
        if self.colour == 'gray':
            self.setColor(self.colours[0])
        else:
            ind = (self.colours.index(self.colour) + 1) % len(self.colours)
            self.setColor(self.colours[ind])


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())