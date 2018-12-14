from PyQt5.QtGui import QTextDocumentWriter

from MainWindowUi import Ui_MainWindow
from PyQt5.QtCore import QDate, pyqtSlot, QFile, qDebug, QTextStream, QByteArray
from PyQt5.QtWidgets import QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    DB_PATH = "db"
    FILE_NAME_PATTERN = "yyyy-MM-dd"
    FILE_FORMAT = "diary"

    def __init__(self):
        super().__init__()
        self.current_document_name = ""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.open_document(self.file_name_by_date(QDate.currentDate()))


    @pyqtSlot(QDate)
    def on_calendarView_clicked(self, date):
        self.open_document(self.file_name_by_date(date))

    def open_document(self, name):
        self.close_document()
        self.ui.documentView.clear()
        self.current_document_name = name
        if not QFile.exists(name):
            return
        reader = DocumentReader(name)
        reader.read(self.ui.documentView.document())
        if reader.is_error:
            QMessageBox.warning(self, "Ошибка",
                                "При попытке сохранить файл дневника произошла ошибка: " + reader.errorString)

    def close_document(self):
        qDebug("MainWindow.close_document()")
        qDebug("self.current_document_name is \"" + self.current_document_name + "\"")
        if len(self.current_document_name) == 0:
            qDebug("file not opened. finished")
            return
        doc = self.ui.documentView.document()
        if doc.isEmpty():
            qDebug("document is empty. finished")
            self.current_document_name = ""
            return
        qDebug("writing document")
        writer = DocumentWriter(self.current_document_name)
        writer.write(doc)
        if writer.is_error:
            QMessageBox.warning(self, "Ошибка",
                                "При попытке сохранить файл дневника произошла ошибка: " + writer.errorString)

    def file_name_by_date(self, date):
        return self.DB_PATH + "/" + date.toString(self.FILE_NAME_PATTERN) + "." + self.FILE_FORMAT


class DocumentWriter:
    def __init__(self, filename):
        self.file = QFile()
        self.file.setFileName(filename)
        self.is_error = False
        self.errorString = ""
        if not self.file.open(QFile.WriteOnly):
            error = self.file.errorString()
            qDebug("cannot open file \"{1}\"".format(error))
            self.is_error = True
            self.errorString = error

    def write(self, document):
        if not self.file.isOpen():
            return
        writer = QTextDocumentWriter()
        writer.setFormat(QByteArray().append("plaintext"))
        writer.setDevice(self.file)
        writer.write(document)


class DocumentReader:
    def __init__(self, filename):
        self.file = QFile()
        self.file.setFileName(filename)
        self.is_error = False
        self.errorString = ""
        if not self.file.open(QFile.ReadOnly):
            error = self.file.errorString()
            qDebug("cannot open file \"{1}\"".format(error))
            self.is_error = True
            self.errorString = error

    def read(self, document):
        if not self.file.isOpen():
            return
        text = str(self.file.readAll().data(), encoding='utf-8')
        document.setPlainText(text)

