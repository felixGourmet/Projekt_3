from playwright.sync_api import Page, sync_playwright
import pytest
import time

@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        yield page
        browser.close()


def test_raspberry_cena(page: Page):
    # Otevřít stránku RPishop
    page.goto("https://rpishop.cz/")

    # Odmítnout cookies – hledání tlačítka podle textu
    try:
        cookies_button = page.get_by_role("button", name="Zamítnout")
        if cookies_button.is_visible():
            cookies_button.click()
            time.sleep(1)
    except:
        pass

    # Najít vyhledávací pole podle ID a vyhledat produkt
    search_input = page.locator("#dgwt-wcas-search-input-1")
    search_input.click()
    search_input.fill("Raspberry Pi 5 - 8GB RAM")
    search_input.press("Enter")

    # Počkat na načtení výsledků a kliknout na první produkt
    page.wait_for_selector("#products_top a[href*='raspberry-pi-5-8gb']")
    page.locator("#products_top a[href*='raspberry-pi-5-8gb']").first.click()

    # Počkat na zobrazení ceny (s DPH)
    page.wait_for_selector(".vat .woocommerce-Price-amount")

    # Získat text ceny
    price_text = page.locator(".vat .woocommerce-Price-amount").inner_text()
    print("Produkt nyní stojí:", price_text)

    # Vzít text před čárkou a nechat v něm jen čísla
    price_text = price_text.split(",")[0]  
    price_value = int(''.join(c for c in price_text if c.isdigit()))

    # Porovnání ceny
    if price_value < 2029:
        print("Slevněno!")
    elif price_value > 2029:
        print("Dražší!")
    else:
        print("Žádná změna..")

    # Ověřit, že jsme na stránce správného produktu
    assert "Raspberry Pi 5" in page.title()
