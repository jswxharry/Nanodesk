"""Setup wizard for first-time configuration."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from nanodesk.desktop.core.config_manager import get_config_manager


class ProviderPage(QWizardPage):
    """Page 1: LLM Provider configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("配置大模型服务")
        self.setSubTitle("选择并配置您要使用的 AI 服务")

        # Set minimum size for the page
        self.setMinimumSize(500, 400)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Provider selection
        provider_label = QLabel("选择服务提供商：")
        provider_label.setStyleSheet("color: #000000; font-weight: bold;")
        layout.addWidget(provider_label)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("阿里云百炼 (通义千问)", "dashscope")
        self.provider_combo.addItem("OpenAI", "openai")
        self.provider_combo.addItem("OpenRouter", "openrouter")
        self.provider_combo.addItem("Ollama (本地)", "ollama")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        layout.addWidget(self.provider_combo)

        layout.addSpacing(20)

        # API Key
        apikey_label = QLabel("API Key:")
        apikey_label.setStyleSheet("color: #000000; font-weight: bold;")
        layout.addWidget(apikey_label)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入您的 API Key")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_key_edit)

        # API Base (for custom/Ollama)
        self.api_base_label = QLabel("API Base URL:")
        self.api_base_edit = QLineEdit()
        self.api_base_edit.setPlaceholderText("https://...")
        layout.addWidget(self.api_base_label)
        layout.addWidget(self.api_base_edit)

        layout.addSpacing(20)

        # Model selection
        model_label = QLabel("默认模型：")
        model_label.setStyleSheet("color: #000000; font-weight: bold;")
        layout.addWidget(model_label)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        layout.addWidget(self.model_combo)

        layout.addStretch()

        # Help text
        help_label = QLabel("💡 提示: API Key 将被加密存储，仅当前用户可访问")
        help_label.setStyleSheet("color: gray;")
        layout.addWidget(help_label)

        self.setLayout(layout)
        self._on_provider_changed(0)

    def _on_provider_changed(self, index):
        """Update UI based on selected provider."""
        provider = self.provider_combo.currentData()

        # Update model options
        self.model_combo.clear()

        models = {
            "dashscope": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "openrouter": ["anthropic/claude-sonnet-4", "meta/llama-3.1-70b"],
            "ollama": ["llama3.1", "qwen2.5", "mistral"],
        }

        for model in models.get(provider, []):
            self.model_combo.addItem(model)

        # Show/hide API base
        is_custom = provider in ["ollama"]
        self.api_base_label.setVisible(is_custom)
        self.api_base_edit.setVisible(is_custom)

        if provider == "ollama":
            self.api_base_edit.setText("http://localhost:11434")
        else:
            self.api_base_edit.clear()

    def validatePage(self) -> bool:
        """Validate page before proceeding."""
        if not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "配置不完整", "请输入 API Key")
            return False
        return True

    def get_config(self) -> dict:
        """Get configuration from this page."""
        return {
            "provider": self.provider_combo.currentData(),
            "api_key": self.api_key_edit.text().strip(),
            "api_base": self.api_base_edit.text().strip(),
            "model": self.model_combo.currentText(),
        }


class ChannelPage(QWizardPage):
    """Page 2: Channel configuration (Feishu)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("配置通讯频道")
        self.setSubTitle("设置飞书机器人（可选，推荐启用）")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Feishu checkbox
        self.feishu_checkbox = QCheckBox("启用飞书机器人")
        self.feishu_checkbox.setChecked(True)
        self.feishu_checkbox.stateChanged.connect(self._on_feishu_toggled)
        layout.addWidget(self.feishu_checkbox)

        layout.addSpacing(10)

        # Feishu config frame
        self.feishu_frame = QFrame()
        feishu_layout = QVBoxLayout()

        # App ID
        feishu_layout.addWidget(QLabel("App ID:"))
        self.app_id_edit = QLineEdit()
        self.app_id_edit.setPlaceholderText("cli_xxxxxxxxxxxxxxxx")
        feishu_layout.addWidget(self.app_id_edit)

        # App Secret
        feishu_layout.addWidget(QLabel("App Secret:"))
        self.app_secret_edit = QLineEdit()
        self.app_secret_edit.setPlaceholderText("从飞书开放平台获取")
        self.app_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        feishu_layout.addWidget(self.app_secret_edit)

        # Help
        help_text = QLabel(
            '<a href="#">如何获取 App ID 和 Secret?</a>\n'
            '1. 访问 <a href="https://open.feishu.cn">open.feishu.cn</a>\n'
            "2. 创建企业自建应用\n"
            '3. 在"凭证与基础信息"中查看'
        )
        help_text.setOpenExternalLinks(True)
        help_text.setStyleSheet("color: gray; padding: 10px;")
        feishu_layout.addWidget(help_text)

        self.feishu_frame.setLayout(feishu_layout)
        layout.addWidget(self.feishu_frame)

        layout.addStretch()

        # Note
        note = QLabel("💡 您也可以先跳过此步骤，稍后在配置中心添加")
        note.setStyleSheet("color: gray;")
        layout.addWidget(note)

        self.setLayout(layout)

    def _on_feishu_toggled(self, state):
        """Enable/disable Feishu config."""
        self.feishu_frame.setEnabled(state == Qt.CheckState.Checked.value)

    def get_config(self) -> dict:
        """Get configuration from this page."""
        return {
            "feishu_enabled": self.feishu_checkbox.isChecked(),
            "feishu_app_id": self.app_id_edit.text().strip(),
            "feishu_app_secret": self.app_secret_edit.text().strip(),
        }


class ConfirmPage(QWizardPage):
    """Page 3: Confirm and finish."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("完成配置")
        self.setSubTitle("确认您的配置信息")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Summary text
        self.summary_edit = QTextEdit()
        self.summary_edit.setReadOnly(True)
        self.summary_edit.setMaximumHeight(150)
        layout.addWidget(self.summary_edit)

        layout.addSpacing(20)

        # Options
        self.autostart_checkbox = QCheckBox("开机自动启动 Nanodesk")
        self.autostart_checkbox.setChecked(True)
        layout.addWidget(self.autostart_checkbox)

        self.minimize_checkbox = QCheckBox("启动后最小化到系统托盘")
        self.minimize_checkbox.setChecked(True)
        layout.addWidget(self.minimize_checkbox)

        layout.addStretch()

        # Note
        note = QLabel('点击"完成"后，配置将被保存并启动服务。')
        note.setStyleSheet("color: gray;")
        layout.addWidget(note)

        self.setLayout(layout)

    def set_summary(self, text: str):
        """Set summary text."""
        self.summary_edit.setText(text)

    def get_config(self) -> dict:
        """Get configuration from this page."""
        return {
            "autostart": self.autostart_checkbox.isChecked(),
            "minimize_on_start": self.minimize_checkbox.isChecked(),
        }


class SetupWizard(QWizard):
    """Setup wizard for first-time configuration."""

    config_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Nanodesk 配置向导")
        self.resize(600, 500)
        self.setMinimumSize(550, 450)

        # Set button text
        self.setButtonText(QWizard.WizardButton.BackButton, "< 返回")
        self.setButtonText(QWizard.WizardButton.NextButton, "下一步 >")
        self.setButtonText(QWizard.WizardButton.FinishButton, "完成")
        self.setButtonText(QWizard.WizardButton.CancelButton, "取消")

        # Create pages
        self.provider_page = ProviderPage()
        self.channel_page = ChannelPage()
        self.confirm_page = ConfirmPage()

        self.addPage(self.provider_page)
        self.addPage(self.channel_page)
        self.addPage(self.confirm_page)

        # Connect signals
        self.currentIdChanged.connect(self._on_page_changed)
        self.finished.connect(self._on_finished)

    def _on_page_changed(self, page_id):
        """Handle page change."""
        if page_id == 2:  # Confirm page
            self._update_summary()

    def _update_summary(self):
        """Update summary on confirm page."""
        provider_cfg = self.provider_page.get_config()
        channel_cfg = self.channel_page.get_config()

        provider_names = {
            "dashscope": "阿里云百炼",
            "openai": "OpenAI",
            "openrouter": "OpenRouter",
            "ollama": "Ollama (本地)",
        }

        summary = f"""配置摘要：
───────────────────────────────
大模型服务: {provider_names.get(provider_cfg["provider"], provider_cfg["provider"])}
模型: {provider_cfg["model"]}
API Key: {"*" * 8}...

飞书机器人: {"已启用" if channel_cfg["feishu_enabled"] else "未启用"}
"""
        if channel_cfg["feishu_enabled"]:
            summary += f"App ID: {channel_cfg['feishu_app_id'][:10]}...\n"

        self.confirm_page.set_summary(summary)

    def _on_finished(self, result):
        """Handle wizard finish."""
        if result == QWizard.DialogCode.Accepted:
            self._save_config()

    def _save_config(self):
        """Save configuration."""
        provider_cfg = self.provider_page.get_config()
        channel_cfg = self.channel_page.get_config()
        confirm_cfg = self.confirm_page.get_config()

        config_manager = get_config_manager()
        config = config_manager.load()

        # Update provider
        config["agents"]["defaults"]["provider"] = provider_cfg["provider"]
        config["agents"]["defaults"]["model"] = provider_cfg["model"]
        config["providers"][provider_cfg["provider"]]["apiKey"] = provider_cfg["api_key"]
        if provider_cfg["api_base"]:
            config["providers"][provider_cfg["provider"]]["apiBase"] = provider_cfg["api_base"]

        # Update Feishu
        config["channels"]["feishu"]["enabled"] = channel_cfg["feishu_enabled"]
        if channel_cfg["feishu_app_id"]:
            config["channels"]["feishu"]["appId"] = channel_cfg["feishu_app_id"]
        if channel_cfg["feishu_app_secret"]:
            config["channels"]["feishu"]["appSecret"] = channel_cfg["feishu_app_secret"]

        # Save
        if config_manager.save(config):
            self.config_saved.emit()
        else:
            QMessageBox.critical(self, "错误", "保存配置失败")
