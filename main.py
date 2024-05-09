import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint


class Shape:
    def __init__(self, shape_data):
        self.shape_data = shape_data
        self.color = random.choice(self.colors)

    @property
    def colors(self):
        return [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 255, 0),
                QColor(255, 0, 255), QColor(0, 255, 255)]

    def draw(self, painter, x, y):
        for dx, dy in self.shape_data:
            painter.fillRect((x + dx) * 40, (9 - y - dy) * 40, 40, 40, self.color)


class Tetris(QWidget):
    def __init__(self):
        super().__init__()
        self.board = None
        self.initUI()
        self.score = 0
        self.board_size = 10
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.available_shapes = [
            Shape([(0, 0), (0, 1), (1, 0), (1, 1)]),  # квадрат2х2
            Shape([(0, 0), (0, 1), (1, 0), (1, 0)]),  # треугольник с основанием 2
            Shape([(0, 0), (0, 1), (0, 2)])  # вертикальная палка на 3
        ]
        self.selected_shape = None
        self.selected_shape_pos = QPoint(0, 9)

    def initUI(self):
        self.setGeometry(100, 100, 560, 700)
        self.setWindowTitle('Tetris with Custom Rules')
        self.show()

    def draw_grid(self, painter):
        pen = QPen()
        pen.setColor(QColor(100, 100, 100))  # Цвет сетки
        painter.setPen(pen)
        for i in range(self.board_size + 1):
            painter.drawLine(i * 40, 0, i * 40, self.board_size * 40)  # Вертикальные линии
            painter.drawLine(0, i * 40, self.board_size * 40, i * 40)  # Горизонтальные линии

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QColor(255, 255, 255))
        # Отрисовка фигур в областях выбора
        for i, shape in enumerate(self.available_shapes[:3]):
            shape.draw(painter, 1 + i * 120 // 40 + i, -7)
        # Отрисовка выбранной фигуры
        if self.selected_shape is not None:
            self.selected_shape.draw(painter, self.selected_shape_pos.x(), self.selected_shape_pos.y())
        # Отрисовка игрового поля
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 1:
                    painter.fillRect(j * 40, (self.board_size - 1 - i) * 40, 40, 40, QColor(255, 0, 0))
        self.draw_grid(painter)
        # Отображение счета
        self.draw_score(painter)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            # Проверка, что клик был в нижней части окна
            if y >= 560:
                for i in range(3):
                    if 10 + i * 120 + i * 40 <= x < 130 + i * 120 + i * 40 and 560 <= y < 680:
                        self.selected_shape = self.available_shapes[i]
                        self.selected_shape_pos = QPoint(x // 40, self.board_size - 1 - y // 40)
                        self.update()
                        break

        print(self.selected_shape)

    def mouseMoveEvent(self, event):
        if self.selected_shape is not None:
            self.selected_shape_pos = QPoint(event.x() // 40, 9 - event.y() // 40)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selected_shape is not None:
            x = event.x() // 40
            y = self.board_size - 1 - event.y() // 40

            if self.can_place(x, y, self.selected_shape):
                for dx, dy in self.selected_shape.shape_data:
                    self.board[y + dy][x + dx] = 1
                    self.score += 1  # Увеличиваем счет на 1 за каждый установленный куб
                self.check_and_clear_lines_columns()
                self.available_shapes.remove(self.selected_shape)
                self.generate_new_shapes()

            self.selected_shape = None
            self.update()

        self.check_end()

    def can_place(self, x, y, shape: Shape) -> bool:
        if not (0 <= y < self.board_size):
            return False

        for dx, dy in shape.shape_data:
            if not (0 <= x + dx < self.board_size and 0 <= y + dy < self.board_size and self.board[y + dy][
                x + dx] == 0):
                return False

        return True

    def check_end(self):
        for shape in self.available_shapes:
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.can_place(i, j, shape):
                        return False
        self.end_game()

    def end_game(self):
        QMessageBox.about(self, "Конец игры!", f"Ваш счёт: {self.score}")
        self.restart()

    def restart(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.available_shapes.clear()
        self.selected_shape = None
        self.selected_shape_pos = None
        self.score = 0

        self.generate_new_shapes()

    def generate_new_shapes(self):
        # Проверка наличия выбранной фигуры
        if len(self.available_shapes) >= 3:
            return

        new_shapes = [
            Shape([(0, 0), (0, 1), (1, 0), (1, 1)]),  # квадрат2х2
            Shape([(0, 0), (0, 1), (1, 0), (1, 0)]),  # треугольник с основанием 2
            Shape([(0, 0), (0, 1), (0, 2)]),  # вертикальная палка на 3
            Shape([(0, 0), (1, 0), (2, 0), (2, 1)]),  # треугольник с основанием 3
            Shape([(0, 0), (1, 0), (2, 0), (1, 1)]),  # перевернутая т
            Shape([(0, 0), (1, 0), (1, 1), (2, 1)]),  # z
            Shape([(0, 0), (0, 1), (0, 2), (0, 3)]),  # вертикальная палка на 4
            Shape([(0, 0), (0, 1), (0, 2), (1, 1)]),  # перевернутая т
            Shape([(0, 0)])  # точка
        ]
        random.shuffle(new_shapes)
        while len(self.available_shapes) < 3:
            self.available_shapes.append(new_shapes.pop())

    def draw_score(self, painter):
        font = painter.font()
        font.setPointSize(20)
        painter.setFont(font)
        painter.drawText(430, 50, f"Score: {self.score}")

    def check_and_clear_lines_columns(self):
        lines_cleared = 0
        columns_cleared = 0
        for i in range(self.board_size):
            if all(cell != 0 for cell in self.board[i]):
                lines_cleared += 1
                for j in range(self.board_size):
                    self.board[i][j] = -1

        for j in range(self.board_size):
            if all(self.board[i][j] != 0 for i in range(self.board_size)):
                columns_cleared += 1
                for i in range(self.board_size):
                    self.board[i][j] = -1

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == -1:
                    self.board[i][j] = 0

        self.score += (
                                  lines_cleared + columns_cleared) * self.board_size  # Увеличиваем счет на 10 баллов за каждую удаленную строку или столбец
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tetris = Tetris()
    sys.exit(app.exec_())
