from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException, NoSuchElementException
from configs import config
from rto_processor.utils import log_message, random_delay, setup_directories
import time
import os
import re
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RTOProcessor:
    def __init__(self, browser):
        self.browser = browser
        setup_directories()

    def setup_axis(self):
        try:
            log_message("Setting up X-axis (Month Wise) and Y-axis (Maker)...")

            WebDriverWait(self.browser.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[name='javax.faces.ViewState']"))
            )
            
            # Select Y-axis (Maker)
            y_axis_label = self.wait_and_scroll_to_element(By.ID, config.Y_AXIS_LABEL, 20, "Y-axis dropdown")
            if not y_axis_label:
                log_message("Could not find Y-axis dropdown")
                return False
                
            self.smart_click(y_axis_label, "Y-axis dropdown")
            random_delay(0.5, 1)
            
            maker_option = self.wait_and_scroll_to_element(By.XPATH, "//li[@data-label='Maker']", 10, "Maker option")
            if maker_option:
                self.smart_click(maker_option, "Maker option")
            else:
                # Try JavaScript fallback
                self.browser.driver.execute_script("PrimeFaces.widgets.widget_yaxisVar.selectValue('4');")
                log_message("Used JavaScript to select Maker for Y-axis")
            random_delay(0.5, 1)
            
            # Select X-axis (Month Wise)
            x_axis_label = self.wait_and_scroll_to_element(By.ID, config.X_AXIS_LABEL, 20, "X-axis dropdown")
            if not x_axis_label:
                log_message("Could not find X-axis dropdown")
                return False
                
            self.smart_click(x_axis_label, "X-axis dropdown")
            random_delay(0.5, 1)
            
            month_wise_option = self.wait_and_scroll_to_element(By.XPATH, "//li[@data-label='Month Wise']", 10, "Month Wise option")
            if month_wise_option:
                self.smart_click(month_wise_option, "Month Wise option")
            else:
                # Try JavaScript fallback
                self.browser.driver.execute_script("PrimeFaces.widgets.widget_xaxisVar.selectValue('6');")
                log_message("Used JavaScript to select Month Wise for X-axis")
            random_delay(0.5, 1)
            
            log_message("Axis setup completed")
            return True
        except Exception as e:
            log_message(f"Error in setup_axis: {str(e)}")
            return False

    def wait_and_find_element(self, locator_type, locator_value, timeout=10, name="element"):
        try:
            element = WebDriverWait(self.browser.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            random_delay(0.2, 0.5)
            return element
        except Exception as e:
            log_message(f"Failed to find {name}: {str(e)}")
            return None

    def get_all_rtos_for_state(self):
        """Get list of all RTOs for the currently selected state"""
        try:
            log_message("Getting list of all RTOs for the selected state")
            
            # Click RTO dropdown to open it
            rto_dropdown_label = self.wait_and_find_element(By.ID, "selectedRto_label", 20, "RTO dropdown label")
            if not rto_dropdown_label:
                return []
            
            self.smart_click(rto_dropdown_label, "RTO dropdown label")
            random_delay(0.5, 1)
            
            # Find all RTO options
            rto_options = self.browser.driver.find_elements(By.XPATH, "//div[@id='selectedRto_panel']//li")
            
            rto_list = []
            for option in rto_options:
                rto_text = option.text.strip()
                if rto_text and "All Vahan4 Running Office" not in rto_text:
                    rto_list.append(rto_text)
            
            # Close dropdown by clicking outside
            self.browser.driver.find_element(By.TAG_NAME, "body").click()
            
            log_message(f"Found {len(rto_list)} RTOs for the state")
            return rto_list
        except Exception as e:
            log_message(f"Error in get_all_rtos_for_state: {str(e)}")
            return []

    def select_specific_rto(self, rto_name, state_name, year):
        """
        Select a specific RTO from dropdown
        Returns True if successful, False otherwise
        """
        try:
            log_message(f"Selecting RTO: {rto_name}")
            
            # Open RTO dropdown
            rto_dropdown_label = self.wait_and_find_element(By.ID, "selectedRto_label", 10, "RTO dropdown")
            if not rto_dropdown_label:
                log_message("Could not find RTO dropdown")
                return False
            
            self.smart_click(rto_dropdown_label, "RTO dropdown")
            random_delay(0.5, 1)
            
            # Find and click specific RTO
            rto_xpath = f"//li[normalize-space(text())='{rto_name}']"
            rto_option = self.wait_and_find_element(By.XPATH, rto_xpath, 5, f"RTO option: {rto_name}")
            
            if not rto_option:
                log_message(f"Could not find RTO: {rto_name}")
                return False
                
            self.smart_click(rto_option, f"RTO option: {rto_name}")
            
            # Verify selection
            selected_rto = self.wait_and_find_element(By.ID, "selectedRto_label", 5, "selected RTO text")
            if not selected_rto or rto_name not in selected_rto.text:
                log_message("RTO selection verification failed")
                return False
                
            log_message(f"Successfully selected RTO: {rto_name}")
            return True
            
        except Exception as e:
            log_message(f"Error in select_specific_rto: {str(e)}")
            return False
        
    def smart_click(self, element, element_name="element"):
        """Try multiple click methods until one works"""
        methods = [
            lambda: element.click(),
            lambda: self.browser.driver.execute_script("arguments[0].click();", element),
            lambda: ActionChains(self.browser.driver).move_to_element(element).click().perform(),
        ]
        
        for i, method in enumerate(methods):
            try:
                method()
                log_message(f"Clicked {element_name} using method {i+1}")
                return True
            except Exception as e:
                if i == len(methods) - 1:
                    log_message(f"All click methods failed for {element_name}: {str(e)}")
                    return False
                continue
        return False

    def wait_and_scroll_to_element(self, locator_type, locator_value, timeout=10, name="element"):
        try:
            # First try with regular wait
            try:
                element = WebDriverWait(self.browser.driver, timeout).until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            except StaleElementReferenceException:
                log_message(f"Stale element when waiting for {name}, retrying...")
                # Handle stale reference by refreshing the wait
                element = WebDriverWait(self.browser.driver, timeout).until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            except TimeoutException:
                log_message(f"Timeout waiting for {name}, checking if page needs refresh...")
                # Check if we need to refresh the page due to session timeout
                try:
                    error_message = self.browser.driver.find_element(By.XPATH, "//span[contains(text(), 'session')]")
                    if error_message and "session" in error_message.text.lower():
                        log_message("Session timeout detected, refreshing page...")
                        self.browser.driver.refresh()
                        WebDriverWait(self.browser.driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "[name='javax.faces.ViewState']"))
                        )
                        # Try again after refresh
                        element = WebDriverWait(self.browser.driver, timeout).until(
                            EC.presence_of_element_located((locator_type, locator_value))
                        )
                    else:
                        raise
                except:
                    log_message(f"Element {name} not found after timeout")
                    return None
            
            # Once we have the element, scroll to it
            try:
                self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                random_delay(0.2, 0.5)
            except Exception as e:
                log_message(f"Warning: Could not scroll to {name}: {str(e)}")
            
            return element
        except WebDriverException as e:
            if "not reachable" in str(e) or "connection" in str(e).lower() or "timeout" in str(e).lower():
                log_message(f"Connection error or timeout when finding {name}: {str(e)}")
                # Check if it's a timeout issue from the website
                if "timeout" in str(e).lower():
                    log_message("Website timeout detected. Waiting for 15 minutes before retrying...")
                    time.sleep(900)  # Wait for 15 minutes (900 seconds)
                    log_message("Resuming after 15-minute wait")
                
                # Try to recover by refreshing
                try:
                    self.browser.driver.refresh()
                    log_message("Page refreshed after connection error or timeout")
                    return self.wait_and_scroll_to_element(locator_type, locator_value, timeout, name)
                except:
                    log_message("Failed to recover from connection error or timeout")
                    return None
            else:
                log_message(f"WebDriver error when finding {name}: {str(e)}")
                return None
        except Exception as e:
            log_message(f"Failed to find {name} ({locator_type}:{locator_value}): {str(e)}")
            return None

    def select_year(self, year):
        """Select year from dropdown"""
        try:
            log_message(f"Selecting Year: {year}")
            
            year_dropdown = self.wait_and_find_element(By.ID, config.YEAR_DROPDOWN_LABEL, 20, "year dropdown")
            if not year_dropdown:
                return False
            
            self.smart_click(year_dropdown, "year dropdown")
            random_delay(0.5, 1)
            
            year_option = self.wait_and_find_element(By.XPATH, f"//li[text()='{year}']", 10, f"year option: {year}")
            if year_option:
                self.smart_click(year_option, f"year option: {year}")
                log_message(f"Successfully selected year: {year}")
                return True
            return False
        except Exception as e:
            log_message(f"Error selecting year: {str(e)}")
            return False

    def select_state_primefaces(self, state_name):
        try:
            log_message(f"Selecting State: {state_name}")
        
            # First find and click the state dropdown label to open the dropdown
            state_dropdown_label = self.wait_and_scroll_to_element(By.ID, config.STATE_DROPDOWN_LABEL, 20, "state dropdown label")
            if not state_dropdown_label:
                # Try alternative locators
                state_dropdown_label = self.wait_and_scroll_to_element(By.XPATH, f"//div[contains(@id, '{config.STATE_DROPDOWN_LABEL}')]//label", 5, "state dropdown alternative")
                if not state_dropdown_label:
                    log_message("Could not find state dropdown label")
                    return False
            
            self.smart_click(state_dropdown_label, "state dropdown label")
            
            random_delay(0.5, 1)
            
            # Extract the base name of the state (without numbers)
            state_base_name = state_name.split('(')[0].strip()
            
            # Try multiple approaches to find and click the state item
            methods = [
                # Method 1: Exact text match
                lambda: self.browser.driver.find_element(By.XPATH, f"//li[normalize-space(text())='{state_name}']"),
                # Method 2: Contains text
                lambda: self.browser.driver.find_element(By.XPATH, f"//li[contains(text(), '{state_base_name}')]"),
                # Method 3: Using data-label attribute
                lambda: self.browser.driver.find_element(By.XPATH, f"//li[@data-label='{state_name}']"),
                # Method 4: Partial data-label match
                lambda: self.browser.driver.find_element(By.XPATH, f"//li[contains(@data-label, '{state_base_name}')]"),
                # Method 5: Using ID containing 'j_idt49' and containing text
                lambda: self.browser.driver.find_element(By.XPATH, f"//ul[contains(@id, 'j_idt49')]/li[contains(text(), '{state_base_name}')]")
            ]
            
            for method in methods:
                try:
                    state_option = method()
                    self.smart_click(state_option, f"state option: {state_name}")
                    random_delay(0.5, 1)
                    
                    # Verify selection was successful
                    current_selection = self.browser.driver.find_element(By.ID, config.STATE_DROPDOWN_LABEL).text
                    if state_base_name in current_selection:
                        log_message(f"Successfully selected state: {current_selection}")
                        return True
                    else:
                        log_message(f"Selection verification failed. Current selection: {current_selection}")
                        continue
                except Exception:
                    continue
            
        except Exception as e:
            log_message(f"Error in select_state_primefaces: {str(e)}")
            return False

    def open_left_panel(self):
        try:
            log_message("Opening left panel if needed")
            
            # Check if panel needs to be expanded by looking at the toggler
            toggler = self.browser.driver.find_element(By.ID, "filterLayout-toggler")
            panel_class = toggler.get_attribute("class")
            
            if "ui-layout-toggler-closed" in panel_class or "layout-toggler-collapsed" in panel_class:
                self.smart_click(toggler, "left panel toggler")
                log_message("Expanded left panel")
                random_delay(0.5, 1)
            else:
                log_message("Left panel already open")
            
            return True
        except Exception as e:
            log_message(f"Error in open_left_panel: {str(e)}")
            # Not critical if this fails - we can still try to select options
            return True

    def close_left_panel_if_opened(self):
        try:
            # Find the collapse button based on its attributes
            collapse_button = self.browser.driver.find_element(
                By.XPATH, '//a[@title="Collapse" and contains(@class, "ui-layout-unit-header-icon")]'
            )
            if collapse_button.is_displayed():
                collapse_button.click()
                random_delay(0.5, 1.5)  # Small delay to allow UI to collapse
                log_message("Left panel collapsed successfully.")
            else:
                log_message("Collapse button not visible; panel might already be closed.")
        except NoSuchElementException:
            log_message("Collapse button not found; left panel may already be closed or selector is incorrect.")
        except Exception as e:
            log_message(f"Unexpected error while closing left panel: {str(e)}")
    
    def select_left_panel_option(self):
        try:
            log_message("Selecting vehicle categories and fuel types")
            
            # Select Vehicle Categories: TWO WHEELER
            for idx in [0, 1, 2]:  # Indices for TWO WHEELER categories
                try:
                    checkbox_id = f"VhCatg:{idx}"
                    checkbox = self.wait_and_scroll_to_element(By.ID, checkbox_id, 5, f"checkbox {checkbox_id}")
                    if checkbox and not checkbox.is_selected():
                        self.smart_click(checkbox, f"checkbox {checkbox_id}")
                        random_delay(0.2, 0.5)
                except Exception as e:
                    log_message(f"Error selecting checkbox VhCatg:{idx}: {str(e)}")
            
            
            for idx in config.FUEL_TYPES:
                try:
                    checkbox_id = f"fuel:{idx}"
                    checkbox = self.wait_and_scroll_to_element(By.ID, checkbox_id, 5, f"checkbox {checkbox_id}")
                    if checkbox and not checkbox.is_selected():
                        self.smart_click(checkbox, f"checkbox {checkbox_id}")
                        random_delay(0.2, 0.5)
                except Exception as e:
                    log_message(f"Error selecting checkbox fuel:{idx}: {str(e)}")
            
            log_message("Vehicle categories and fuel types selected")
            return True
        except Exception as e:
            log_message(f"Error in select_left_panel_option: {str(e)}")
            return False

    def click_left_refresh(self):
        try:
            log_message("Clicking left refresh button")
            
            refresh_button = self.wait_and_scroll_to_element(By.ID, config.LEFT_REFRESH_BUTTON_LABEL, 20, "left refresh button")
            if not refresh_button:
                log_message("Could not find left refresh button")
                return False
                
            self.smart_click(refresh_button, "left refresh button")
            # random_delay(2, 4)  # Longer delay for processing
            log_message("Left refresh button clicked")
            return True
        except Exception as e:
            log_message(f"Error in click_left_refresh: {str(e)}")
            return False

    def download_excel_rto(self, state_name, year, rto_name):
        try:
            log_message(f"Downloading Excel file for {state_name}, {rto_name}, {year}")
            
            # Find the Excel download button
            excel_button = self.wait_and_scroll_to_element(By.ID, "groupingTable:xls", 20, "Excel download button")
            
            if not excel_button:
                # Try alternative methods
                locators = [
                    (By.XPATH, "//button[contains(@id, 'xls')]"),
                    (By.XPATH, "//button[contains(@title, 'Excel')]"),
                    (By.CSS_SELECTOR, "button[id$='xls']")
                ]
                
                for locator_type, locator in locators:
                    excel_button = self.wait_and_scroll_to_element(locator_type, locator, 5, "Excel button alternative")
                    if excel_button:
                        break
            
            if not excel_button:
                log_message("Could not find Excel download button")
                return False
            
            # Click the download button
            self.smart_click(excel_button, "Excel download button")
            log_message("Clicked Excel download button")
            
            # Create year-wise directory structure: base_dir/year/state_name
            target_dir = os.path.join(config.BASE_DOWNLOAD_DIR, state_name)
            random_delay(3, 4)
            os.makedirs(target_dir, exist_ok=True)
            
            # Call wait_for_download_and_rename
            result = self.wait_for_download_and_rename(target_dir, state_name, rto_name)
            return result

        except Exception as e:
            log_message(f"Error in download_excel_rto: {str(e)}")
            import traceback
            log_message(f"Traceback: {traceback.format_exc()}")
            return False

    def wait_for_download_and_rename(self, target_dir, state_name, rto_name):
        """
        Wait for download to complete and rename file
        
        Args:
            target_dir (str): Directory to move the downloaded file to
            state_name (str): Name of the state
            rto_name (str): Name of the RTO for filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            log_message(f"BASE_DOWNLOAD_DIR being checked: {config.BASE_DOWNLOAD_DIR}")
            log_message(f"Inside_wait_for_download_and_rename for {state_name}")
            
            # Ensure the base download directory exists
            if not os.path.exists(config.BASE_DOWNLOAD_DIR):
                log_message(f"Creating base download directory: {config.BASE_DOWNLOAD_DIR}")
                os.makedirs(config.BASE_DOWNLOAD_DIR, exist_ok=True)
            
            # Ensure target directory exists
            if not os.path.exists(target_dir):
                log_message(f"Creating target directory: {target_dir}")
                os.makedirs(target_dir, exist_ok=True)
            
            found_file = None
            timeout = 30  # 30 second timeout for download
            start_time = time.time()
    
            # Wait for download to complete
            while time.time() - start_time < timeout:
                current_files = os.listdir(config.BASE_DOWNLOAD_DIR)
                
                if any(f.endswith('.crdownload') for f in current_files):
                    time.sleep(1)
                    continue  # still downloading

                valid_files = [f for f in current_files if f.lower().endswith(('.xlsx', '.xls'))]
                if valid_files:
                    valid_files.sort(key=lambda f: os.path.getmtime(os.path.join(config.BASE_DOWNLOAD_DIR, f)), reverse=True)
                    found_file = os.path.join(config.BASE_DOWNLOAD_DIR, valid_files[0])

                    # Wait till size is stable
                    if self.is_download_complete(found_file):
                        time.sleep(1)  # small buffer
                        break
    
            if not found_file:
                log_message("Download timeout - file not found")
                return False
                
            try:
                def sanitize_filename(filename):
                    return re.sub(r'[\\/*?:"<>|]', "_", filename)

                # Sanitize the rto_name before using it in the filename
                sanitized_rto_name = sanitize_filename(rto_name)
                base_name = f"{sanitized_rto_name}.xlsx"
                new_filepath = os.path.join(target_dir, base_name)
                
                # Handle file name conflicts
                counter = 1
                original_new_filepath = new_filepath
                while os.path.exists(new_filepath):
                    name, ext = os.path.splitext(base_name)
                    new_filepath = os.path.join(target_dir, f"{name}_{counter}{ext}")
                    counter += 1
                    if counter > 100:  # Prevent infinite loop
                        log_message("Too many file conflicts, using timestamp")
                        timestamp = int(time.time())
                        new_filepath = os.path.join(target_dir, f"{name}_{timestamp}{ext}")
                        break
                
                if new_filepath != original_new_filepath:
                    log_message(f"File already exists, using new name: {os.path.basename(new_filepath)}")
                
                # Move the file to target directory
                log_message(f"Moving file from {found_file} to {new_filepath}")
                shutil.move(found_file, new_filepath)
                
                if not os.path.exists(new_filepath):
                    log_message("Error: File move operation failed")
                    return False

                log_message(f"Successfully moved file to: {new_filepath}")
                return True
                
            except Exception as e:
                log_message(f"Error processing downloaded file: {str(e)}")
                return False
                
        except Exception as e:
            log_message(f"Unexpected error in download wait: {str(e)}")
            return False
        
    def is_download_complete(self, file_path, check_interval=2):
        try:
            size1 = os.path.getsize(file_path)
            time.sleep(check_interval)
            size2 = os.path.getsize(file_path)
            return size1 == size2
        except:
            return False

    def check_for_503_error(self):
        """
        Detects actual 503 Service Unavailable / Bad Gateway errors based on title or heading tags.
        Returns True if detected, else False.
        """
        log_message("Checking for Badgateway (503) error")
        
        try:
            title = self.browser.driver.title.strip().lower()
            source = self.browser.driver.page_source.strip().lower()

            # log_message(f"Page title: {title}")
            # log_message(f"First 300 chars of page source: {source[:300]}")

            # Check very specific patterns to avoid false triggers
            if "503 service unavailable" in title or "bad gateway" in title:
                return True

            # Check HTML structure that typically appears in actual 503 pages
            if (
                "<h1>503" in source or
                "<title>503 service unavailable" in source or
                "<h1>bad gateway" in source or
                "nginx" in source and "503" in source
            ):
                return True

            return False

        except Exception as e:
            log_message(f"Error during 503 detection: {str(e)}")
            return False

    def apply_filters(self):
        """Apply specific filters"""
        try:
            log_message("Applying left panel filters")
            
            # Click right refresh to load data
            refresh_button = self.wait_and_find_element(By.ID, config.RIGHT_REFRESH_BUTTON_LABEL, 20, "right refresh button")
            if refresh_button:
                self.smart_click(refresh_button, "right refresh button")
                random_delay(4, 5)

            # Open LEFT PANEL options
            self.open_left_panel()

            random_delay(0.5, 1)
            
            # Select TWO WHEELER categories
            self.select_left_panel_option()

            random_delay(0.5, 1)

            # Click LEFT REFRESH
            self.click_left_refresh()

            random_delay(3.5, 4)

            # Close LEFT PANEL if opened
            self.close_left_panel_if_opened()
            
            return True
        except Exception as e:
            log_message(f"Error applying filters: {str(e)}")
            return False