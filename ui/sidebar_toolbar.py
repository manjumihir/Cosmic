from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy,
    QFrame, QLabel, QGraphicsOpacityEffect, QStyle, QSplitter,
    QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve,
    QMimeData, QPoint, QEvent, QPointF, QSettings
)
from PyQt6.QtGui import (
    QIcon, QPalette, QColor, QDrag, QPainter, QCursor, 
    QEnterEvent, QPointingDevice
)
from .side_panels import (
    ChartsSidePanel, HelpSidePanel, PreferencesSidePanel,
    ReportSidePanel, ResearchSidePanel
)

class DraggableButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.drag_start_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self.drag_start_position:
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.objectName())  # Store button identifier
        drag.setMimeData(mime_data)

        # Create semi-transparent drag pixmap
        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #3b3b3b;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event):
        source_button = event.source()
        if source_button and source_button != self:
            parent = self.parent()
            if parent:
                parent.reorder_buttons(source_button, self)
        self.setStyleSheet("")
        event.acceptProposedAction()

class SidebarContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarContainer")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.buttons = {}
        
    def save_button_order(self):
        """Save the current order of buttons to settings"""
        settings = QSettings('Cosmic', 'CosmicCalculator')
        button_order = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, DraggableButton):
                button_order.append(widget.objectName())
        settings.setValue('sidebar_button_order', button_order)
        
    def restore_button_order(self):
        """Restore the saved order of buttons"""
        settings = QSettings('Cosmic', 'CosmicCalculator')
        button_order = settings.value('sidebar_button_order', [], type=list)
        
        if not button_order:  # If no saved order, keep default
            return
            
        # Create a mapping of button names to widgets
        button_widgets = {}
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, DraggableButton):
                button_widgets[widget.objectName()] = widget
        
        # Remove all buttons from layout
        for button_name in button_widgets:
            self.layout.removeWidget(button_widgets[button_name])
        
        # Add buttons back in saved order
        for button_name in button_order:
            if button_name in button_widgets:
                self.layout.addWidget(button_widgets[button_name])
        
        # Add any remaining buttons that weren't in the saved order
        for button_name, widget in button_widgets.items():
            if button_name not in button_order:
                self.layout.addWidget(widget)
        
        # Add stretch at the end
        self.layout.addStretch()
        
    def reorder_buttons(self, source_button, target_button):
        """Reorder buttons when one is dropped onto another"""
        source_index = self.layout.indexOf(source_button)
        target_index = self.layout.indexOf(target_button)
        
        if source_index != -1 and target_index != -1:
            # Remove source button
            self.layout.removeWidget(source_button)
            # Insert at target position
            self.layout.insertWidget(target_index, source_button)
            # Save the new order
            self.save_button_order()

class SidebarToolbar(QFrame):
    def __init__(self, parent=None, input_page=None):
        super().__init__(parent)
        self.setObjectName("sidebarToolbar")
        self.input_page = input_page
        
        # Initialize settings
        self.settings = QSettings('Cosmic', 'CosmicCalculator')
        
        # Set fixed widths
        self.collapsed_width = 5
        self.sidebar_width = 50  # Width when showing icons
        self.expanded_width = self.settings.value('sidebar_expanded_width', 600, type=int)  # Load from settings
        self.setFixedWidth(self.collapsed_width)
        
        # Create main horizontal layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar container
        self.sidebar_container = SidebarContainer()
        self.sidebar_container.setFixedWidth(self.sidebar_width)
        self.sidebar_container.setMouseTracking(True)  # Enable mouse tracking
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.sidebar_container)
        
        # Create panel container
        self.panel_container = QWidget()
        self.panel_container.setObjectName("panelContainer")
        self.panel_container.setMouseTracking(True)  # Enable mouse tracking
        self.panel_layout = QVBoxLayout(self.panel_container)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_layout.setSpacing(0)
        self.splitter.addWidget(self.panel_container)
        self.panel_container.hide()
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Configure splitter
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3b3b3b;
            }
            QSplitter::handle:hover {
                background-color: #4b4b4b;
            }
        """)
        
        # Initialize side panels
        self.charts_panel = ChartsSidePanel()
        self.help_panel = HelpSidePanel()
        self.preferences_panel = PreferencesSidePanel()
        self.report_panel = ReportSidePanel()
        self.research_panel = ResearchSidePanel()
        
        # Add panels to container
        self.panel_layout.addWidget(self.charts_panel)
        self.panel_layout.addWidget(self.help_panel)
        self.panel_layout.addWidget(self.preferences_panel)
        self.panel_layout.addWidget(self.report_panel)
        self.panel_layout.addWidget(self.research_panel)
        
        # Hide all panels initially
        self.charts_panel.hide()
        self.help_panel.hide()
        self.preferences_panel.hide()
        self.report_panel.hide()
        self.research_panel.hide()
        
        # Add input page to panel container if provided
        if self.input_page:
            self.panel_layout.addWidget(self.input_page)
            self.input_page.hide()
        
        # Add buttons
        self.create_buttons()
        
        # Setup animations
        self.sidebar_animation = QPropertyAnimation(self, b"minimumWidth")
        self.sidebar_animation.setDuration(150)
        self.sidebar_animation.finished.connect(self.on_animation_finished)
        
        # Track mouse events and state
        self.setMouseTracking(True)
        self.is_sidebar_visible = False
        self.active_panel = None
        self.last_active_panel = None
        self.last_expanded_width = self.expanded_width
        self.mouse_inside = False  # Track if mouse is inside widget
        
        # Setup hover timer
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.collapse_sidebar)
        
        # Setup keep-alive timer
        self.keep_alive_timer = QTimer()
        self.keep_alive_timer.setInterval(100)  # Check every 100ms
        self.keep_alive_timer.timeout.connect(self.check_mouse_position)
        self.keep_alive_timer.start()
        
        # Style
        self.setStyleSheet("""
            QFrame#sidebarToolbar {
                background-color: transparent;
                border: none;
            }
            QWidget#sidebarContainer {
                background-color: #2b2b2b;
            }
            QWidget#panelContainer {
                background-color: #2b2b2b;
                border-left: 1px solid #3b3b3b;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ffffff;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
        """)

    def create_buttons(self):
        button_data = [
            ("Input", "SP_DirOpenIcon", self.toggle_input_panel),
            ("Help", "SP_MessageBoxQuestion", self.toggle_help_panel),
            ("Preferences", "SP_TitleBarMenuButton", self.toggle_preferences_panel),
            ("Chart", "SP_FileDialogDetailedView", self.toggle_charts_panel),
            ("Report", "SP_DialogSaveButton", self.toggle_report_panel),
            ("Research", "SP_FileDialogContentsView", self.toggle_research_panel),
        ]
        
        for text, icon_name, callback in button_data:
            btn = DraggableButton()
            btn.setObjectName(text)
            icon = self.style().standardIcon(getattr(QStyle.StandardPixmap, icon_name))
            btn.setIcon(icon)
            btn.setToolTip(text)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(callback)
            self.sidebar_container.layout.addWidget(btn)
            self.sidebar_container.buttons[text] = btn
        
        # Add stretch to push buttons to top
        self.sidebar_container.layout.addStretch()
        
        # Restore button order after creating buttons
        self.sidebar_container.restore_button_order()

    def toggle_charts_panel(self):
        self._toggle_panel(self.charts_panel)

    def toggle_help_panel(self):
        self._toggle_panel(self.help_panel)

    def toggle_preferences_panel(self):
        self._toggle_panel(self.preferences_panel)

    def toggle_report_panel(self):
        self._toggle_panel(self.report_panel)

    def toggle_research_panel(self):
        self._toggle_panel(self.research_panel)

    def _toggle_panel(self, panel):
        # Hide all panels first
        self.input_page.hide()
        self.charts_panel.hide()
        self.help_panel.hide()
        self.preferences_panel.hide()
        self.report_panel.hide()
        self.research_panel.hide()
        
        # Show the selected panel
        panel.show()
        self.panel_container.show()
        
        # Update the active panel
        self.active_panel = panel
        self.last_active_panel = panel
        
        # Expand the sidebar if it's not already expanded
        if self.width() <= self.sidebar_width:
            self.sidebar_animation.setStartValue(self.width())
            self.sidebar_animation.setEndValue(self.expanded_width)
            self.sidebar_animation.start()

    def toggle_input_panel(self):
        """Toggle the input panel visibility"""
        if self.input_page:
            if self.active_panel != self.input_page:
                # Hide any active panel
                if self.active_panel:
                    self.active_panel.hide()
                # Show input panel
                self.input_page.show()
                self.panel_container.show()
                self.active_panel = self.input_page
                self.last_active_panel = self.active_panel  # Update last active panel
                # Expand to last width or default
                self.sidebar_animation.setStartValue(self.width())
                self.sidebar_animation.setEndValue(self.last_expanded_width)
                self.sidebar_animation.start()
            else:
                # Save current width before collapsing
                self.last_expanded_width = self.width()
                self.settings.setValue('sidebar_expanded_width', self.last_expanded_width)  # Save to settings
                # Collapse back to sidebar width
                self.sidebar_animation.setStartValue(self.width())
                self.sidebar_animation.setEndValue(self.sidebar_width)
                self.sidebar_animation.start()
                self.active_panel = None
                # Start timer to hide sidebar if mouse is not over it
                if not self.underMouse():
                    self.hover_timer.start(300)

    def check_mouse_position(self):
        """Periodically check if mouse is inside the widget"""
        if self.isVisible():
            mouse_pos = QCursor.pos()
            widget_rect = self.rect()
            widget_pos = self.mapToGlobal(widget_rect.topLeft())
            widget_rect.moveTo(widget_pos)
            
            is_inside = widget_rect.contains(mouse_pos)
            if is_inside != self.mouse_inside:
                self.mouse_inside = is_inside
                if is_inside:
                    # Convert QPoint to QPointF for QEnterEvent
                    pos_f = QPointF(mouse_pos.x(), mouse_pos.y())
                    enter_event = QEnterEvent(
                        pos_f,  # localPos
                        pos_f,  # scenePos
                        pos_f,  # globalPos
                        QPointingDevice.primaryPointingDevice()  # device
                    )
                    self.enterEvent(enter_event)
                else:
                    self.leaveEvent(QEvent(QEvent.Type.Leave))

    def enterEvent(self, event):
        """Show sidebar and last active panel on mouse enter"""
        self.mouse_inside = True
        self.hover_timer.stop()
        if not self.is_sidebar_visible:
            target_width = self.last_expanded_width if self.last_active_panel else self.sidebar_width
            self.sidebar_animation.setStartValue(self.width())
            self.sidebar_animation.setEndValue(target_width)
            self.sidebar_animation.start()
            self.is_sidebar_visible = True
            
            # Show last active panel if exists
            if self.last_active_panel and not self.active_panel:
                self.panel_container.show()
                self.last_active_panel.show()
                self.active_panel = self.last_active_panel
        
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Start timer to hide sidebar and panel on mouse leave"""
        self.mouse_inside = False
        if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            self.hover_timer.start(300)
        super().leaveEvent(event)
        
    def collapse_sidebar(self):
        """Collapse sidebar and hide panel"""
        if not self.mouse_inside:  # Only collapse if mouse is really outside
            if self.active_panel:
                self.last_active_panel = self.active_panel
                self.active_panel = None
            self.sidebar_animation.setStartValue(self.width())
            self.sidebar_animation.setEndValue(self.collapsed_width)
            self.sidebar_animation.start()
            self.is_sidebar_visible = False
        
    def on_animation_finished(self):
        """Handle animation completion"""
        if not self.active_panel and not self.mouse_inside:
            if self.input_page:
                self.input_page.hide()
            self.panel_container.hide()
            
    def showEvent(self, event):
        """Start keep-alive timer when widget becomes visible"""
        super().showEvent(event)
        self.keep_alive_timer.start()
        
    def hideEvent(self, event):
        """Stop keep-alive timer when widget is hidden"""
        super().hideEvent(event)
        self.keep_alive_timer.stop()
