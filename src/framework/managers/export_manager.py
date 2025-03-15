from PyQt5.QtCore import Qt, QRectF, QUrl, QSizeF
from PyQt5.QtGui import QBrush, QColor, QImage, QPainter, QDesktopServices
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QGraphicsScene
from src.framework.items import CanvasItem
from src.gui.app_screens import CanvasItemSelector
from src.scripts.app_internal import supported_file_exporting, filter_extensions


class ExportManager:
    def __init__(self, canvas: QGraphicsScene):
        self.canvas = canvas

    def normalExport(self):
        # Exit add canvas tool if active
        self.canvas.parentWindow.use_exit_add_canvas()
        self.canvas.parentWindow.select_btn.trigger()

        # Create a custom dialog to with a dropdown to select which canvas to export
        selector = CanvasItemSelector(self.canvas, self.canvas.parentWindow)
        selector.show()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                # Add the canvas items to the selector
                selector.add_canvas_item(itemName=item.toolTip(), itemKey=item)

        # Create a function to choose the selected item
        def export():
            index = selector.canvas_chooser_combo.currentIndex()
            selected_item = selector.canvas_chooser_combo.itemData(index)

            if selected_item:
                if selector.transparent_check_btn.isChecked():
                    self.canvas.setBackgroundBrush(QBrush(QColor(Qt.transparent)))

                    for item in self.canvas.items():
                        if isinstance(item, CanvasItem):
                            item.setTransparentMode()

                self.filterSelectedCanvasForExport(selected_item)

            else:
                QMessageBox.warning(self.canvas.parentWindow,
                                    'Export Selected Canvas',
                                    'No canvas elements found within the scene. '
                                    'Please create a canvas element to export.',
                                    QMessageBox.Ok)

        selector.export_btn.clicked.connect(export)

    def exportAsBitmap(self, filename, selected_item):
        # Create a QImage with the size of the selected item (QGraphicsRectItem)
        rect = selected_item.sceneBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        print(rect)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        try:
            # Save the image to file
            success = image.save(filename)

            if success:
                self.show_export_finished()

                # Open the image with the default image viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

        except Exception as e:
            # If saving failed, show an error notification
            QMessageBox.critical(self.canvas.parentWindow, "Export Error", f"Failed to export canvas to file: {e}")

    def exportAsSVG(self, file_path, selected_item):
        try:
            # Get the bounding rect
            rect = selected_item.sceneBoundingRect()

            # Export as SVG
            svg_generator = QSvgGenerator()
            svg_generator.setFileName(file_path)
            svg_generator.setSize(rect.size().toSize())
            svg_generator.setViewBox(rect)

            # Clear selection
            self.canvas.clearSelection()

            # Create a QPainter to paint onto the QSvgGenerator
            painter = QPainter()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.begin(svg_generator)

            # Render the scene onto the QPainter
            self.canvas.render(painter, target=rect, source=rect)

            # End painting
            painter.end()

            self.show_export_finished()

            # Open the image with the default image viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

        except Exception as e:
            # Show export error notification
            QMessageBox.information(self.canvas.parentWindow, 'Export Failed', f'Export failed: {e}',
                                    QMessageBox.Ok)

    def exportAsPDF(self, file_path, selected_item):
        try:
            # Get the bounding rect of the selected item
            bounding_rect = selected_item.sceneBoundingRect()

            # Configure the printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            # Adjust the printer's page size to match the bounding rect
            printer.setPageSizeMM(QSizeF(bounding_rect.width(), bounding_rect.height()))

            # Start painting
            painter = QPainter()
            painter.begin(printer)

            # Translate painter to the bounding rect top-left
            painter.translate(-bounding_rect.topLeft())

            # Render the selected item
            self.canvas.render(painter, QRectF(), bounding_rect)

            # End painting
            painter.end()

        except Exception as e:
            print(e)

        self.show_export_finished()

        # Open the PDF with the default viewer
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def filterSelectedCanvasForExport(self, selected_item):
        # File dialog, filepath
        file_dialog = QFileDialog()

        file_path, selected_filter = file_dialog.getSaveFileName(self.canvas.parentWindow, 'Export Canvas', '',
                                                                 supported_file_exporting)

        if file_path:
            selected_extension = filter_extensions.get(selected_filter, '.png')

            # Ensure the file_path has the selected extension
            if not file_path.endswith(selected_extension):
                file_path += selected_extension

            if selected_extension == '.svg':
                self.exportAsSVG(file_path, selected_item)

            elif selected_extension == '.pdf':
                self.exportAsPDF(file_path, selected_item)

            else:
                try:
                    self.canvas.clearSelection()
                    self.exportAsBitmap(file_path, selected_item)

                except Exception as e:
                    print(e)

            self.canvas.parentWindow.use_exit_add_canvas()

    def show_export_finished(self):
        self.canvas.views()[0].showMessage('Export', 'Export completed successfully.')
