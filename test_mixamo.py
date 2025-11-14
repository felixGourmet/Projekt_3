from playwright.sync_api import sync_playwright, Page
import pytest
import time


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False, slow_mo=250)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()


# Funkce pro ovládání akcí na Popup stránkách
def kontrola_popup(page: Page):

    # Popup - Learn & Support (kliknutí na dropdown, čekání na selektor Learn & Support)
    print("Otevírám Learn & Support jako POPUP…")
    page.locator("li.dropdown").click()
    page.wait_for_selector("li.dropdown a:has-text('Learn & Support')", timeout=8000)

    context = page.context
    before = context.pages

    # Otevřít odkaz v nové záložce 
    page.keyboard.down("Shift")
    page.locator("li.dropdown a:has-text('Learn & Support')").click()
    page.keyboard.up("Shift")

    time.sleep(1.5)

    after = context.pages
    popup = [p for p in after if p not in before][0]

    print("Popup otevřen:", popup.url)

    # Popup - Zvolení češtiny
    print("Čekám na panel s výběrem jazyka…")
    popup.wait_for_selector("#localeModal a:has-text('Česká republika')", timeout=10000)

    print("Klikám na Česká republika…")
    popup.locator("#localeModal a:has-text('Česká republika')").click()

    # Popup - Odmítnutí cookies Adobe
    print("Odmítám cookies na Adobe stránce…")
    try:
        popup.wait_for_selector("button#onetrust-reject-all-handler", timeout=6000)
        popup.click("button#onetrust-reject-all-handler")
        print("Adobe cookies odmítnuty.")
    except:
        print("Cookies na Adobe se nezobrazily.")

    # Popup - Scrollování stránky
    print("Scrolluji popup…")
    for _ in range(12):
        popup.mouse.wheel(0, 650)
        time.sleep(0.35)

    # Popup - Zavření záložky
    print("Zavírám popup…")
    popup.close()
    time.sleep(1)

    print("Vrácím se zpět na Mixamo…")
    page.reload()
    time.sleep(1.5)



# Funkce pro ovládání akcí na Mixamo stránkách
def kontrola_mixamo(page: Page):

    # Ovládání tlačítka Characters
    print("Otevírám záložku Characters…")
    page.get_by_role("link", name="Characters").click()

    page.wait_for_selector("input[placeholder='Search']", timeout=15000)
    time.sleep(0.8)

    # Hledání postavy "Erika Archer"
    print("Vyhledávám Erika Archer…")

    s = page.locator("input[placeholder='Search']")
    s.fill("Erika Archer")
    s.press("Enter")

    page.wait_for_selector("p:text('Erika Archer')", timeout=10000)
    page.locator("p:text('Erika Archer')").first.click()

    page.wait_for_selector(".product-preview-holder", timeout=15000)
    print("Postava načtena.")
    time.sleep(1)

    # Ovladání tlačítka Animations
    print("Otevírám Animations…")
    page.get_by_role("link", name="Animations").click()

    page.wait_for_selector("input[placeholder='Search']", timeout=15000)

    # Hledání animace "Front Twist Flip"
    print("Vyhledávám Front Twist Flip…")

    a = page.locator("input[placeholder='Search']")
    a.fill("Front Twist Flip")
    a.press("Enter")

    page.wait_for_selector("p:text('Front Twist Flip')", timeout=10000)
    item = page.locator("p:text('Front Twist Flip')").first

    item.hover()
    time.sleep(1.2)

    item.click()

    page.wait_for_selector(".product-preview-holder", timeout=15000)
    time.sleep(1)

    # Najít a nastavit Overdrive na 0
    print("Nastavuju Overdrive na 0…")
    over = page.locator("input[name='Overdrive']")
    over.fill("0")
    over.press("Enter")

    time.sleep(1.2)

    # Zapnout sledování kamery
    print("Zapínám Follow Camera…")
    page.click(".fa-video-camera")

    # Závěr - sledování animace a následné ukončení testu
    print("Sleduji animaci…")
    time.sleep(6)

    print("Test byl dokončen")



# Funkce pro spuštění testování Mixamo a Popup 
def test_mixamo_popup(page: Page):

    print("Otevírám Mixamo…")
    page.goto("https://www.mixamo.com/#/", timeout=60000)

    # Cookies Mixamo
    print("Čekám na banner cookies…")
    try:
        page.wait_for_selector("button#onetrust-reject-all-handler", timeout=6000)
        page.click("button#onetrust-reject-all-handler")
        print("Cookies odmítnuty.")
    except:
        print("Cookies banner se neobjevil.")

    # Zavolání popup funkce
    kontrola_popup(page)

    # Zavolání hlavní Mixamo funkce
    kontrola_mixamo(page)

    print("Test byl dokončen.")
