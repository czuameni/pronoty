from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QMessageBox,
    QMenu, QAbstractItemView, QListWidgetItem, QComboBox
)
from PySide6.QtCore import QTimer, Qt


class MainWindow(QMainWindow):
    def __init__(self, notes_manager):
        super().__init__()
        self.notes_manager = notes_manager

        self.setWindowTitle("Pronoty")
        self.resize(1200, 800)

        self.filtered_notes = None
        self.current_note_id = None
        self.is_loading = False

        self.init_ui()
        self.load_notes()

    def init_ui(self):
        central = QWidget()
        layout = QHBoxLayout()

        # sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(["All Notes", "Work", "Private"])
        self.sidebar.setFixedWidth(120)
        self.sidebar.clicked.connect(self.filter_by_category)

        # list
        self.notes_list = QListWidget()
        self.notes_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.notes_list.clicked.connect(self.display_note)
        self.notes_list.itemChanged.connect(self.handle_rename)
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.open_context_menu)

        # buttons
        self.new_btn = QPushButton("New Note")
        self.new_btn.clicked.connect(self.create_note)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_note)

        # editor
        self.editor = QTextEdit()
        self.title_input = QLineEdit()
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["All Notes", "Work", "Private"])
        self.category_dropdown.currentTextChanged.connect(self.change_category)

        # autosave
        self.save_timer = QTimer()
        self.save_timer.setInterval(1500)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        self.editor.textChanged.connect(self.trigger_autosave)
        self.title_input.textChanged.connect(self.trigger_autosave)

        # search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.search_notes)

        # layout
        left = QVBoxLayout()

        btns = QHBoxLayout()
        btns.addWidget(self.new_btn)
        btns.addWidget(self.delete_btn)

        left.addLayout(btns)
        left.addWidget(self.search)
        left.addWidget(self.notes_list)

        top = QHBoxLayout()
        top.addWidget(self.title_input)
        top.addWidget(self.category_dropdown)

        right = QVBoxLayout()
        right.addLayout(top)
        right.addWidget(self.editor)

        layout.addWidget(self.sidebar)
        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        central.setLayout(layout)
        self.setCentralWidget(central)

    # -------------------------
    # DATA / LIST
    # -------------------------

    def populate_list(self, notes):
        self.notes_list.clear()

        for n in notes:
            title = n["title"]
            if n.get("pinned"):
                title = "⭐ " + title

            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, n["id"])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.notes_list.addItem(item)

    def load_notes(self):
        self.notes = self.notes_manager.get_notes()
        self.populate_list(self.notes)

    # -------------------------
    # DISPLAY
    # -------------------------

    def display_note(self):
        item = self.notes_list.currentItem()
        if not item:
            return

        note_id = item.data(Qt.UserRole)
        note = next((n for n in self.notes if n["id"] == note_id), None)
        if not note:
            return

        self.is_loading = True

        self.current_note_id = note["id"]
        self.title_input.setText(note["title"])
        self.category_dropdown.setCurrentText(note["category"])
        self.editor.setText(note["content"])

        self.is_loading = False

    # -------------------------
    # CREATE
    # -------------------------

    def create_note(self):
        category = "default"

        selected = self.sidebar.currentItem()
        if selected and selected.text() != "All Notes":
            category = selected.text()

        self.notes_manager.create_note("New Note", "", category)

        self.load_notes()

        last = self.notes_list.count() - 1
        if last >= 0:
            self.notes_list.setCurrentRow(last)
            self.display_note()

    # -------------------------
    # AUTOSAVE
    # -------------------------

    def trigger_autosave(self):
        if self.is_loading or self.current_note_id is None:
            return
        self.save_timer.start()

    def auto_save(self):
        if self.is_loading or self.current_note_id is None:
            return

        note = next((n for n in self.notes if n["id"] == self.current_note_id), None)
        if not note:
            return

        title = self.title_input.text()
        content = self.editor.toPlainText()
        category = self.category_dropdown.currentText()

        self.notes_manager.update_note(note["id"], title, content, category)

        note["title"] = title
        note["content"] = content
        note["category"] = category

        item = self.notes_list.currentItem()
        if item:
            item.setText(title)

    # -------------------------
    # SEARCH / FILTER
    # -------------------------

    def search_notes(self, text):
        if not text:
            self.filtered_notes = None
            self.populate_list(self.notes)
            return

        notes = [
            n for n in self.notes
            if text.lower() in n["title"].lower()
            or text.lower() in n["content"].lower()
        ]

        self.filtered_notes = notes
        self.populate_list(notes)

    def filter_by_category(self):
        selected = self.sidebar.currentItem().text()

        if selected == "All Notes":
            self.filtered_notes = None
            self.populate_list(self.notes)
            return

        notes = [n for n in self.notes if n["category"] == selected]
        self.filtered_notes = notes
        self.populate_list(notes)

    # -------------------------
    # DELETE
    # -------------------------

    def delete_note(self):
        if self.current_note_id is None:
            return

        reply = QMessageBox.question(
            self, "Delete", "Delete note?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.notes_manager.delete_note(self.current_note_id)
        self.current_note_id = None

        self.load_notes()
        self.editor.clear()
        self.title_input.clear()

    # -------------------------
    # CONTEXT MENU
    # -------------------------

    def open_context_menu(self, pos):
        item = self.notes_list.itemAt(pos)
        if not item:
            return

        note_id = item.data(Qt.UserRole)
        note = next((n for n in self.notes if n["id"] == note_id), None)
        if not note:
            return

        menu = QMenu()

        pin_text = "Unpin" if note.get("pinned") else "Pin"
        pin = menu.addAction(pin_text)
        rename = menu.addAction("Rename")
        delete = menu.addAction("Delete")

        action = menu.exec(self.notes_list.mapToGlobal(pos))

        if action == pin:
            self.notes_manager.toggle_pin(note["id"], note.get("pinned"))
            self.load_notes()

        elif action == rename:
            self.notes_list.editItem(item)

        elif action == delete:
            self.delete_note()

    # -------------------------
    # RENAME
    # -------------------------

    def handle_rename(self, item):
        note_id = item.data(Qt.UserRole)
        note = next((n for n in self.notes if n["id"] == note_id), None)
        if not note:
            return

        new_title = item.text()

        self.notes_manager.update_note(
            note["id"],
            new_title,
            note["content"],
            note["category"]
        )

        note["title"] = new_title

    # -------------------------
    # CATEGORY CHANGE
    # -------------------------

    def change_category(self, category):
        if self.current_note_id is None:
            return

        note = next((n for n in self.notes if n["id"] == self.current_note_id), None)
        if not note:
            return

        self.notes_manager.update_note(
            note["id"],
            note["title"],
            note["content"],
            category
        )

        note["category"] = category