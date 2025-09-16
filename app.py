#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import QTabWidget, QSpinBox, QGroupBox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                                QPushButton, QTextEdit, QFrame, QFileDialog, 
                                QMessageBox, QGroupBox, QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QPalette, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("❌ PyQt6 not found. Install with: pip install PyQt6")

class ImageCropperWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.cropped_image = None
        self.input_file_path = ""
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Image Cropper to 34mm x 34mm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Input section
        input_group = QGroupBox("تصویر ورودی")
        input_layout = QVBoxLayout(input_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.select_button = QPushButton("انتخاب تصویر")
        self.select_button.clicked.connect(self.select_image)
        self.file_label = QLabel("فایلی انتخاب نشده")
        file_layout.addWidget(self.select_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        input_layout.addLayout(file_layout)
        
        # DPI setting
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("Image DPI (برای محاسبه اندازه):"))
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(72)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(300)
        self.dpi_spinbox.setSuffix(" DPI")
        dpi_layout.addWidget(self.dpi_spinbox)
        dpi_layout.addStretch()
        input_layout.addLayout(dpi_layout)
        
        main_layout.addWidget(input_group)
        
        # Preview section
        preview_group = QGroupBox("پیش نمایش")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("تصویری لود نشده")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 2px dashed #ccc;")
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("پردازش و ذخیره")
        self.process_button.clicked.connect(self.process_and_save)
        self.process_button.setEnabled(False)
        
        button_layout.addWidget(self.process_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("آماده")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.gif *jfif)"
        )
        
        if file_path:
            self.input_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.load_image(file_path)
            
    def load_image(self, file_path):
        try:
            self.original_image = Image.open(file_path)
            
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')
            
            self.show_preview(self.original_image, "Original Image")
            self.process_button.setEnabled(True)
            self.status_label.setText(f"Loaded: {self.original_image.size[0]}x{self.original_image.size[1]} pixels")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            
    def show_preview(self, pil_image, title="Preview"):
        preview_image = pil_image.copy()
        
        max_size = 400
        ratio = min(max_size / preview_image.width, max_size / preview_image.height)
        new_size = (int(preview_image.width * ratio), int(preview_image.height * ratio))
        preview_image = preview_image.resize(new_size, Image.Resampling.LANCZOS)
        
        preview_image.save('temp_preview.png')
        pixmap = QPixmap('temp_preview.png')
        self.preview_label.setPixmap(pixmap)
        
        try:
            os.remove('temp_preview.png')
        except:
            pass
    
    def process_and_save(self):
        if not self.original_image:
            return
            
        save_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if not save_dir:
            return
            
        try:
            dpi = self.dpi_spinbox.value()
            
            mm_to_inch = 1 / 25.4
            size_in_inches = 34 * mm_to_inch
            size_in_pixels = int(size_in_inches * dpi)
            
            original_width, original_height = self.original_image.size
            
            left = (original_width - size_in_pixels) // 2
            top = (original_height - size_in_pixels) // 2
            right = left + size_in_pixels
            bottom = top + size_in_pixels
            
            if left < 0 or top < 0 or right > original_width or bottom > original_height:
                scale_factor = max(
                    size_in_pixels / original_width,
                    size_in_pixels / original_height
                )
                
                new_width = int(original_width * scale_factor * 1.1)
                new_height = int(original_height * scale_factor * 1.1)
                
                resized_image = self.original_image.resize(
                    (new_width, new_height), 
                    Image.Resampling.LANCZOS
                )
                
                left = (new_width - size_in_pixels) // 2
                top = (new_height - size_in_pixels) // 2
                right = left + size_in_pixels
                bottom = top + size_in_pixels
                
                self.cropped_image = resized_image.crop((left, top, right, bottom))
            else:
                self.cropped_image = self.original_image.crop((left, top, right, bottom))
            
            self.show_preview(self.cropped_image, "Cropped Image (34mm x 34mm)")
            
            base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
            
            image_path = os.path.join(save_dir, f"{base_name}_34mm.png")
            self.cropped_image.save(image_path, quality=95)
            
            pdf_path = os.path.join(save_dir, f"{base_name}_34mm.pdf")
            
            page_size = (34 * mm, 34 * mm)
            c = canvas.Canvas(pdf_path, pagesize=page_size)
            
            temp_image_path = "temp_for_pdf.png"
            self.cropped_image.save(temp_image_path)
            
            c.drawImage(temp_image_path, 0, 0, width=34*mm, height=34*mm)
            
            c.save()
            
            try:
                os.remove(temp_image_path)
            except:
                pass
            
            self.status_label.setText(f"Saved: {image_path} and {pdf_path}")
            QMessageBox.information(self, "Success", f"Files saved successfully:\n{image_path}\n{pdf_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process and save: {str(e)}")

class AddressLabelWidget(QWidget):  # Change from QMainWindow to QWidget
    def __init__(self):
        super().__init__()
        
        # اطلاعات ثابت فرستنده
        self.sender_info = [
            "شرکت هوش مصنوعی اندیشمندان برتر",
            "شیراز،شهرک آرین بلوار سفیر امید ۲، کوچه ۲/۶",
            "۷۱۴۵۶۸۳۲۱۰",
            "۰۲۱۹۱۰۹۱۷۲۲"
        ]
        
        self.init_ui()
        self.load_sample_data()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        # Remove these lines since we're now a widget:
        # self.setWindowTitle("🏷️ تولیدکننده برچسب پستی حرارتی - NokhbehSho.com")
        # self.setGeometry(200, 200, 800, 700)
        
        # تنظیم فونت برای پشتیبانی از فارسی
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.setFont(font)
        
        # لایه‌بندی اصلی - change from central_widget to self
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # هدر
        self.create_header(main_layout)
        
        # بخش فرستنده
        self.create_sender_section(main_layout)
        
        # بخش گیرنده
        self.create_receiver_section(main_layout)
        
        # دکمه‌های کنترل
        self.create_control_buttons(main_layout)
        
        # فوتر
        self.create_footer(main_layout)
        
        # اعمال استایل
        self.apply_styles()
    
    def create_header(self, layout):
        """ایجاد هدر"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_frame.setFixedHeight(80)
        
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("🏷️ تولیدکننده برچسب پستی حرارتی")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        header_layout.addWidget(title_label)
        layout.addWidget(header_frame)
    
    def create_sender_section(self, layout):
        """ایجاد بخش فرستنده"""
        sender_group = QGroupBox("📤 اطلاعات فرستنده (ثابت)")
        sender_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        sender_layout = QVBoxLayout(sender_group)
        
        # نمایش اطلاعات فرستنده
        sender_text = QTextEdit()
        sender_text.setReadOnly(True)
        sender_text.setMaximumHeight(100)
        
        sender_info_text = f"""
نام: {self.sender_info[0]}
آدرس: {self.sender_info[1]}
کدپستی: {self.sender_info[2]}  |  تلفن: {self.sender_info[3]}
        """.strip()
        
        sender_text.setPlainText(sender_info_text)
        sender_text.setStyleSheet("""
            QTextEdit {
                background-color: #bdc3c7;
                color: #2c3e50;
                border: 1px solid #95a5a6;
                border-radius: 5px;
                padding: 10px;
                font-size: 17px;
            }
        """)
        
        sender_layout.addWidget(sender_text)
        layout.addWidget(sender_group)
    
    def create_receiver_section(self, layout):
        """ایجاد بخش گیرنده"""
        receiver_group = QGroupBox("📥 اطلاعات گیرنده (قابل ویرایش)")
        receiver_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #27ae60;
                background-color: #e8f5e8;
                border: 2px solid #27ae60;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        receiver_layout = QGridLayout(receiver_group)
        receiver_layout.setSpacing(10)
        
        # تعریف فیلدها - حذف آدرس خط دوم
        fields = [
            ("نام گیرنده:", "receiver_name"),
            ("آدرس:", "receiver_address"),
            ("کدپستی:", "receiver_postal"),
            ("تلفن:", "receiver_phone")
        ]
        
        self.receiver_entries = {}
        
        for row, (label_text, field_name) in enumerate(fields):
            # برچسب
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    font-weight: bold;
                    background: transparent;
                }
            """)
            
            # ورودی - برای آدرس از ورودی چندخطی استفاده می‌کنیم
            if field_name == "receiver_address":
                entry = QTextEdit()
                entry.setMaximumHeight(80)
                entry.setStyleSheet("""
                    QTextEdit {
                        padding: 8px;
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        font-size: 17px;
                        background-color: white;
                    }
                    QTextEdit:focus {
                        border: 2px solid #3498db;
                    }
                """)
            else:
                entry = QLineEdit()
                entry.setAlignment(Qt.AlignmentFlag.AlignRight)  # راست‌چین برای فارسی
                entry.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        font-size: 17px;
                        background-color: white;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3498db;
                    }
                """)
            
            receiver_layout.addWidget(label, row, 0)
            receiver_layout.addWidget(entry, row, 1)
            
            self.receiver_entries[field_name] = entry
        
        layout.addWidget(receiver_group)
    
    def create_control_buttons(self, layout):
        """ایجاد دکمه‌های کنترل"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        # تعریف دکمه‌ها
        buttons = [
            ("🔍 پیش‌نمایش برچسب", "#3498db", self.preview_label),
            ("🏷️ تولید برچسب", "#27ae60", self.generate_label),
            ("🗑️ پاک کردن فیلدها", "#e74c3c", self.clear_fields),
            ("💾 ذخیره به فایل", "#8e44ad", self.save_to_file)
        ]
        
        for button_text, color, callback in buttons:
            btn = QPushButton(button_text)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(150)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 15px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 0.3)};
                }}
            """)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        
        layout.addWidget(button_frame)
    
    def create_footer(self, layout):
        """ایجاد فوتر"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        footer_frame.setFixedHeight(60)
        
        footer_layout = QVBoxLayout(footer_frame)
        
        footer_label = QLabel("🌐 NokhbehSho.com | ☎️ 021-91091722 | مرجع تخصصی آموزش رباتیک و هوش مصنوعی")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                background: transparent;
            }
        """)
        
        footer_layout.addWidget(footer_label)
        layout.addWidget(footer_frame)
    
    def apply_styles(self):
        """اعمال استایل‌های کلی"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)
    
    def darken_color(self, color, factor=0.2):
        """تیره کردن رنگ برای حالت hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def load_sample_data(self):
        """بارگذاری داده‌های نمونه"""
        sample_data = {
            "receiver_name": "علی رضا شجاع",
            "receiver_address": "گناوه خیابان آزادی، پلاک ۱۲۳، واحد ۴",
            "receiver_postal": "۵۴۶۵۴۶۵۴۶۵",
            "receiver_phone": "۰۹۱۷۷۰۱۲۱۵۴"
        }
        
        for field_name, sample_value in sample_data.items():
            if field_name in self.receiver_entries:
                if field_name == "receiver_address":
                    self.receiver_entries[field_name].setPlainText(sample_value)
                else:
                    self.receiver_entries[field_name].setText(sample_value)
    
    def get_receiver_info(self):
        """دریافت اطلاعات گیرنده"""
        # برای آدرس از toPlainText() استفاده می‌کنیم
        address_text = self.receiver_entries["receiver_address"].toPlainText().strip()
        
        return [
            self.receiver_entries["receiver_name"].text().strip(),
            address_text,
            self.receiver_entries["receiver_postal"].text().strip(),
            self.receiver_entries["receiver_phone"].text().strip()
        ]
    
    def validate_fields(self):
        """اعتبارسنجی فیلدها"""
        receiver_info = self.get_receiver_info()
        
        if not receiver_info[0]:  # نام
            QMessageBox.warning(self, "خطا", "لطفاً نام گیرنده را وارد کنید.")
            return False
        
        if not receiver_info[1]:  # آدرس
            QMessageBox.warning(self, "خطا", "لطفاً آدرس گیرنده را وارد کنید.")
            return False
        
        if not receiver_info[2]:  # کدپستی
            QMessageBox.warning(self, "خطا", "لطفاً کدپستی را وارد کنید.")
            return False
        
        return True
    
    def preview_label(self):
        """پیش‌نمایش برچسب"""
        if not self.validate_fields():
            return
        
        try:
            receiver_info = self.get_receiver_info()
            img = self.create_address_label(self.sender_info, receiver_info, "preview_label.png")
            
            # نمایش تصویر
            img.show()
            QMessageBox.information(self, "موفقیت", "پیش‌نمایش برچسب نمایش داده شد!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد پیش‌نمایش:\n{str(e)}")
    
    def generate_label(self):
        """تولید برچسب نهایی"""
        if not self.validate_fields():
            return
        
        try:
            # انتخاب مکان ذخیره
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره برچسب",
                "",
                "PNG files (*.png);;PDF files (*.pdf);;All files (*.*)"
            )
            
            if not filename:
                return
            
            receiver_info = self.get_receiver_info()
            img = self.create_address_label(self.sender_info, receiver_info, filename)
            
            # ذخیره PDF نیز
            if filename.endswith('.png'):
                pdf_filename = filename.replace('.png', '.pdf')
                img.save(pdf_filename, "PDF", resolution=300.0)
                success_msg = f"برچسب با موفقیت ذخیره شد!\n\nفایل‌های ایجاد شده:\n- {filename}\n- {pdf_filename}"
                QMessageBox.information(self, "موفقیت", success_msg)
            else:
                success_msg = f"برچسب با موفقیت در {filename} ذخیره شد!"
                QMessageBox.information(self, "موفقیت", success_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید برچسب:\n{str(e)}")
    
    def clear_fields(self):
        """پاک کردن تمام فیلدها"""
        reply = QMessageBox.question(
            self, 
            "تأیید", 
            "آیا مطمئن هستید که می‌خواهید تمام فیلدها را پاک کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for field_name, entry in self.receiver_entries.items():
                if field_name == "receiver_address":
                    entry.clear()  # برای QTextEdit
                else:
                    entry.clear()  # برای QLineEdit
    
    def save_to_file(self):
        """ذخیره اطلاعات در فایل متنی"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره اطلاعات گیرنده",
                "",
                "Text files (*.txt);;All files (*.*)"
            )
            
            if not filename:
                return
            
            receiver_info = self.get_receiver_info()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("اطلاعات گیرنده:\n")
                f.write("=" * 30 + "\n")
                f.write(f"نام: {receiver_info[0]}\n")
                f.write(f"آدرس: {receiver_info[1]}\n")
                f.write(f"کدپستی: {receiver_info[2]}\n")
                f.write(f"تلفن: {receiver_info[3]}\n")
            
            QMessageBox.information(self, "موفقیت", f"اطلاعات در {filename} ذخیره شد!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل:\n{str(e)}")
    
    def wrap_text(self, draw, text, font, max_width):
        """تابع برای تقسیم متن طولانی به چند خط"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # تست اضافه کردن کلمه به خط فعلی
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                # اگر خط فعلی خالی نیست، آن را اضافه کن و خط جدید شروع کن
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # اگر حتی یک کلمه هم در عرض نمی‌گنجد، آن را اضافه کن
                    lines.append(word)
        
        # خط آخر را اضافه کن
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def create_address_label(self, sender_info, receiver_info, output_filename="address_label.png"):
        """تابع ایجاد برچسب آدرس - بروزرسانی شده برای آدرس تکی"""
        
        # تنظیمات اندازه (8cm x 5cm در 300 DPI)
        width = 945
        height = 591
        
        # رنگ‌ها - برای Grayscale
        white = 255
        black = 0
        gray = 100
        light_gray = 220
        dark_gray = 60
        
        # ایجاد تصویر
        img = Image.new('L', (width, height), white)
        draw = ImageDraw.Draw(img)
        
        # تلاش برای بارگذاری فونت‌های فارسی
        font_loaded = False
        try:
            font_paths = [
                "Vazir-Bold.ttf",
                "Vazir-Medium.ttf", 
                "Vazir.ttf",
                "Sahel-Bold.ttf",
                "Sahel.ttf",
                "IRANSans.ttf",
                "B Nazanin.ttf",
                "Yekan.ttf"
            ]
            
            font_file = None
            bold_font = None
            for path in font_paths:
                if os.path.exists(path):
                    if "Bold" in path and not bold_font:
                        bold_font = path
                    if not font_file:
                        font_file = path
            
            if not font_file:
                raise Exception("فونت فارسی یافت نشد")
                
            # استفاده از فونت Bold برای عناوین اگر موجود بود
            title_font_file = bold_font if bold_font else font_file
            
            # بارگذاری فونت‌ها با اندازه‌های مناسب
            font_title = ImageFont.truetype(title_font_file, 42)
            font_label = ImageFont.truetype(title_font_file, 30)
            font_main = ImageFont.truetype(font_file, 35)
            font_info = ImageFont.truetype(font_file, 36)
            font_website = ImageFont.truetype(title_font_file, 24)
            font_phone = ImageFont.truetype(font_file, 22)
            font_tiny = ImageFont.truetype(font_file, 18)
            
            font_loaded = True
            
        except Exception as e:
            font_title = ImageFont.load_default()
            font_label = ImageFont.load_default()
            font_main = ImageFont.load_default()
            font_info = ImageFont.load_default()
            font_website = ImageFont.load_default()
            font_phone = ImageFont.load_default()
            font_tiny = ImageFont.load_default()
        
        # کادر اصلی با گوشه‌های گرد و ضخامت بیشتر
        draw.rounded_rectangle(
            [(10, 10), (width-10, height-10)],
            radius=20,
            outline=black,
            width=4
        )
        
        # ================== هدر ==================
        header_height = 75
        
        # کادر هدر با پس‌زمینه خاکستری روشن
        draw.rounded_rectangle(
            [(10, 10), (width-10, header_height)],
            radius=20,
            fill=light_gray,
            outline=None
        )
        # مستطیل پایین برای گوشه‌های تیز
        draw.rectangle(
            [(10, header_height-20), (width-10, header_height)],
            fill=light_gray,
            outline=None
        )
        
        # خط زیر هدر
        draw.line([(10, header_height), (width-10, header_height)], fill=black, width=3)
        
        # عنوان در وسط هدر
        title_text = "برچسب پستی"
        bbox = draw.textbbox((0, 0), title_text, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (header_height - text_height) // 2 - 5
        draw.text((x, y), title_text, black, font=font_title)
        
        # ================== بخش فرستنده (ردیف بالا) ==================
        section1_start = header_height + 20
        
        # کادر عنوان فرستنده - سمت چپ با ارتفاع بیشتر
        label_width = 140
        label_height = 50
        label_x = 50
        label_y = section1_start
        
        # سایه برای کادر
        draw.rounded_rectangle(
            [(label_x+3, label_y+3), (label_x + label_width+3, label_y + label_height+3)],
            radius=10,
            fill=gray,
            outline=None
        )
        # کادر اصلی
        draw.rounded_rectangle(
            [(label_x, label_y), (label_x + label_width, label_y + label_height)],
            radius=10,
            fill=dark_gray,
            outline=black,
            width=2
        )
        
        # متن فرستنده - بالاتر در کادر
        sender_label_text = "فرستنده"
        bbox = draw.textbbox((0, 0), sender_label_text, font=font_label)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_label = label_x + (label_width - text_width) // 2
        y_label = label_y + (label_height - text_height) // 2 - 3
        draw.text((x_label, y_label), sender_label_text, white, font=font_label)
        
        # اطلاعات فرستنده - راست چین
        right_margin = 60
        info_y = section1_start + 5
        max_text_width = width - right_margin - 220  # فضای در نظر گرفته شده برای متن
        
        # نام - راست چین
        text = f"نام: {sender_info[0]}"
        bbox = draw.textbbox((0, 0), text, font=font_main)
        text_width = bbox[2] - bbox[0]
        draw.text((width - right_margin - text_width, info_y), text, black, font=font_main)
        info_y += 35
        
        # آدرس - راست چین (تکی)
        text = f"آدرس: {sender_info[1]}"
        bbox = draw.textbbox((0, 0), text, font=font_info)
        text_width = bbox[2] - bbox[0]
        draw.text((width - right_margin - text_width, info_y), text, black, font=font_info)
        info_y += 35
        
        # کدپستی و تلفن - راست چین
        text = f"کدپستی: {sender_info[2]}  |  تلفن: {sender_info[3]}"
        bbox = draw.textbbox((0, 0), text, font=font_info)
        text_width = bbox[2] - bbox[0]
        draw.text((width - right_margin - text_width, info_y), text, black, font=font_info)
        
        # خط جداکننده وسط با طرح زیباتر
        middle_y = section1_start + 140
        # خط نقطه‌چین
        for x in range(30, width-30, 15):
            draw.ellipse([(x, middle_y-2), (x+8, middle_y+2)], fill=gray)
        
        # ================== بخش گیرنده (ردیف پایین) ==================
        section2_start = middle_y + 20
        
        # کادر عنوان گیرنده - سمت چپ با ارتفاع بیشتر
        label_y = section2_start
        
        # سایه برای کادر
        draw.rounded_rectangle(
            [(label_x+3, label_y+3), (label_x + label_width+3, label_y + label_height+3)],
            radius=10,
            fill=gray,
            outline=None
        )
        # کادر اصلی
        draw.rounded_rectangle(
            [(label_x, label_y), (label_x + label_width, label_y + label_height)],
            radius=10,
            fill=dark_gray,
            outline=black,
            width=2
        )
        
        # متن گیرنده - بالاتر در کادر
        receiver_label_text = "گیرنده"
        bbox = draw.textbbox((0, 0), receiver_label_text, font=font_label)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_label = label_x + (label_width - text_width) // 2
        y_label = label_y + (label_height - text_height) // 2 - 3
        draw.text((x_label, y_label), receiver_label_text, white, font=font_label)
        
        # اطلاعات گیرنده - راست چین
        info_y = section2_start + 5
        
        # نام - راست چین
        text = f"نام: {receiver_info[0]}"
        bbox = draw.textbbox((0, 0), text, font=font_main)
        text_width = bbox[2] - bbox[0]
        draw.text((width - right_margin - text_width, info_y), text, black, font=font_main)
        info_y += 35
        
        # آدرس - راست چین با قابلیت تقسیم به چند خط
        address_prefix = "آدرس: "
        address_text = receiver_info[1]
        full_address = address_prefix + address_text
        
        # بررسی آیا آدرس در یک خط جا می‌شود
        bbox = draw.textbbox((0, 0), full_address, font=font_info)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_text_width:
            # اگر در یک خط جا می‌شود
            draw.text((width - right_margin - text_width, info_y), full_address, black, font=font_info)
            info_y += 35
        else:
            # اگر نمی‌شود، تقسیم کن
            wrapped_lines = self.wrap_text(draw, full_address, font_info, max_text_width)
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font_info)
                text_width = bbox[2] - bbox[0]
                draw.text((width - right_margin - text_width, info_y), line, black, font=font_info)
                info_y += 35
        
        # کدپستی و تلفن - راست چین
        text = f"کدپستی: {receiver_info[2]}  |  تلفن: {receiver_info[3]}"
        bbox = draw.textbbox((0, 0), text, font=font_info)
        text_width = bbox[2] - bbox[0]
        draw.text((width - right_margin - text_width, info_y), text, black, font=font_info)
        
        # ================== فوتر - وب‌سایت و شماره در وسط ==================
        footer_y = height - 85
        
        # کادر فوتر با پس‌زمینه
        draw.rounded_rectangle(
            [(10, footer_y), (width-10, height-10)],
            radius=20,
            fill=light_gray,
            outline=None
        )
        # مستطیل بالا برای گوشه‌های تیز
        draw.rectangle(
            [(10, footer_y), (width-10, footer_y+20)],
            fill=light_gray,
            outline=None
        )
        
        # خط بالای فوتر
        draw.line([(10, footer_y), (width-10, footer_y)], fill=black, width=3)
        
        # خط اول: وب‌سایت و شماره تلفن در وسط صفحه
        first_line_y = footer_y + 15
        
        # محاسبه عرض کل متن برای وسط‌چین
        website_text = "NokhbehSho.com"
        phone_text = "021-91091722"
        separator = " | "
        
        # محاسبه عرض هر بخش
        bbox_website = draw.textbbox((0, 0), website_text, font=font_website)
        website_width = bbox_website[2] - bbox_website[0]
        
        bbox_sep = draw.textbbox((0, 0), separator, font=font_website)
        sep_width = bbox_sep[2] - bbox_sep[0]
        
        bbox_phone = draw.textbbox((0, 0), phone_text, font=font_phone)
        phone_width = bbox_phone[2] - bbox_phone[0]
        
        # عرض کل
        total_width = website_width + sep_width + phone_width
        
        # شروع از وسط صفحه
        start_x = (width - total_width) // 2
        
        # وب‌سایت
        draw.text((start_x, first_line_y), website_text, black, font=font_website)
        
        # جداکننده
        draw.text((start_x + website_width, first_line_y), separator, dark_gray, font=font_website)
        
        # شماره تلفن
        draw.text((start_x + website_width + sep_width, first_line_y + 2), phone_text, black, font=font_phone)
        
        # خط دوم: متن توضیحی در وسط
        desc_text = "مرجع تخصصی آموزش رباتیک و هوش مصنوعی کودکان و نوجوانان"
        bbox = draw.textbbox((0, 0), desc_text, font=font_tiny)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, footer_y + 45), desc_text, dark_gray, font=font_tiny)
        
        # تبدیل به RGB برای ذخیره
        img = img.convert('RGB')
        
        # ذخیره تصویر
        img.save(output_filename, dpi=(300, 300), quality=100)
        
        return img
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🏷️ Image Tools - Label Maker & Cropper")
        self.setGeometry(200, 200, 900, 750)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add the address label tab
        address_widget = AddressLabelWidget()
        tab_widget.addTab(address_widget, "🏷️ Address Labels")
        
        # Add the image cropper tab
        cropper_widget = ImageCropperWidget()
        tab_widget.addTab(cropper_widget, "✂️ Image Cropper")
        
        main_layout.addWidget(tab_widget)

# MODIFY your main function:
def main():
    """تابع اصلی برنامه"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 در دسترس نیست. لطفاً نصب کنید:")
        print("pip install PyQt6")
        return
    
    try:
        app = QApplication(sys.argv)
        
        # تنظیم فونت برای کل برنامه
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        app.setFont(font)
        
        # تنظیم راست‌چین برای زبان‌های RTL
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        window = MainApp()  # Changed from AddressLabelApp to MainApp
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()