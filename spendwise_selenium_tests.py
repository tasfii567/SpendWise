"""
SpendWise — Selenium Automation Test Suite
==========================================
Requirements:
    pip install selenium webdriver-manager

Usage:
    python spendwise_selenium_tests.py

Notes:
    - Google Sign-In cannot be automated (Google blocks bots).
      These tests inject a mock user into localStorage before the app loads,
      bypassing the login screen entirely — this is standard practice.
    - Replace APP_URL with your actual Vercel URL.
    - Tests run in headless Chrome by default. Set HEADLESS = False to watch.
"""

import time
import json
import unittest
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ── Config ────────────────────────────────────────────────────────────────────
APP_URL  = "https://your-app.vercel.app"   # <-- change this
HEADLESS = True                             # set False to watch the browser
TIMEOUT  = 10                              # seconds to wait for elements

# Mock user — mirrors the shape saved by onGoogleCred()
MOCK_USER = json.dumps({
    "name":  "Test User",
    "email": "testuser@gmail.com",
    "pic":   "",
    "id":    "test_user_123"
})

TODAY      = date.today().strftime("%Y-%m-%d")
YESTERDAY  = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
TOMORROW   = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")


# ── Helpers ───────────────────────────────────────────────────────────────────
def make_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=390,844")     # mobile viewport
    opts.add_argument("--disable-notifications")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts
    )
    driver.implicitly_wait(TIMEOUT)
    return driver


def inject_user(driver, clear_data=True):
    """Open the app, inject a mock logged-in user, then reload."""
    driver.get(APP_URL)
    time.sleep(1)
    uid = json.loads(MOCK_USER)["id"]
    if clear_data:
        driver.execute_script(
            f"localStorage.setItem('sw_u', arguments[0]);"
            f"localStorage.removeItem('sw_{uid}');",
            MOCK_USER
        )
    else:
        driver.execute_script("localStorage.setItem('sw_u', arguments[0]);", MOCK_USER)
    driver.refresh()
    # Wait for app to be visible (splash fades after ~1.8s)
    WebDriverWait(driver, 6).until(
        EC.visibility_of_element_located((By.ID, "app"))
    )


def wait(driver, by, value, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def click(driver, by, value):
    el = wait(driver, by, value)
    el.click()
    return el


def fill(driver, field_id, value):
    el = driver.find_element(By.ID, field_id)
    el.clear()
    el.send_keys(value)
    return el


def get_text(driver, element_id):
    return driver.find_element(By.ID, element_id).text


def add_transaction(driver, desc, amount, tx_type="exp", date_val=None):
    """Helper: fill in and submit the Add Transaction form."""
    fill(driver, "f-desc", desc)
    # Clear and type raw number (no formatting)
    amt_el = driver.find_element(By.ID, "f-amt")
    amt_el.clear()
    amt_el.send_keys(str(amount))
    if date_val:
        driver.execute_script(
            f"document.getElementById('f-date').value = '{date_val}';"
        )
    if tx_type == "inc":
        driver.find_element(By.ID, "t-inc").click()
    else:
        driver.find_element(By.ID, "t-exp").click()
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(0.5)


# ── Test Cases ────────────────────────────────────────────────────────────────
class TestSplashScreen(unittest.TestCase):
    """TC-SW-01 — Splash screen appears then fades."""

    def setUp(self):
        self.driver = make_driver()

    def tearDown(self):
        self.driver.quit()

    def test_splash_visible_then_hidden(self):
        self.driver.get(APP_URL)
        splash = wait(self.driver, By.ID, "splash")
        self.assertTrue(splash.is_displayed(), "Splash should be visible on load")
        # After ~2.5s the splash should be gone
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.ID, "splash"))
        )

    def test_login_screen_shown_when_no_user(self):
        self.driver.get(APP_URL)
        # Clear any saved user so login shows
        self.driver.execute_script("localStorage.removeItem('sw_u');")
        self.driver.refresh()
        time.sleep(2.5)
        login = self.driver.find_element(By.ID, "login")
        self.assertIn("show", login.get_attribute("class"),
                      "Login screen should appear when no user in localStorage")


class TestAddTransaction(unittest.TestCase):
    """TC-SW-05 to TC-SW-12 — Add transaction form."""

    def setUp(self):
        self.driver = make_driver()
        inject_user(self.driver, clear_data=True)

    def tearDown(self):
        self.driver.quit()

    def test_add_valid_expense(self):
        add_transaction(self.driver, "Groceries", 500, "exp", TODAY)
        btn = self.driver.find_element(By.ID, "add-btn")
        self.assertIn("Added", btn.text, "Button should show '✓ Added!' after submission")

    def test_add_valid_income(self):
        add_transaction(self.driver, "Salary", 50000, "inc", TODAY)
        btn = self.driver.find_element(By.ID, "add-btn")
        self.assertIn("Added", btn.text)

    def test_empty_description_shows_error(self):
        # Leave description blank
        amt_el = self.driver.find_element(By.ID, "f-amt")
        amt_el.clear()
        amt_el.send_keys("100")
        self.driver.find_element(By.ID, "add-btn").click()
        time.sleep(0.3)
        desc_el = self.driver.find_element(By.ID, "f-desc")
        self.assertIn("err", desc_el.get_attribute("class"),
                      "Description field should have 'err' class when empty")

    def test_empty_amount_shows_error(self):
        fill(self.driver, "f-desc", "Test")
        self.driver.find_element(By.ID, "f-amt").clear()
        self.driver.find_element(By.ID, "add-btn").click()
        time.sleep(0.3)
        amt_el = self.driver.find_element(By.ID, "f-amt")
        self.assertIn("err", amt_el.get_attribute("class"),
                      "Amount field should have 'err' class when empty")

    def test_future_date_blocked(self):
        fill(self.driver, "f-desc", "Future payment")
        amt_el = self.driver.find_element(By.ID, "f-amt")
        amt_el.clear()
        amt_el.send_keys("100")
        driver = self.driver
        driver.execute_script(
            f"document.getElementById('f-date').value = '{TOMORROW}';"
        )
        # Handle the alert that appears
        driver.find_element(By.ID, "add-btn").click()
        time.sleep(0.5)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            self.assertIn("not allowed", alert_text.lower(),
                          "Alert should warn about future dates")
        except Exception:
            self.fail("Expected an alert for future date but none appeared")

    def test_description_cleared_after_add(self):
        add_transaction(self.driver, "Lunch", 150, "exp", TODAY)
        time.sleep(1.5)
        desc_val = self.driver.find_element(By.ID, "f-desc").get_attribute("value")
        self.assertEqual(desc_val, "", "Description field should be cleared after adding")

    def test_summary_updates_after_expense(self):
        # Get initial expense value
        exp_before_text = get_text(self.driver, "s-exp").replace(",", "")
        exp_before = float(exp_before_text) if exp_before_text else 0.0
        add_transaction(self.driver, "Transport", 200, "exp", TODAY)
        time.sleep(0.5)
        exp_after_text = get_text(self.driver, "s-exp").replace(",", "")
        exp_after = float(exp_after_text)
        self.assertAlmostEqual(
            exp_after, exp_before + 200, delta=1,
            msg="Expense total should increase by the added amount"
        )

    def test_summary_updates_after_income(self):
        inc_before = float(get_text(self.driver, "s-inc").replace(",", "") or 0)
        add_transaction(self.driver, "Freelance", 3000, "inc", TODAY)
        time.sleep(0.5)
        inc_after = float(get_text(self.driver, "s-inc").replace(",", ""))
        self.assertAlmostEqual(inc_after, inc_before + 3000, delta=1)


class TestHistory(unittest.TestCase):
    """TC-SW-13 to TC-SW-17 — History tab."""

    def setUp(self):
        self.driver = make_driver()
        inject_user(self.driver, clear_data=True)
        # Pre-add transactions
        add_transaction(self.driver, "Salary", 20000, "inc", TODAY)
        add_transaction(self.driver, "Rent",   8000,  "exp", TODAY)
        # Switch to history tab
        self.driver.find_element(By.XPATH,
            "//button[contains(text(),'History')]").click()
        time.sleep(0.3)

    def tearDown(self):
        self.driver.quit()

    def test_transactions_appear_in_history(self):
        items = self.driver.find_elements(By.CLASS_NAME, "txi")
        self.assertGreaterEqual(len(items), 2, "History should show added transactions")

    def test_filter_income_only(self):
        self.driver.find_element(By.XPATH,
            "//div[@class='fbts']//button[text()='In']").click()
        time.sleep(0.3)
        items = self.driver.find_elements(By.CSS_SELECTOR, ".txic.inc")
        exp_items = self.driver.find_elements(By.CSS_SELECTOR, ".txic.exp")
        self.assertGreater(len(items), 0, "Should show income transactions")
        self.assertEqual(len(exp_items), 0, "Should NOT show expense transactions")

    def test_filter_expense_only(self):
        self.driver.find_element(By.XPATH,
            "//div[@class='fbts']//button[text()='Out']").click()
        time.sleep(0.3)
        items = self.driver.find_elements(By.CSS_SELECTOR, ".txic.exp")
        inc_items = self.driver.find_elements(By.CSS_SELECTOR, ".txic.inc")
        self.assertGreater(len(items), 0)
        self.assertEqual(len(inc_items), 0)

    def test_delete_transaction(self):
        count_before = len(self.driver.find_elements(By.CLASS_NAME, "txi"))
        self.driver.find_element(By.CLASS_NAME, "txdel").click()
        time.sleep(0.4)
        count_after = len(self.driver.find_elements(By.CLASS_NAME, "txi"))
        self.assertEqual(count_after, count_before - 1,
                         "One transaction should be removed after delete")


class TestGoals(unittest.TestCase):
    """TC-SW-23 to TC-SW-26 — Goals tab."""

    def setUp(self):
        self.driver = make_driver()
        inject_user(self.driver, clear_data=True)
        self.driver.find_element(By.XPATH,
            "//button[contains(text(),'Goals')]").click()
        time.sleep(0.3)

    def tearDown(self):
        self.driver.quit()

    def test_add_valid_goal(self):
        fill(self.driver, "g-name", "New Phone")
        amt = self.driver.find_element(By.ID, "g-target")
        amt.clear(); amt.send_keys("30000")
        rate = self.driver.find_element(By.ID, "g-rate")
        rate.clear(); rate.send_keys("10")
        # Select Work category
        work_cb = self.driver.find_element(
            By.XPATH, "//input[@value='💼 Work']")
        if not work_cb.is_selected():
            work_cb.click()
        self.driver.find_element(By.CLASS_NAME, "gadd-btn").click()
        time.sleep(0.4)
        goals = self.driver.find_elements(By.CLASS_NAME, "gitem")
        self.assertGreater(len(goals), 0, "Goal should appear in the list")

    def test_add_goal_no_category_shows_alert(self):
        fill(self.driver, "g-name", "Vacation")
        amt = self.driver.find_element(By.ID, "g-target")
        amt.clear(); amt.send_keys("50000")
        rate = self.driver.find_element(By.ID, "g-rate")
        rate.clear(); rate.send_keys("5")
        # Deselect all checkboxes
        for cb in self.driver.find_elements(By.CSS_SELECTOR, "#g-cats input[type=checkbox]"):
            if cb.is_selected():
                cb.click()
        self.driver.find_element(By.CLASS_NAME, "gadd-btn").click()
        time.sleep(0.3)
        try:
            alert = self.driver.switch_to.alert
            self.assertIn("category", alert.text.lower())
            alert.accept()
        except Exception:
            self.fail("Expected alert when no category selected")

    def test_delete_goal(self):
        # Add a goal first
        fill(self.driver, "g-name", "Laptop")
        amt = self.driver.find_element(By.ID, "g-target")
        amt.clear(); amt.send_keys("80000")
        rate = self.driver.find_element(By.ID, "g-rate")
        rate.clear(); rate.send_keys("15")
        work_cb = self.driver.find_element(By.XPATH, "//input[@value='💼 Work']")
        if not work_cb.is_selected():
            work_cb.click()
        self.driver.find_element(By.CLASS_NAME, "gadd-btn").click()
        time.sleep(0.4)
        count_before = len(self.driver.find_elements(By.CLASS_NAME, "gitem"))
        # Delete it
        self.driver.find_element(By.CLASS_NAME, "gdel").click()
        time.sleep(0.3)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(0.3)
        count_after = len(self.driver.find_elements(By.CLASS_NAME, "gitem"))
        self.assertLess(count_after, count_before, "Goal count should decrease after delete")


class TestDataPersistence(unittest.TestCase):
    """TC-SW-27 — Data persists after page reload."""

    def setUp(self):
        self.driver = make_driver()

    def tearDown(self):
        self.driver.quit()

    def test_transaction_persists_after_reload(self):
        inject_user(self.driver, clear_data=True)
        add_transaction(self.driver, "Persistent Item", 999, "exp", TODAY)
        time.sleep(0.8)
        # Reload page (don't re-inject user — test real persistence)
        self.driver.refresh()
        WebDriverWait(self.driver, 6).until(
            EC.visibility_of_element_located((By.ID, "app"))
        )
        # Switch to history
        self.driver.find_element(By.XPATH,
            "//button[contains(text(),'History')]").click()
        time.sleep(0.5)
        page_source = self.driver.page_source
        self.assertIn("Persistent Item", page_source,
                      "Transaction description should survive a page reload")


# ── Runner ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nSpendWise Selenium Test Suite")
    print(f"Target: {APP_URL}")
    print(f"Mode:   {'Headless' if HEADLESS else 'Browser visible'}")
    print("-" * 50)
    unittest.main(verbosity=2)
