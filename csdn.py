#++++ author：@Prorise
#++++ main：爬取csdn文章并保存为markdown格式
#++++ 外部库: requests, BeautifulSoup, html2text, PyQt6
#++++ time: 2024年9月16日

import sys
import re
import os
import requests
import configparser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit,
                             QMessageBox, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QLabel, QProgressDialog)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize, Qt
from bs4 import BeautifulSoup, Comment
import html2text


class AnimatedButton(QPushButton):
    """
    自定义动画按钮类，继承自QPushButton，具有鼠标悬停和离开时的大小动画效果。
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(200, 50)  # 设置按钮固定大小
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 设置鼠标悬停时的光标形状

        # 初始化大小动画
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(100)  # 动画持续时间100毫秒
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # 设置缓和曲线

    def enterEvent(self, event):
        """
        鼠标进入按钮区域时触发，增加按钮大小。
        """
        self._animation.setEndValue(QSize(210, 55))  # 目标大小
        self._animation.start()  # 启动动画
        super().enterEvent(event)

    def leaveEvent(self, event):
        """
        鼠标离开按钮区域时触发，恢复按钮大小。
        """
        self._animation.setEndValue(QSize(200, 50))  # 恢复原大小
        self._animation.start()  # 启动动画
        super().leaveEvent(event)


class CSDNScraper(QMainWindow):
    """
    CSDN文章爬虫主窗口类，继承自QMainWindow，负责用户界面和爬取逻辑。
    """
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()  # 初始化配置解析器
        self.config_file = 'settings.ini'  # 配置文件名
        self.load_config()  # 加载配置
        self.initUI()  # 初始化用户界面

    def load_config(self):
        """
        加载配置文件，如果不存在则创建默认配置。
        """
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)  # 读取现有配置
        if 'Settings' not in self.config:
            self.config['Settings'] = {'save_path': os.path.expanduser('~')}  # 设置默认保存路径
        self.save_path = self.config['Settings']['save_path']  # 获取保存路径

    def save_config(self):
        """
        保存当前配置到配置文件中。
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)  # 写入配置

    def initUI(self):
        """
        初始化用户界面，包括窗口标题、尺寸、样式以及各个控件。
        """
        self.setWindowTitle("CSDN文章爬虫")  # 设置窗口标题
        self.setGeometry(100, 100, 600, 400)  # 设置窗口位置和大小
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QWidget {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QPlainTextEdit {
                background-color: #2C3E50;
                border: 2px solid #3498DB;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                color: #ECF0F1;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2574A9;
            }
            QLabel {
                font-size: 18px;
                color: #ECF0F1;
            }
        """)  # 设置样式表

        central_widget = QWidget()
        self.setCentralWidget(central_widget)  # 设置中央部件

        layout = QVBoxLayout()  # 创建垂直布局

        # 创建并添加标题标签
        title_label = QLabel("CSDN文章爬虫")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 创建并添加文本输入框
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("在此输入CSDN文章URL，每行一个，或输入HTML内容")
        layout.addWidget(self.text_input)

        button_layout = QHBoxLayout()  # 创建水平布局用于按钮

        # 创建并添加“获取文章”按钮
        self.get_article_button = AnimatedButton("获取文章")
        self.get_article_button.clicked.connect(self.spider_csdn)  # 连接点击事件
        button_layout.addWidget(self.get_article_button)

        # 创建并添加“解析文本”按钮
        self.parse_text_button = AnimatedButton("解析文本")
        self.parse_text_button.clicked.connect(self.parse_html_text)  # 连接点击事件
        button_layout.addWidget(self.parse_text_button)

        # 创建并添加“设置保存路径”按钮
        self.set_path_button = AnimatedButton("设置保存路径")
        self.set_path_button.clicked.connect(self.set_save_path)  # 连接点击事件
        button_layout.addWidget(self.set_path_button)

        layout.addLayout(button_layout)  # 将按钮布局添加到主布局

        central_widget.setLayout(layout)  # 设置中央部件的布局

    def set_save_path(self):
        """
        打开文件对话框，允许用户选择保存路径，并更新配置。
        """
        new_path = QFileDialog.getExistingDirectory(self, "选择保存路径", self.save_path)  # 打开目录选择对话框
        if new_path:
            self.save_path = new_path  # 更新保存路径
            self.config['Settings']['save_path'] = self.save_path  # 更新配置
            self.save_config()  # 保存配置
            self.show_message("成功", f"保存路径已设置为: {self.save_path}", QMessageBox.Icon.Information)  # 显示成功消息

    def spider_csdn(self):
        """
        爬取CSDN文章的主方法，支持多个URL输入，逐一爬取并保存为Markdown文件。
        """
        input_text = self.text_input.toPlainText().strip()  # 获取输入文本并去除首尾空白
        if not input_text:
            self.show_message("错误", "请输入URL或HTML内容", QMessageBox.Icon.Critical)  # 输入为空，显示错误
            return

        # 检查是否为HTML内容
        if input_text.startswith('<!DOCTYPE html') or input_text.startswith('<html'):
            self.show_message("错误", "请点击'解析文本'按钮来处理HTML内容", QMessageBox.Icon.Warning)  # 提示用户使用解析文本按钮
            return

        # 分割输入为多行URL
        urls = [line.strip() for line in input_text.splitlines() if line.strip()]  # 获取非空行的URL列表
        if not urls:
            self.show_message("错误", "未检测到有效的URL", QMessageBox.Icon.Critical)  # 无有效URL，显示错误
            return

        # 显示进度对话框
        progress = QProgressDialog("正在爬取文章...", "取消", 0, len(urls), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)  # 设置为模态对话框
        progress.setMinimumDuration(0)  # 最小显示时间

        success_count = 0  # 成功计数
        failure_messages = []  # 失败消息列表

        for i, url in enumerate(urls):
            if progress.wasCanceled():
                break  # 用户取消，退出循环
            progress.setValue(i)  # 更新进度值
            QApplication.processEvents()  # 处理事件，保持界面响应

            if not self.is_valid_url(url):
                failure_messages.append(f"无效的URL: {url}")  # 无效URL，记录失败消息
                continue

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                response = requests.get(url=url, headers=headers)  # 发送GET请求
                response.raise_for_status()  # 检查响应状态
                html = response.text  # 获取HTML内容

                self.process_html(html, single_file=False)  # 处理HTML并保存为单独文件
                success_count += 1  # 增加成功计数

            except requests.RequestException as e:
                failure_messages.append(f"URL: {url} 请求失败: {str(e)}")  # 网络请求失败，记录失败消息
            except Exception as e:
                failure_messages.append(f"URL: {url} 发生错误: {str(e)}")  # 其他错误，记录失败消息

        progress.setValue(len(urls))  # 完成进度

        # 构建结果消息
        result_message = f"成功爬取 {success_count} 篇文章。"
        if failure_messages:
            result_message += "\n\n失败详情:\n" + "\n".join(failure_messages)

        self.show_message("完成", result_message, QMessageBox.Icon.Information)  # 显示完成消息

    def parse_html_text(self):
        """
        解析输入框中的HTML内容，并将其附加到统一的Markdown文件中。
        """
        html = self.text_input.toPlainText().strip()  # 获取输入文本并去除首尾空白
        if not html:
            self.show_message("错误", "请输入HTML内容", QMessageBox.Icon.Critical)  # 输入为空，显示错误
            return

        if not (html.startswith('<!DOCTYPE html') or html.startswith('<html')):
            self.show_message("错误", "输入的内容不是有效的HTML", QMessageBox.Icon.Warning)  # 非HTML内容，显示警告
            return

        try:
            self.process_html(html, single_file=True)  # 处理HTML并附加到统一文件
            self.show_message("成功", "HTML内容已附加到笔记中。", QMessageBox.Icon.Information)  # 显示成功消息
        except Exception as e:
            self.show_message("错误", f"解析HTML失败: {str(e)}", QMessageBox.Icon.Critical)  # 解析失败，显示错误

    def process_html(self, html, single_file=False):
        """
        处理HTML内容，将其转换为Markdown格式并保存到文件中。

        :param html: 要处理的HTML内容
        :param single_file: 是否将内容附加到单一文件中
        """
        soup = BeautifulSoup(html, 'html.parser')  # 解析HTML

        # 移除所有注释
        for comment in soup.find_all(string=lambda string: isinstance(string, Comment)):
            comment.extract()

        # 处理 <pre> 标签中的代码
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                # 移除可能的行号
                lines = code.get_text().split('\n')
                cleaned_lines = [re.sub(r'^\s*\d+\s*', '', line) for line in lines]
                code.string = '\n'.join(cleaned_lines)

        # 获取文章标题
        title = soup.select_one(".title-article")
        if title:
            title = title.text.strip()
        else:
            title = "未知标题"
        title_clean = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '_', title)  # 清理标题，替换非法字符

        # 获取文章内容
        content = soup.select_one("article")
        if not content:
            content = soup.body

        # 处理图片标签
        for img in content.find_all('img'):
            alt_text = img.get('alt', '').strip()  # 获取alt属性
            src = img.get('src', '').strip()  # 获取src属性

            if src.startswith('//'):
                src = f"https:{src}"  # 补全协议
            elif src.startswith('/'):
                src = f"https://blog.csdn.net{src}"  # 补全域名

            src = src.split('#')[0]  # 去除URL中的锚点

            markdown_img = f"![{alt_text}]({src})"  # 构建Markdown图片语法

            parent_a = img.find_parent('a')  # 查找图片的父级链接
            if parent_a and parent_a.get('href'):
                href = parent_a.get('href')
                markdown_img = f"[{markdown_img}]({href})"  # 如果有链接，则包裹在Markdown链接中

            img.replace_with(soup.new_string(markdown_img))  # 替换图片标签为Markdown语法

        # 使用html2text进行最终转换
        h = html2text.HTML2Text()
        h.body_width = 0  # 不自动换行
        markdown_content = h.handle(str(content))  # 获取Markdown内容

        # 处理LaTeX公式
        markdown_content = re.sub(r'\$\$(.*?)\$\$', r'$$\n\1\n$$', markdown_content, flags=re.DOTALL)
        markdown_content = re.sub(r'\$(.*?)\$', r'$\1$', markdown_content)

        # 额外的清理步骤
        markdown_content = re.sub(r'^\s*\*\s*\d+\s*$', '', markdown_content, flags=re.MULTILINE)  # 移除类似 "* 1" 的行
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)  # 将多个连续的空行减少到最多两个

        if single_file:
            # 生成或附加到统一的Markdown文件
            file_path = os.path.join(self.save_path, "merged_notes.md")
            with open(file_path, mode="a", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(markdown_content)
                f.write("\n\n---\n\n")  # 添加分隔线
        else:
            # 生成单独的Markdown文件
            base_title = title_clean if title_clean else "未知标题"
            file_path = os.path.join(self.save_path, f"{base_title}.md")
            original_file_path = file_path
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(self.save_path, f"{base_title}_{counter}.md")  # 避免文件名冲突
                counter += 1

            with open(file_path, mode="w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(markdown_content)

    def is_valid_url(self, url):
        """
        验证给定的URL是否有效。

        :param url: 要验证的URL
        :return: 如果URL有效，返回True；否则返回False
        """
        regex = re.compile(
            r'^(?:http|https)://'  # 以http://或https://开头
            r'(?:\S+)'  # 后面跟随非空白字符
            , re.IGNORECASE)
        return re.match(regex, url) is not None  # 返回匹配结果

    def show_message(self, title, message, icon):
        """
        显示消息框。

        :param title: 消息框标题
        :param message: 消息内容
        :param icon: 消息图标类型
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)  # 设置标题
        msg_box.setText(message)  # 设置内容
        msg_box.setIcon(icon)  # 设置图标
        msg_box.exec()  # 显示消息框


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 设置应用程序样式
    scraper = CSDNScraper()  # 创建爬虫窗口实例
    scraper.show()  # 显示窗口
    sys.exit(app.exec())  # 运行应用程序并等待退出
