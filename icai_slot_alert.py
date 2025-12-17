#!/usr/bin/env python3
"""
ICAI Course Slot Availability Monitor
======================================
This script monitors ICAI course slot availability and sends Telegram notifications
when slots become available.

Author: Cloud Automation Engineer
License: Free to use
"""

import os
import sys
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
WEBSITE_URL = "https://icaionlineregistration.org/launchbatchdetail.aspx"
REGION = "Southern"
POU = "HYDERABAD"
COURSES_TO_MONITOR = [
    "Advanced (ICITSS) MCS Course",
    "ICITSS - Information Technology",
    "ICITSS - Orientation Course"
]

# Telegram configuration (from environment variables / GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Validate Telegram credentials
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set as environment variables")
    sys.exit(1)


def send_telegram_notification(course_name: str) -> bool:
    """
    Send Telegram notification when a slot is available.
    
    Args:
        course_name: Name of the course with available slot
        
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    message = f"🚨 ICAI SLOT OPEN!\n\nCourse: {course_name}\nPOU: Hyderabad\n\nBook NOW!"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Telegram notification sent successfully for {course_name}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send Telegram notification: {e}")
        return False


def setup_chrome_driver():
    """
    Setup headless Chrome driver for GitHub Actions (Linux environment).
    
    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    chrome_options = Options()
    
    # Headless mode for server environments
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Additional options for stability
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    try:
        # Chrome driver will be auto-detected or use system PATH
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("✅ Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"❌ Failed to initialize Chrome driver: {e}")
        raise


def check_course_availability(driver, course_name: str) -> bool:
    """
    Check if a specific course has available slots.
    
    Args:
        driver: Selenium WebDriver instance
        course_name: Name of the course to check
        
    Returns:
        bool: True if slots are available, False otherwise
    """
    try:
        # Wait for page to load with increased timeout
        wait = WebDriverWait(driver, 30)
        
        # Select Region dropdown
        logger.info(f"Selecting Region: {REGION}")
        region_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ddlRegion"))
        )
        region_select = Select(region_dropdown)
        region_select.select_by_visible_text(REGION)
        time.sleep(3)  # Wait for dependent dropdowns to populate
        
        # Select POU dropdown
        logger.info(f"Selecting POU: {POU}")
        pou_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ddlPOU"))
        )
        pou_select = Select(pou_dropdown)
        pou_select.select_by_visible_text(POU)
        time.sleep(3)  # Wait for course dropdown to populate
        
        # Select Course dropdown
        logger.info(f"Selecting Course: {course_name}")
        course_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ddlCourse"))
        )
        course_select = Select(course_dropdown)
        course_select.select_by_visible_text(course_name)
        time.sleep(3)
        
        # Click "Get List" button
        logger.info("Clicking 'Get List' button")
        get_list_button = wait.until(
            EC.element_to_be_clickable((By.ID, "btnGetList"))
        )
        get_list_button.click()
        
        # Wait for results to load (wait for table or message to appear)
        time.sleep(5)
        
        # Check for "No Batch Available" message
        try:
            # Look for common "no batch" indicators
            page_text = driver.page_source.lower()
            
            # Check for "no batch available" or similar messages
            no_batch_indicators = [
                "no batch available",
                "no batch",
                "no records found",
                "batch not available"
            ]
            
            for indicator in no_batch_indicators:
                if indicator in page_text:
                    logger.info(f"❌ No slots available for {course_name}")
                    return False
            
            # Check if there's a table with batch data
            try:
                # Look for table rows (batches)
                batch_rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
                if len(batch_rows) > 1:  # More than just header row
                    logger.info(f"✅ Slots available for {course_name}!")
                    return True
            except NoSuchElementException:
                pass
            
            # If we can't find clear indicators, check for any data table
            try:
                data_table = driver.find_element(By.CSS_SELECTOR, "table")
                if data_table:
                    # Check if table has meaningful content
                    table_text = data_table.text.strip()
                    if table_text and len(table_text) > 50:  # Has substantial content
                        logger.info(f"✅ Slots available for {course_name}!")
                        return True
            except NoSuchElementException:
                pass
            
            # Default: assume no slots if we can't find clear evidence
            logger.warning(f"⚠️ Could not determine availability for {course_name}, assuming no slots")
            return False
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
            
    except TimeoutException as e:
        logger.error(f"Timeout while checking {course_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking {course_name}: {e}")
        return False


def main():
    """
    Main function to monitor ICAI course slots.
    """
    logger.info("=" * 60)
    logger.info("ICAI Course Slot Monitor - Starting Check")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    driver = None
    available_courses = []
    
    try:
        # Setup Chrome driver
        driver = setup_chrome_driver()
        
        # Check each course
        for course in COURSES_TO_MONITOR:
            logger.info(f"\n--- Checking: {course} ---")
            try:
                # Navigate to the website (fresh page for each course)
                logger.info(f"Navigating to: {WEBSITE_URL}")
                driver.get(WEBSITE_URL)
                time.sleep(5)  # Wait for page to load completely
                
                if check_course_availability(driver, course):
                    available_courses.append(course)
                    # Send notification immediately
                    send_telegram_notification(course)
                    time.sleep(1)  # Small delay between notifications
            except Exception as e:
                logger.error(f"Error checking {course}: {e}")
                logger.info("Continuing with next course...")
                continue
        
        # Summary
        if available_courses:
            logger.info(f"\n✅ Found {len(available_courses)} course(s) with available slots!")
            logger.info(f"Available courses: {', '.join(available_courses)}")
        else:
            logger.info("\n❌ No slots available for any monitored courses")
            
    except WebDriverException as e:
        logger.error(f"WebDriver error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        if driver:
            try:
                driver.quit()
                logger.info("✅ Chrome driver closed successfully")
            except Exception as e:
                logger.warning(f"Warning while closing driver: {e}")
    
    logger.info("=" * 60)
    logger.info("ICAI Course Slot Monitor - Check Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()


