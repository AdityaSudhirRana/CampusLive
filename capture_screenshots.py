"""
Script to launch CampusLive, capture all desired screenshots using headless Chrome,
and optionally embed them into the documentation.
"""
import os
import sys
import time
import threading
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import app factory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campuslive import create_app
from campuslive.seed import seed

import socket
def pick_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

PORT = pick_port()
BASE_URL = f"http://127.0.0.1:{PORT}"
SHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SHOTS_DIR, exist_ok=True)

def run_server():
    app = create_app()
    app.run(host="127.0.0.1", port=PORT, threaded=True, use_reloader=False)

def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,920")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1440, 920)
    return driver

def snap(driver, name, delay=1.0):
    time.sleep(delay)
    path = os.path.join(SHOTS_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"Captured: {name}.png ({os.path.getsize(path)} bytes)")
    return path

def main():
    print("Ensuring database has clean seed...")
    seed(force=True)

    print(f"Starting server in background on port {PORT}...")
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2)

    print("Launching headless Chrome...")
    driver = get_driver()
    wait = WebDriverWait(driver, 10)

    try:
        # --- 1. Public Landing Page ---
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hero")))
        snap(driver, "fig01_landing_page", 1.5)

        # --- 2. Student Sign-Up Form ---
        driver.get(f"{BASE_URL}/#signup")
        wait.until(EC.presence_of_element_located((By.NAME, "college_code")))
        cc_input = driver.find_element(By.NAME, "college_code")
        cc_input.send_keys("COL001")
        # trigger change/input event
        driver.execute_script("document.getElementById('cc').dispatchEvent(new Event('input'));")
        time.sleep(1)
        snap(driver, "fig02_student_signup", 1.0)

        # Helper to logout
        def logout():
            try:
                driver.execute_script("""
                    fetch('/api/logout', {method: 'POST'})
                        .then(() => {
                            document.cookie = 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
                            location.href = '/#signin';
                            location.reload();
                        });
                """)
                time.sleep(1.5)
            except Exception:
                driver.delete_all_cookies()
                driver.get(f"{BASE_URL}/#signin")
                time.sleep(1.0)

        # Helper to login
        def login(username, password="demo123"):
            logout()
            driver.get(f"{BASE_URL}/#signin")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            u_el = driver.find_element(By.NAME, "username")
            u_el.clear()
            u_el.send_keys(username)
            p_el = driver.find_element(By.NAME, "password")
            p_el.clear()
            p_el.send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "form.mform button").click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rail")))
            time.sleep(1.5)

        # Helper to click tab
        def click_tab(tab_name):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//aside[@class='rail']//nav//button[contains(text(), '{tab_name}')]")))
            btn.click()
            time.sleep(1.2)

        # --- 3. Principal Live Campus Monitoring Dashboard ---
        login("principal")
        snap(driver, "fig03_principal_live_board", 1.5)

        # --- 4. Lecture Detail Modal ---
        # Click on the first live lecture row
        live_row = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".brow.live[data-detail]")))
        live_row.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dialog")))
        time.sleep(1.0)
        snap(driver, "fig04_lecture_detail_modal", 1.0)
        
        # Close modal
        driver.find_element(By.CSS_SELECTOR, "button[data-close]").click()
        time.sleep(0.5)

        # --- 5. Department & HOD Management (Admin) ---
        click_tab("Departments")
        snap(driver, "fig05_department_hod_management", 1.0)

        # --- 6. Faculty Directory & Live Teaching Status ---
        click_tab("Teachers")
        snap(driver, "fig06_faculty_directory_live", 1.0)

        # --- 7. Institutional Reports & Analytics ---
        click_tab("Reports")
        snap(driver, "fig07_reports_analytics", 1.0)

        # --- 8. Central Activity Audit Log ---
        click_tab("Logs")
        snap(driver, "fig08_activity_audit_log", 1.0)

        # --- 9. Teacher Active Lecture Controller (Asst. Prof. Rohit Sahu) ---
        login("rohit_sahu")
        click_tab("My lectures")
        snap(driver, "fig09_teacher_live_controller", 1.5)

        # --- 10. Lecture Scheduling Modal ---
        sch_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Schedule lecture')]")))
        sch_btn.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dialog")))
        time.sleep(0.8)
        snap(driver, "fig10_lecture_schedule_modal", 1.0)
        driver.find_element(By.CSS_SELECTOR, "button[data-close]").click()
        time.sleep(0.5)

        # --- 11. Weekly Timetable Slot Manager ---
        click_tab("Weekly timetable")
        snap(driver, "fig11_weekly_timetable", 1.0)

        # --- 12. HOD Substitutions & Rooms (Asst. Prof. Pradnya Kharade) ---
        login("pradnya_k")
        click_tab("Substitutions")
        snap(driver, "fig12_hod_substitutions", 1.2)

        # --- 13. Student Live Board & PIN Check-in (Aditya Rana) ---
        login("student")
        click_tab("Live now")
        snap(driver, "fig13_student_live_checkin", 1.5)

        # --- 14. Student Attendance History ---
        click_tab("History")
        snap(driver, "fig14_student_history", 1.0)

        # --- 15. User Profile & Security Settings ---
        click_tab("Account")
        snap(driver, "fig15_user_profile", 1.0)

        print("\nAll 15 screenshots successfully captured!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
