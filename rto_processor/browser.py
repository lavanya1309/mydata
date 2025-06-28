from selenium import webdriver
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from configs import config
from rto_processor.utils import *

class Browser:
    def __init__(self):
        self.setup_driver()
        self.load_page()

    
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        for arg in config.CHROME_OPTIONS:
            options.add_argument(arg)
        for key, value in config.CHROME_EXPERIMENTAL_OPTIONS.items():
            options.add_experimental_option(key, value)

        options.add_argument(f"--user-agent={random.choice(config.USER_AGENTS)}")
        
        options.add_experimental_option("prefs", config.PREFS)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # anti detection script
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        })

    def load_page(self):
        try:
            log_message("Loading page")
            self.driver.get(config.BASE_URL)
            log_message("Page loaded")
        except Exception as e:
            log_message(f"Error loading page: {str(e)}")
            raise

    def update_download_directory(self, download_dir):
        """
        Update the download directory for the browser
        
        Args:
            download_dir (str): Path to the new download directory
        """
        try:
            # Update the config
            config.BASE_DOWNLOAD_DIR = download_dir
            
            # Update Chrome preferences
            self.driver.execute_cdp_cmd(
                'Page.setDownloadBehavior',
                {
                    'behavior': 'allow',
                    'downloadPath': download_dir
                }
            )
            log_message(f"Download directory updated to: {download_dir}")
        except Exception as e:
            log_message(f"Error updating download directory: {str(e)}")
            raise

    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
            log_message("Browser closed successfully")
        except Exception as e:
            log_message(f"Error closing browser: {str(e)}")
