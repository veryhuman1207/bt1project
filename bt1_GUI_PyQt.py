import sys
import os
import json
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QTabWidget, QMessageBox, QListWidget, QProgressBar,
    QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
import bt1module
import shutil
import tempfile

CONFIG_FILE = ".bt1config.json"

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"password": "test1", "salt": "", "dark_mode": False}

# Save configuration to file
def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

# List widget for dragging and dropping files
class DropListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.addItem(path)

# Main GUI class
class BT1GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BT1 GUI PyQt V2")
        self.resize(700, 500)
        self.config = load_config()
        self.initUI()

    # Initialize the UI components
    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Tabs for different sections
        self.tab_pack = QWidget()
        self.tab_unpack = QWidget()
        self.tab_settings = QWidget()

        self.tabs.addTab(self.tab_pack, "📦 Pack Files")
        self.tabs.addTab(self.tab_unpack, "🧹 Unpack")
        self.tabs.addTab(self.tab_settings, "⚙️ Settings")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.init_pack_tab()
        self.init_unpack_tab()
        self.init_settings_tab()

    # Initialize the "Pack Files" tab
    def init_pack_tab(self):
        layout = QVBoxLayout()

        self.file_list = DropListWidget()
        btn_add_files = QPushButton("➕ Add Files")
        btn_add_files.clicked.connect(self.add_files)
        btn_clear = QPushButton("🗑 Clear List")
        btn_clear.clicked.connect(lambda: self.file_list.clear())

        layout.addWidget(QLabel("📂 Drag and drop or select multiple files to pack:"))
        layout.addWidget(self.file_list)

        # Layout for buttons
        h1 = QHBoxLayout()
        h1.addWidget(btn_add_files)
        h1.addWidget(btn_clear)
        layout.addLayout(h1)

        # Output file path
        self.outfile_entry = QLineEdit()
        btn_browse_out = QPushButton("💾 Save As")
        btn_browse_out.clicked.connect(self.select_output_file)

        h2 = QHBoxLayout()
        h2.addWidget(self.outfile_entry)
        h2.addWidget(btn_browse_out)
        layout.addLayout(h2)

        # Progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Pack button
        btn_pack = QPushButton("🚀 Pack")
        btn_pack.clicked.connect(self.pack_files)
        layout.addWidget(btn_pack)

        self.tab_pack.setLayout(layout)

    # Add files to list
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for f in files:
            self.file_list.addItem(f)

    # Select the output file for packing
    def select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", filter="BT1 Files (*.bt1)")
        if path:
            self.outfile_entry.setText(path)

    # Pack the selected files
    def pack_files(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not files:
            return QMessageBox.warning(self, "Error", "No files to pack.")

        output = self.outfile_entry.text()
        if not output:
            return QMessageBox.warning(self, "Error", "Output file not selected.")

        self.progress.setValue(10)

        # Create a temporary ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmpzip:
            with zipfile.ZipFile(tmpzip.name, "w") as zf:
                for file in files:
                    zf.write(file, arcname=os.path.basename(file))
        self.progress.setValue(30)

        # Pack files using the BT1 module
        try:
            bt1module.bt1_pack_file(tmpzip.name, output, self.config["password"])
            self.progress.setValue(100)
            QMessageBox.information(self, "Done", f"Packed into: {output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Initialize the "Unpack" tab
    def init_unpack_tab(self):
        layout = QVBoxLayout()

        self.unpack_input = QLineEdit()
        btn_browse = QPushButton("📂 Select .bt1 File")
        btn_browse.clicked.connect(lambda: self.browse_file(self.unpack_input))

        h1 = QHBoxLayout()
        h1.addWidget(self.unpack_input)
        h1.addWidget(btn_browse)
        layout.addLayout(h1)

        self.unpack_outdir = QLineEdit()
        btn_outdir = QPushButton("🗃 Output Directory")
        btn_outdir.clicked.connect(lambda: self.browse_folder(self.unpack_outdir))

        h2 = QHBoxLayout()
        h2.addWidget(self.unpack_outdir)
        h2.addWidget(btn_outdir)
        layout.addLayout(h2)

        # Unpack progress bar
        self.unpack_progress = QProgressBar()
        layout.addWidget(self.unpack_progress)

        # Unpack button
        btn_unpack = QPushButton("🔓 Unpack")
        btn_unpack.clicked.connect(self.unpack_file)
        layout.addWidget(btn_unpack)

        self.tab_unpack.setLayout(layout)

    # Unpack the selected file
    def unpack_file(self):
        infile = self.unpack_input.text()
        outdir = self.unpack_outdir.text()

        if not os.path.isfile(infile):
            return QMessageBox.warning(self, "Error", "The .bt1 file does not exist.")
        if not os.path.isdir(outdir):
            return QMessageBox.warning(self, "Error", "Invalid output directory.")

        try:
            self.unpack_progress.setValue(10)
            bt1module.bt1_unpack_file(infile, outdir, self.config["password"])
            self.unpack_progress.setValue(100)
            QMessageBox.information(self, "Done", f"Unpacked to: {outdir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Initialize the "Settings" tab
    def init_settings_tab(self):
        layout = QVBoxLayout()

        # Settings form: password, salt, dark mode
        self.pass_input = QLineEdit(self.config.get("password", ""))
        self.salt_input = QLineEdit(self.config.get("salt", ""))
        self.dark_check = QCheckBox("🌙 Enable Dark Mode")
        self.dark_check.setChecked(self.config.get("dark_mode", False))

        # Save and reset buttons
        btn_save = QPushButton("📀 Save Settings")
        btn_save.clicked.connect(self.save_settings)

        btn_reset = QPushButton("🔄 Reset to Default")
        btn_reset.clicked.connect(self.reset_settings)

        layout.addWidget(QLabel("🔑 Password:"))
        layout.addWidget(self.pass_input)
        layout.addWidget(QLabel("🧂 Salt (hex):"))
        layout.addWidget(self.salt_input)
        layout.addWidget(self.dark_check)
        layout.addWidget(btn_save)
        layout.addWidget(btn_reset)

        self.tab_settings.setLayout(layout)

    # Browse for a file
    def browse_file(self, target):
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            target.setText(path)

    # Browse for a folder
    def browse_folder(self, target):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            target.setText(path)

    # Save settings to configuration
    def save_settings(self):
        self.config["password"] = self.pass_input.text()
        self.config["salt"] = self.salt_input.text()
        self.config["dark_mode"] = self.dark_check.isChecked()
        save_config(self.config)
        QMessageBox.information(self, "Done", "Settings saved.")

    # Reset settings to default values
    def reset_settings(self):
        self.pass_input.setText("test1")
        self.salt_input.setText("")
        self.dark_check.setChecked(False)
        self.save_settings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BT1GUI()
    win.show()

    # Apply dark mode stylesheet if enabled
    if win.config.get("dark_mode"):
        app.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #ffffff; font-size: 14px; }
            QPushButton { background-color: #444; color: #fff; border: 1px solid #555; padding: 5px; }
            QLineEdit { background-color: #3c3c3c; color: white; border: 1px solid #666; }
            QListWidget { background-color: #333; color: white; }
            QTabWidget::pane { border: 1px solid #444; }
        """)

    sys.exit(app.exec_())

