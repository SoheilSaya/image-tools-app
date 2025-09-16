import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QMessageBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyQt6.QtWidgets import QTabWidget, QSpinBox, QGroupBox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class ImageCropperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.cropped_image = None
        self.input_file_path = ""
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Image Cropper - 34mm x 34mm")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Image Cropper to 34mm x 34mm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Input section
        input_group = QGroupBox("Input Image")
        input_layout = QVBoxLayout(input_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.select_image)
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.select_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        input_layout.addLayout(file_layout)
        
        # DPI setting
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("Image DPI (for size calculation):"))
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(72)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(300)  # Default to 300 DPI
        self.dpi_spinbox.setSuffix(" DPI")
        dpi_layout.addWidget(self.dpi_spinbox)
        dpi_layout.addStretch()
        input_layout.addLayout(dpi_layout)
        
        main_layout.addWidget(input_group)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("No image loaded")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 2px dashed #ccc;")
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Process & Save (Image + PDF)")
        self.process_button.clicked.connect(self.process_and_save)
        self.process_button.setEnabled(False)
        
        button_layout.addWidget(self.process_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)
        
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.gif)"
        )
        
        if file_path:
            self.input_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.load_image(file_path)
            
    def load_image(self, file_path):
        try:
            self.original_image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')
            
            # Show preview
            self.show_preview(self.original_image, "Original Image")
            self.process_button.setEnabled(True)
            self.status_label.setText(f"Loaded: {self.original_image.size[0]}x{self.original_image.size[1]} pixels")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            
    def show_preview(self, pil_image, title="Preview"):
        # Convert PIL image to QPixmap for display
        # Create a copy and resize for preview
        preview_image = pil_image.copy()
        
        # Calculate preview size (max 400x400)
        max_size = 400
        ratio = min(max_size / preview_image.width, max_size / preview_image.height)
        new_size = (int(preview_image.width * ratio), int(preview_image.height * ratio))
        preview_image = preview_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to QPixmap
        preview_image.save('temp_preview.png')
        pixmap = QPixmap('temp_preview.png')
        self.preview_label.setPixmap(pixmap)
        
        # Clean up temp file
        try:
            os.remove('temp_preview.png')
        except:
            pass
    def process_and_save(self):
        if not self.original_image:
            return
            
        # Get save directory
        save_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if not save_dir:
            return
            
        try:
            dpi = self.dpi_spinbox.value()
            
            # Calculate 34mm in pixels at given DPI
            mm_to_inch = 1 / 25.4
            size_in_inches = 34 * mm_to_inch
            size_in_pixels = int(size_in_inches * dpi)
            
            # Get original image dimensions
            original_width, original_height = self.original_image.size
            
            # Calculate crop box for center crop
            left = (original_width - size_in_pixels) // 2
            top = (original_height - size_in_pixels) // 2
            right = left + size_in_pixels
            bottom = top + size_in_pixels
            
            # Check if the image is large enough
            if left < 0 or top < 0 or right > original_width or bottom > original_height:
                # If image is too small, resize it first
                scale_factor = max(
                    size_in_pixels / original_width,
                    size_in_pixels / original_height
                )
                
                new_width = int(original_width * scale_factor * 1.1)  # Add 10% margin
                new_height = int(original_height * scale_factor * 1.1)
                
                resized_image = self.original_image.resize(
                    (new_width, new_height), 
                    Image.Resampling.LANCZOS
                )
                
                # Recalculate crop box
                left = (new_width - size_in_pixels) // 2
                top = (new_height - size_in_pixels) // 2
                right = left + size_in_pixels
                bottom = top + size_in_pixels
                
                self.cropped_image = resized_image.crop((left, top, right, bottom))
            else:
                self.cropped_image = self.original_image.crop((left, top, right, bottom))
            
            # Show cropped preview
            self.show_preview(self.cropped_image, "Cropped Image (34mm x 34mm)")
            
            # Generate base filename
            base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
            
            # Save as PNG
            image_path = os.path.join(save_dir, f"{base_name}_34mm.png")
            self.cropped_image.save(image_path, quality=95)
            
            # Save as PDF (34mm x 34mm page size)
            pdf_path = os.path.join(save_dir, f"{base_name}_34mm.pdf")
            
            # Create PDF with 34mm x 34mm page size
            page_size = (34 * mm, 34 * mm)  # 34mm x 34mm
            c = canvas.Canvas(pdf_path, pagesize=page_size)
            
            # Save cropped image to temporary file
            temp_image_path = "temp_for_pdf.png"
            self.cropped_image.save(temp_image_path)
            
            # Draw the image to fill the entire PDF page (34mm x 34mm)
            c.drawImage(temp_image_path, 0, 0, width=34*mm, height=34*mm)
            
            c.save()
            
            # Clean up temp file
            try:
                os.remove(temp_image_path)
            except:
                pass
            
            self.status_label.setText(f"Saved: {image_path} and {pdf_path}")
            QMessageBox.information(self, "Success", f"Files saved successfully:\n{image_path}\n{pdf_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process and save: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = ImageCropperApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()