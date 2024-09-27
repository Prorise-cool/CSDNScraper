## 简介

CSDNScraper 是一个基于 Python 和 PyQt6 开发的图形用户界面（GUI）应用程序，旨在帮助用户轻松爬取 [CSDN](https://www.csdn.net/) 文章，并将其保存为 Markdown 格式。该工具支持同时输入多个 URL 进行批量爬取，并提供便捷的保存路径设置功能。

## 功能特性

- **多 URL 支持**：一次性输入多个 CSDN 文章的 URL，程序将逐一爬取并生成独立的 Markdown 文件。
- **HTML 内容解析**：支持直接输入或粘贴 HTML 内容，并将其附加到统一的 Markdown 笔记中。
- **自动处理图片**：自动下载并转换文章中的图片为 Markdown 格式。
- **配置管理**：通过配置文件管理保存路径，方便用户自定义文件存储位置。
- **错误处理与反馈**：实时显示爬取进度，并在爬取完成后提供详细的结果反馈。

## 演示视频

观看项目的使用演示视频：[Bilibili 视频链接](https://www.bilibili.com/video/BV19v4de6EPK/)

## 安装与配置

### 前提条件

- **Python 3.7 或更高版本**：请确保您的系统已安装 Python。可以通过以下命令检查 Python 版本：

  ```bash
  python --version
  ```
### 安装依赖

使用 `pip` 安装项目所需的外部库：

```bash
pip install -r requirements.txt
```

**注意**：如果您没有 `requirements.txt` 文件，可以手动安装所需的库：

```bash
pip install requests beautifulsoup4 html2text PyQt6
```

### 配置设置

初次运行程序时，默认的保存路径为用户主目录。您可以通过程序的“设置保存路径”按钮自定义保存目录。

## 使用方法

1. **运行程序**

   在项目根目录下运行以下命令启动应用程序：

   ```bash
   python main.py
   ```

   > **说明**：确保您当前位于包含 `main.py` 文件的目录。

2. **输入 URL 或 HTML 内容**

   - **爬取多个 CSDN 文章**：
     - 在文本输入框中，每行输入一个 CSDN 文章的 URL。
     - 例如：
       ```
       https://blog.csdn.net/username/article/details/123456789
       https://blog.csdn.net/username/article/details/987654321
       ```

   - **解析 HTML 内容**：
     - 直接粘贴或输入 HTML 内容，然后点击“解析文本”按钮，将内容附加到统一的 Markdown 文件中。

3. **获取文章**

   点击“获取文章”按钮，程序将开始爬取输入的所有 URL，对应的文章将被保存为独立的 Markdown 文件。

4. **解析文本**

   如果输入的是 HTML 内容，点击“解析文本”按钮，内容将被转换为 Markdown 格式并附加到 `merged_notes.md` 文件中。

5. **设置保存路径**

   点击“设置保存路径”按钮，选择您希望保存 Markdown 文件的目录。更改后，所有后续的爬取或解析内容将保存到新的路径中。

## 联系方式

如果您有任何问题或建议，请通过以下方式联系我：

- **邮箱**：3381292732@qq.com.com
- **GitHub**：[Prorise-cool](https://github.com/Prorise-cool)
- **Bilibili**：[Prorise的Bilibili频道](https://space.bilibili.com/361040115)

---

感谢您使用 CSDNScraper！如果您觉得这个项目对您有帮助，请考虑给我一个 Star ⭐。

