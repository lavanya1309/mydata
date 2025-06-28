import logging
from rto_processor.processor import RTOProcessor
from rto_processor.browser import Browser
from rto_processor.utils import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
from configs import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        # Start the scraping process
        start_scrapper()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise
    finally:
        try:
            if 'browser' in locals():
                browser.driver.quit()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error while closing browser: {str(e)}")

def start_scrapper():
    """Main function to start the RTO data scraping process."""
    try:
        browser = Browser()
        processor = RTOProcessor(browser)
        log_message("\n=== Starting RTO-wise processing ===")
        year_state_mapping = config.YEAR_STATE_MAPPING
        
        # Track failed processes
        failed_processes = []
        
        # Save the original download directory
        # original_download_dir = config.BASE_DOWNLOAD_DIR
        
        for year, states in year_state_mapping.items():
            # Create year-specific download directory
            year_download_dir = os.path.join(config.BASE_DOWNLOAD_DIR, str(year))
            os.makedirs(year_download_dir, exist_ok=True)
            browser.update_download_directory(year_download_dir)

            for state in states:
                log_message(f"\nProcessing state: {state}, Year: {year}")
                
                # Process RTOs for this state and year
                failed_rtos = process_rto_wise_data(processor, state, year)
                
                if failed_rtos:
                    failed_processes.append({
                        'state': state,
                        'year': year,
                        'failed_rtos': failed_rtos
                    })
        
        # Log summary of failed processes
        if failed_processes:
            log_message("\n=== Processing Summary (Failed) ===")
            for process in failed_processes:
                log_message(f"Failed to process {len(process['failed_rtos'])} RTOs in {process['state']} ({process['year']}):")
                for rto in process['failed_rtos']:
                    log_message(f"  - {rto}")
            with open("failed_processes.json", "w") as f:
                json.dump(failed_processes, f, indent=4)
        else:
            log_message("\n=== All RTOs processed successfully ===")
            
    except Exception as e:
        log_message(f"Error in start_scrapper: {str(e)}")
        raise

def handle_503_and_recover(processor, retry_delay=900):
    """
    Handle recovery from a 503 Bad Gateway error.
    Waits, refreshes the page, and re-sets axis configuration.
    """
    log_message(f"503 error detected. Waiting {retry_delay // 60} minutes before retrying...")
    time.sleep(retry_delay)

    try:
        processor.browser.driver.refresh()
        WebDriverWait(processor.browser.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[name='javax.faces.ViewState']"))
        )
        log_message("Page refreshed. Re-attempting axis setup...")
        
        if not processor.setup_axis():
            raise Exception("Axis setup failed after 503 recovery")
        
        log_message("Axis re-setup successful after 503 recovery.")
        return True
    except Exception as e:
        log_message(f"Failed to recover after 503: {str(e)}")
        return False

def process_rto_wise_data(processor, state_name, year, specific_rtos=None, start_rto_index=0):
    """
    Main function to process RTO-wise data with resume capability
    """
    try:
        log_message(f"\n=== Starting RTO-wise processing for {state_name}, {year} ===\n")
        
        # Process the state with RTO processing
        failed_rtos = process_state(processor, state_name, year, start_rto_index, specific_rtos)
        
        log_message(f"\n=== Processing completed for {state_name} ===\n")
        log_message(f"Failed RTOs: {failed_rtos if failed_rtos else 'None'}")
        
        return failed_rtos
        
    except Exception as e:
        log_message(f"Unexpected error in process_rto_wise_data: {str(e)}")
        return ["All RTOs (unexpected error)"]

def process_state(processor, state_name, year, start_rto_index=0, specific_rtos=None):
    """
    Process a single state with RTO processing resumption
    """
    # 1. Configure the state (axis, state, year)
    rto_list = configure_state(processor, state_name, year, specific_rtos)
    if not rto_list:
        return ["All RTOs (configuration failed)"]
    
    # 2. Process RTOs starting from the given index
    failed_rtos = process_rtos(processor, state_name, year, rto_list, start_rto_index)

    log_message(f"Successfully processed: {len(rto_list) - len(failed_rtos)}/{len(rto_list)} RTOs")
    
    return failed_rtos

def configure_state(processor, state_name, year, specific_rtos=None):
    """
    Configure the state (axis, state, year) and return RTO list
    Returns None if configuration fails
    """
    try:
        # Setup axis
        if not processor.setup_axis():
            log_message("Failed to setup axis configuration")
            return None

        # Select state
        if not processor.select_state_primefaces(state_name):
            log_message(f"Failed to select state: {state_name}")
            return None

        # Select year
        if not processor.select_year(year):
            log_message(f"Failed to select year: {year}")
            return None

        # Get RTO list if not provided
        rto_list = specific_rtos or processor.get_all_rtos_for_state()
        if not rto_list:
            log_message("No RTOs found for the selected state")
            return None

        return rto_list

    except Exception as e:
        log_message(f"Error in configure_state: {str(e)}")
        return None

def process_rtos(processor, state_name, year, rto_list, start_index=0):
    """
    Process RTOs starting from the given index
    Returns list of failed RTOs
    """
    failed_rtos = []
    
    for index in range(start_index, len(rto_list)):
        rto = rto_list[index]
        success = False
        max_attempts = 2
        
        for attempt in range(max_attempts):
            try:
                log_message(f"\nProcessing RTO {index + 1}/{len(rto_list)}: {rto} (Attempt {attempt + 1}/{max_attempts})")
                
                # Try to process the current RTO
                if process_single_rto(processor, state_name, year, rto):
                    success = True
                    break
                
                # If we get here, processing failed
                log_message(f"Attempt {attempt + 1} failed for RTO: {rto}")
                
                # On last attempt, add to failed list
                if attempt == max_attempts - 1:
                    failed_rtos.append(rto)
                    log_message(f"Max attempts reached for RTO: {rto}")
                    break
                    
                # Otherwise, try to recover
                log_message("Attempting to recover...")
                if not recover_state(processor, state_name, year):
                    log_message("Recovery failed, marking RTO as failed")
                    failed_rtos.append(rto)
                    break
                    
            except Exception as e:
                log_message(f"Unexpected error processing RTO {rto}: {str(e)}")
                if attempt == max_attempts - 1:
                    failed_rtos.append(rto)
                if not recover_state(processor, state_name, year):
                    break
    
    return failed_rtos

def process_single_rto(processor, state_name, year, rto):
    """Process a single RTO with the given configuration, with 503 error checking and recovery"""
    try:
        # Select RTO
        if not processor.select_specific_rto(rto, state_name, year):
            log_message(f"Failed to select RTO: {rto}")
            return False
        # 503 check after RTO selection
        if processor.check_for_503_error():
            log_message("503 error detected after RTO selection. Attempting recovery...")
            if handle_503_and_recover(processor):
                # Retry RTO selection after recovery
                if not processor.select_specific_rto(rto, state_name, year):
                    log_message(f"Failed to select RTO after 503 recovery: {rto}")
                    return False
            else:
                log_message("503 recovery failed after RTO selection.")
                return False

        # Apply filters
        if not processor.apply_filters():
            log_message("Failed to apply filters")
            return False
        # 503 check after filter application
        if processor.check_for_503_error():
            log_message("503 error detected after filter application. Attempting recovery...")
            if handle_503_and_recover(processor):
                # Retry filter application after recovery
                if not processor.apply_filters():
                    log_message("Failed to apply filters after 503 recovery")
                    return False
            else:
                log_message("503 recovery failed after filter application.")
                return False

        # Download Excel
        if not processor.download_excel_rto(state_name, year, rto):
            log_message("Failed to download Excel")
            return False
        # 503 check after download attempt
        if processor.check_for_503_error():
            log_message("503 error detected after download attempt. Attempting recovery...")
            if handle_503_and_recover(processor):
                # Retry download after recovery
                if not processor.download_excel_rto(state_name, year, rto):
                    log_message("Failed to download Excel after 503 recovery")
                    return False
            else:
                log_message("503 recovery failed after download attempt.")
                return False

        log_message(f"Successfully processed RTO: {rto}")
        return True

    except Exception as e:
        log_message(f"Error in process_single_rto: {str(e)}")
        return False

def recover_state(processor, state_name, year):
    """Recover the state by reinitializing the flow"""
    try:
        log_message("Attempting to recover state...")
        
        # Refresh the browser
        processor.browser.driver.refresh()
        
        # Wait for page to load
        WebDriverWait(processor.browser.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[name='javax.faces.ViewState']"))
        )
        
        # Reinitialize the flow
        if not processor.setup_axis() or \
           not processor.select_state_primefaces(state_name) or \
           not processor.select_year(year):
            log_message("Failed to reinitialize flow after refresh")
            return False
            
        log_message("Successfully recovered state")
        return True
        
    except Exception as e:
        log_message(f"Error in recover_state: {str(e)}")
        return False

if __name__ == "__main__":
    main()
