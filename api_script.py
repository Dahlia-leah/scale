import sys
import requests
import pyperclip
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QFrame, QSizePolicy, QToolButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QLinearGradient, QBrush, QPainter, QPainterPath
import subprocess
import os
import time

def start_api():
    """Start the Flask API in the background."""
    try:
        if os.name == "nt":  # Windows
            subprocess.Popen(["python", "scale_api.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["python3", "scale_api.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("API started successfully")
    except Exception as e:
        print(f"Error starting API: {e}")

def get_weight():
    """Fetch weight data from the API."""
    try:
        response = requests.get("http://127.0.0.1:5000/read-scale", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {"weight": data['weight'], "unit": data['unit'], "status": "connected"}
        else:
            return {"weight": "0.0", "unit": "g", "status": "error"}
    except requests.exceptions.RequestException:
        return {"weight": "0.0", "unit": "g", "status": "disconnected"}

def get_ngrok_url():
    """Fetch and shorten the ngrok public URL."""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if response.status_code == 200:
            tunnels = response.json()
            for tunnel in tunnels.get("tunnels", []):
                if "https" in tunnel.get("public_url", ""):
                    full_url = tunnel["public_url"]
                    return {"url": full_url.split("//")[-1].split(".")[0], "status": "connected"}
        return {"url": "Not found", "status": "not_found"}
    except requests.exceptions.RequestException:
        return {"url": "Not available", "status": "offline"}

class ModernFrame(QFrame):
    """A modern styled frame with rounded corners, shadow and gradient background."""
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setObjectName("ModernFrame")
        
        # Add drop shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(self.shadow)
        
        self.update_style()
        
    def update_style(self, is_dark=None):
        if is_dark is not None:
            self.is_dark = is_dark
            
        if self.is_dark:
            self.setStyleSheet("""
                #ModernFrame {
                    background-color: #2D2D2D;
                    border-radius: 16px;
                    border: 1px solid #3D3D3D;
                }
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
            """)
            self.shadow.setColor(QColor(0, 0, 0, 70))
        else:
            self.setStyleSheet("""
                #ModernFrame {
                    background-color: white;
                    border-radius: 16px;
                    border: 1px solid #E0E0E0;
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
            """)
            self.shadow.setColor(QColor(0, 0, 0, 30))

class CircularButton(QToolButton):
    """A circular button with icon and hover effects."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.setFixedSize(50, 50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Toggle Dark/Light Mode")
        
        # Animation for hover effect
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(150)
        
        self.update_icon()
        
    def update_icon(self):
        # Using Unicode characters for sun and moon
        if self.is_dark_mode:
            self.setText("☀️")  # Sun emoji for light mode
        else:
            self.setText("🌙")  # Moon emoji for dark mode
        
        self.setFont(QFont("Arial", 16))  # Reduced font size
        self.update_style()
        
    def update_style(self):
        if self.is_dark_mode:
            self.setStyleSheet("""
                QToolButton {
                    background-color: #3D3D3D;
                    color: #FDB813;
                    border: none;
                    border-radius: 25px;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: #4D4D4D;
                }
            """)
        else:
            self.setStyleSheet("""
                QToolButton {
                    background-color: #EEEEEE;
                    color: #5C6BC0;
                    border: none;
                    border-radius: 25px;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: #E0E0E0;
                }
            """)
    
    def enterEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() - 3, rect.width(), rect.height()))
        self._animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() + 3, rect.width(), rect.height()))
        self._animation.start()
        super().leaveEvent(event)
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.update_icon()
        return self.is_dark_mode

class ModernButton(QPushButton):
    """A modern styled button with hover and click animations."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.is_dark_mode = False
        self.setFixedHeight(50)  # Reduced height
        self.setFont(QFont("Arial", 12))  # Reduced font size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Animation for hover effect
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(150)
        
        self.update_style()
        
    def update_style(self, is_dark=False):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5CBF60;
                }
                QPushButton:pressed {
                    background-color: #3C9F40;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5CBF60;
                }
                QPushButton:pressed {
                    background-color: #3C9F40;
                }
            """)
    
    def enterEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() - 3, rect.width(), rect.height()))
        self._animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() + 3, rect.width(), rect.height()))
        self._animation.start()
        super().leaveEvent(event)

class StatusLabel(QLabel):
    """A styled status label with background."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.is_dark_mode = False
        self.setFont(QFont("Arial", 11))  # Reduced font size
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
        
    def update_style(self, is_dark=False):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("""
                QLabel {
                    color: #CCCCCC;
                    background-color: #222222;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    color: #555555;
                    background-color: #F0F0F0;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)

class TitleBar(QWidget):
    """Custom title bar with window controls."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.parent = parent
        self.setFixedHeight(45)  # Reduced height
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # Window controls (red, yellow, green buttons)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        self.close_btn = QToolButton(self)
        self.close_btn.setFixedSize(14, 14)  # Reduced size
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.parent.close)
        
        self.minimize_btn = QToolButton(self)
        self.minimize_btn.setFixedSize(14, 14)  # Reduced size
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        self.maximize_btn = QToolButton(self)
        self.maximize_btn.setFixedSize(14, 14)  # Reduced size
        self.maximize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        controls_layout.addWidget(self.close_btn)
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.maximize_btn)
        
        # Title
        self.title_label = QLabel("USB Scale Reader")
        self.title_label.setFont(QFont("Arial", 14))  # Reduced font size
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addSpacing(40)  # Balance the layout
        
        self.update_style()
        
    def update_style(self, is_dark=False):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("""
                background-color: #1A1A1A;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            """)
            self.title_label.setStyleSheet("color: white;")
            self.close_btn.setStyleSheet("background-color: #FF5F57; border-radius: 7px;")
            self.minimize_btn.setStyleSheet("background-color: #FDBC2C; border-radius: 7px;")
            self.maximize_btn.setStyleSheet("background-color: #28C840; border-radius: 7px;")
        else:
            self.setStyleSheet("""
                background-color: #E0E0E0;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            """)
            self.title_label.setStyleSheet("color: #333333;")
            self.close_btn.setStyleSheet("background-color: #FF5F57; border-radius: 7px;")
            self.minimize_btn.setStyleSheet("background-color: #FDBC2C; border-radius: 7px;")
            self.maximize_btn.setStyleSheet("background-color: #28C840; border-radius: 7px;")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent.moving = True
            self.parent.offset = event.position()
    
    def mouseMoveEvent(self, event):
        if self.parent.moving:
            self.parent.move(self.parent.mapToGlobal(event.position().toPoint()) - self.parent.offset.toPoint())

class ScaleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True  # Start with dark mode by default
        self.current_ngrok_url = "Not available"
        self.moving = False
        self.offset = None
        
        # Remove window frame
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Start the API
        print("Starting API...")
        start_api()
        time.sleep(1)  # Allow API time to start
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("USB Scale Reader")
        # Keep the larger window size
        self.setGeometry(100, 100, 650, 800)
        self.setMinimumSize(600, 750)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main container with rounded corners
        self.container = QFrame()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 25)
        container_layout.setSpacing(25)  # Reduced spacing
        
        # Custom title bar
        self.title_bar = TitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(35, 15, 35, 15)
        content_layout.setSpacing(30)  # Reduced spacing
        
        # Header with title and theme toggle
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 15, 0, 15)
        
        # Title
        title_label = QLabel("USB Scale Reader", self)
        title_font = QFont("Arial", 24, QFont.Weight.Bold)  # Reduced font size
        title_label.setFont(title_font)
        
        # Theme toggle button
        self.theme_toggle = CircularButton(self)
        self.theme_toggle.is_dark_mode = self.is_dark_mode
        self.theme_toggle.update_icon()
        self.theme_toggle.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle)
        
        content_layout.addLayout(header_layout)
        
        # Weight card
        self.weight_card = ModernFrame(self, self.is_dark_mode)
        weight_layout = QVBoxLayout(self.weight_card)
        weight_layout.setContentsMargins(30, 30, 30, 30)  # Reduced margins
        weight_layout.setSpacing(15)  # Reduced spacing
        
        weight_title = QLabel("Current Weight", self.weight_card)
        weight_title.setFont(QFont("Arial", 18))  # Reduced font size
        weight_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Fix for weight display - use a fixed-width font and ensure proper formatting
        self.weight_value = QLabel("0.0 g", self.weight_card)
        self.weight_value.setFont(QFont("Courier New", 48, QFont.Weight.Bold))  # Reduced font size
        self.weight_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.weight_status = QLabel("Connecting...", self.weight_card)
        self.weight_status.setFont(QFont("Arial", 14))  # Reduced font size
        self.weight_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        weight_layout.addWidget(weight_title)
        weight_layout.addWidget(self.weight_value)
        weight_layout.addWidget(self.weight_status)
        content_layout.addWidget(self.weight_card)
        
        # Ngrok card
        self.ngrok_card = ModernFrame(self, self.is_dark_mode)
        ngrok_layout = QVBoxLayout(self.ngrok_card)
        ngrok_layout.setContentsMargins(30, 30, 30, 30)  # Reduced margins
        ngrok_layout.setSpacing(15)  # Reduced spacing
        
        ngrok_title = QLabel("Ngrok Tunnel", self.ngrok_card)
        ngrok_title.setFont(QFont("Arial", 18))  # Reduced font size
        ngrok_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.ngrok_value = QLabel("--", self.ngrok_card)
        self.ngrok_value.setFont(QFont("Arial", 20, QFont.Weight.Bold))  # Reduced font size
        self.ngrok_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.ngrok_status = QLabel("Connecting...", self.ngrok_card)
        self.ngrok_status.setFont(QFont("Arial", 14))  # Reduced font size
        self.ngrok_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ngrok_layout.addWidget(ngrok_title)
        ngrok_layout.addWidget(self.ngrok_value)
        ngrok_layout.addWidget(self.ngrok_status)
        content_layout.addWidget(self.ngrok_card)
        
        # Copy button
        self.copy_button = ModernButton("Copy Ngrok Subdomain", self)
        self.copy_button.update_style(self.is_dark_mode)
        self.copy_button.clicked.connect(self.copy_ngrok_url)
        content_layout.addWidget(self.copy_button)
        
        # Status bar
        self.status_label = StatusLabel("Status: Initializing...", self)
        self.status_label.update_style(self.is_dark_mode)
        content_layout.addWidget(self.status_label)
        
        container_layout.addLayout(content_layout)
        main_layout.addWidget(self.container)
        
        # Apply initial theme
        self.apply_theme()
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self.update_info()

    def apply_theme(self):
        if self.is_dark_mode:
            # Dark theme
            self.container.setStyleSheet("""
                #container {
                    background-color: #121212;
                    border-radius: 15px;
                    border: 1px solid #2A2A2A;
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
        else:
            # Light theme
            self.container.setStyleSheet("""
                #container {
                    background-color: #F5F5F5;
                    border-radius: 15px;
                    border: 1px solid #E0E0E0;
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
            """)
        
        # Update components with new theme
        if hasattr(self, 'title_bar'):
            self.title_bar.update_style(self.is_dark_mode)
            
        if hasattr(self, 'weight_card'):
            self.weight_card.update_style(self.is_dark_mode)
            self.ngrok_card.update_style(self.is_dark_mode)
            self.copy_button.update_style(self.is_dark_mode)
            self.status_label.update_style(self.is_dark_mode)
            
        if hasattr(self, 'theme_toggle'):
            self.theme_toggle.is_dark_mode = self.is_dark_mode
            self.theme_toggle.update_icon()

    def toggle_theme(self):
        self.is_dark_mode = self.theme_toggle.toggle_theme()
        self.apply_theme()
        self.status_label.setText(f"Status: Theme changed to {'dark' if self.is_dark_mode else 'light'} mode")

    def update_info(self):
        try:
            # Update weight information
            weight_data = get_weight()
            
            # Fix for weight display - ensure proper formatting and handle potential encoding issues
            try:
                # Try to convert to float for consistent formatting
                weight_value = float(weight_data["weight"])
                formatted_weight = f"{weight_value:.1f} {weight_data['unit']}"
            except (ValueError, TypeError):
                # If conversion fails, use as is with proper spacing
                formatted_weight = f"{weight_data['weight']} {weight_data['unit']}"
                
            # Set the text with proper encoding
            self.weight_value.setText(formatted_weight)
            
            if weight_data["status"] == "connected":
                self.weight_status.setText("✓ Connected")
                self.weight_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
            elif weight_data["status"] == "error":
                self.weight_status.setText("⚠ Scale Error")
                self.weight_status.setStyleSheet("color: #f39c12; font-weight: bold;")
            else:
                self.weight_status.setText("✗ Disconnected")
                self.weight_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.status_label.setText("Status: Scale disconnected. Check USB connection.")
            
            # Update ngrok information
            ngrok_data = get_ngrok_url()
            self.ngrok_value.setText(ngrok_data["url"])
            self.current_ngrok_url = ngrok_data["url"]
            
            if ngrok_data["status"] == "connected":
                self.ngrok_status.setText("✓ Tunnel Active")
                self.ngrok_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
                self.status_label.setText("Status: System online and ready")
            elif ngrok_data["status"] == "offline":
                self.ngrok_status.setText("✗ Ngrok Offline")
                self.ngrok_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.status_label.setText("Status: Ngrok is not running")
            else:
                self.ngrok_status.setText("⚠ Tunnel Not Found")
                self.ngrok_status.setStyleSheet("color: #f39c12; font-weight: bold;")
                self.status_label.setText("Status: No active Ngrok tunnel found")
        
        except Exception as e:
            print(f"Error updating info: {e}")
            self.status_label.setText(f"Status: Error updating information")
            # Ensure weight display shows something valid even on error
            self.weight_value.setText("0.0 g")

    def copy_ngrok_url(self):
        try:
            if self.current_ngrok_url not in ["Not available", "Not found"]:
                pyperclip.copy(self.current_ngrok_url)
                self.status_label.setText(f"Status: Copied '{self.current_ngrok_url}' to clipboard")
                
                # Show a styled message box
                self.show_message("Copied", f"Ngrok subdomain '{self.current_ngrok_url}' copied to clipboard!")
            else:
                self.status_label.setText("Status: Nothing to copy - Ngrok not available")
                self.show_error("Ngrok is not running or no tunnel is available.")
        except Exception as e:
            print(f"Error copying URL: {e}")
            self.status_label.setText("Status: Error copying to clipboard")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        
        # Style the message box
        if self.is_dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5CBF60;
                }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                    color: #333333;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5CBF60;
                }
            """)
        
        msg_box.exec()

    def show_error(self, message):
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText(message)
            msg_box.setWindowTitle("Error")
            
            # Style the message box
            if self.is_dark_mode:
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #1E1E1E;
                        color: #FFFFFF;
                        font-size: 12px;
                    }
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #f85c4c;
                    }
                """)
            else:
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #FFFFFF;
                        color: #333333;
                        font-size: 12px;
                    }
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #f85c4c;
                    }
                """)
            
            msg_box.exec()
        except Exception as e:
            print(f"Error showing message box: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScaleApp()
    window.show()
    sys.exit(app.exec())