import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as element_condition
import random

# CUSTOM
def create_random_email(username_char_count=10):
    # letters a-z
    ascii_bounds = (97, 122)
    ger_random_ascii_letter = lambda: chr(random.randint(*ascii_bounds))
    return ''.join(
        [
            ger_random_ascii_letter()
            for _ in range(username_char_count)
        ]) + '@gmail.com'

class CustomEdgeDriver(webdriver.Edge):
    def find_element_until_xpath(self, xpath, timeout=5, raise_over_none=True):
        try:
            return WebDriverWait(self, timeout).until(
                element_condition.presence_of_element_located((By.XPATH, xpath))
                and element_condition.element_to_be_clickable((By.XPATH, xpath))
            )
        except TimeoutException:
            print('timed out waiting for element to load')
            if raise_over_none:
                raise TimeoutException
            return None


# create a driver for new session
@pytest.fixture
def driver():
    custom_driver = CustomEdgeDriver()
    custom_driver.maximize_window()
    yield custom_driver
    custom_driver.close()
    custom_driver.quit()
    print('Driver closed')


# scope='session' makes random email one time
@pytest.fixture(scope='session')
def credentials():
    return {'email': create_random_email(), 'password': 'slaptas1'}

@pytest.mark.order(1)
def test_create_account(credentials, driver):
    driver.get('https://demowebshop.tricentis.com/')
    # click login
    driver.find_element_until_xpath(
        '//a[@href="/login"]').click()
    # click register
    driver.find_element_until_xpath(
        '//div[descendant::text()="New Customer"]\
        /descendant::input[@value="Register"]'
        ).click()
    # click male gender
    driver.find_element_until_xpath(
        '(//input[@type="radio"])[1]').click()
    # input first name
    driver.find_element_until_xpath(
        '//input[@name="FirstName"]').send_keys('Ignas')
    # input last name
    driver.find_element_until_xpath(
        '//input[@name="LastName"]').send_keys('Jogminas')
    # input email
    driver.find_element_until_xpath(
        '//input[@name="Email"]').send_keys(credentials['email'])
    # input password
    driver.find_element_until_xpath(
        '//input[@name="Password"]').send_keys(credentials['password'])
    # input confirm password
    driver.find_element_until_xpath(
        '//input[@name="ConfirmPassword"]').send_keys(credentials['password'])
    # click register
    driver.find_element_until_xpath(
        '//input[@value="Register"]').click()
    # click continue
    driver.find_element_until_xpath(
        '//input[@value="Continue"]').click()
    print(credentials)
    assert True


@pytest.mark.order(2)
@pytest.mark.parametrize('data_path', ['data1.txt', 'data2.txt'])
def test_same_account_parallel_buying(credentials, driver, data_path):
    driver.get('https://demowebshop.tricentis.com/')
    # click login
    driver.find_element_until_xpath(
        '//a[@href="/login"]').click()
    # input email
    driver.find_element_until_xpath(
        '//input[@name="Email"]').send_keys(credentials['email'])
    # input password
    driver.find_element_until_xpath(
        '//input[@name="Password"]').send_keys(credentials['password'])
    print(credentials)
    # click log in
    driver.find_element_until_xpath(
        '//input[@value="Log in"]').click()
    # click digital downloads
    driver.find_element_until_xpath(
        '//a[@href="/digital-downloads"]').click()
    cart = driver.find_element_until_xpath(
        '//a[@href="/cart"]')
    # click add to cart to items specified in cart
    with open(data_path, 'r') as read_file:
        last_cart_quantity = 0
        for line in read_file.readlines():
            print(f'LINE: {line.strip()}')
            driver.find_element_until_xpath(
                f'//div[@class="details"\
                and descendant::text()="{line.strip()}"]\
                /descendant::input[@value="Add to cart"]').click()
            # wait because of delay between adding to cart and cart quantity
            last_cart_quantity += 1
            cart_quantity = CustomEdgeDriver.find_element_until_xpath(cart,
                f'./*[@class="cart-qty" and contains(text(), "{last_cart_quantity}")]')
            print(f'Cart quantity: {cart_quantity.text}')
    cart.click()
    # click terms of service
    driver.find_element_until_xpath(
        '//input[@name="termsofservice"]').click()
        # click checkout
    driver.find_element_until_xpath(
        '//button[@name="checkout"]').click()
    select_country = driver.find_element_until_xpath(
        '//select[@name="BillingNewAddress.CountryId"]', raise_over_none=False)
    # if select country option is present create new billing info
    if select_country:
        # select country
        Select(select_country).select_by_visible_text('Canada')
        # input city
        driver.find_element_until_xpath(
            '//input[@name="BillingNewAddress.City"]').send_keys('Yes')
        # input address
        driver.find_element_until_xpath(
            '//input[@name="BillingNewAddress.Address1"]').send_keys('Yes')
        # input zip postal code
        driver.find_element_until_xpath(
            '//input[@name="BillingNewAddress.ZipPostalCode"]').send_keys('Yes')
        # input phone number
        driver.find_element_until_xpath(
            '//input[@name="BillingNewAddress.PhoneNumber"]').send_keys('Yes')
    else:
        # confirm that auto billing address is present
        driver.find_element_until_xpath('//select[@id="billing-address-select"]')
        # click through fields if the first element in tuple is highlighted
    checkout_steps = (
        ('Billing address', 'Continue'),
        ('Payment method', 'Continue'),
        ('Payment information', 'Continue'),
        ('Confirm order', 'Confirm'))
    for step, confirmation in checkout_steps:
        driver.find_element_until_xpath(f'//li[contains(@class, "active")\
            and descendant::text()="{step}"]\
            /descendant::input[@value="{confirmation}"]').click()
    # confirm order was made if "order number" text is present
    driver.find_element_until_xpath(f'//li[contains(text(), "Order number")]')
    assert True