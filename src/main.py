import webview

from src.config import config
from src.utils.js_api import js_api

if __name__ == '__main__':
    webview.create_window('xiSearch', config.project_path + 'html/index.html', js_api=js_api,
                          min_size=(1300, 800))
    webview.start()
