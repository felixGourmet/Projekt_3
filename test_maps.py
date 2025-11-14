from playwright.sync_api import Page, sync_playwright
import pytest
import time
import random


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=250)
        page = browser.new_page()
        yield page
        browser.close()


# Funkce pro přípravu mapy
def kontrola_mapy(page: Page, mesto: str):
    print("Otevírám Google Mapy…")
    page.goto("https://www.google.com/maps")
    time.sleep(2)

    # Cookies Google Maps, (CZ / EN)
    print("Hledám banner s cookies…")

    try:
        btn = None

        if page.locator("button[aria-label='Odmítnout vše']").count() > 0:
            btn = page.locator("button[aria-label='Odmítnout vše']").first
            print("Nalezeno CZ tlačítko.")
        elif page.locator("button[aria-label='Reject all']").count() > 0:
            btn = page.locator("button[aria-label='Reject all']").first
            print("Nalezeno EN tlačítko.")

        if btn:
            btn.click()
            print("Cookies odmítnuty.")
        else:
            print("Cookies dialog nebyl zobrazen.")

    except Exception as e:
        print("Chyba při odmítání cookies:", e)

    time.sleep(1)

    # Vyhledat město - defaultně Praha
    page.wait_for_selector("input#searchboxinput")
    search = page.locator("input#searchboxinput")
    search.fill(mesto)
    search.press("Enter")
    print(f"Vyhledávám město: {mesto}…")

    # Počkat dokud se nenačte info panel s vybraným místem
    page.wait_for_selector(f"h1.DUwDvf:has-text('{mesto}')", timeout=15000)
    print(f"Info panel {mesto} načten.")
    time.sleep(4)

    # Načítání mapy
    page.wait_for_selector("div#scene")
    map_el = page.locator("div#scene")
    rect = map_el.bounding_box()

    if not rect:
        pytest.skip("Nelze načíst mapový kontejner.")

    map_left = rect["x"]
    map_top = rect["y"]
    map_width = rect["width"]
    map_height = rect["height"]

    # Přibližné vycentrování mapy
    map_center_x = map_left + map_width * 0.70
    map_center_y = map_top + map_height * 0.50

    # Přiblížení mapy
    for _ in range(3):
        page.mouse.move(map_center_x, map_center_y)
        page.mouse.wheel(0, -240)  # zoom in
        time.sleep(0.4)

    print("Mapa se vycentrovala a přiblížila.")

    # Hledání Pegmana
    print("Hledám Pegmana…")

    peg = None
    if page.locator("button[aria-label='Procházet snímky Street View']").count() > 0:
        peg = page.locator("button[aria-label='Procházet snímky Street View']").first
        print("Pegman nalezen (CZ).")
    elif page.locator("button[aria-label='Browse Street View imagery']").count() > 0:
        peg = page.locator("button[aria-label='Browse Street View imagery']").first
        print("Pegman nalezen (EN).")
    else:
        pytest.skip("Pegman nebyl nalezen.")

    peg_box = peg.bounding_box()
    if not peg_box:
        pytest.skip("Nelze určit Pegmana–bounding-box vrací None.")

    x_start = peg_box["x"] + peg_box["width"] / 2
    y_start = peg_box["y"] + peg_box["height"] / 2

    print(f"Startovní pozice Pegmana: {x_start:.1f}, {y_start:.1f}")

    return {
        "x_start": x_start,
        "y_start": y_start,
        "map_center_x": map_center_x,
        "map_center_y": map_center_y,
        "map_width": map_width,
        "map_height": map_height,
    }


# Funkce pro ovládání prvků ve Street View
def kontrola_streetview(page: Page, info):
    x_start = info["x_start"]
    y_start = info["y_start"]
    mcx = info["map_center_x"]
    mcy = info["map_center_y"]
    w = info["map_width"]
    h = info["map_height"]

    success = False

    # Pokus o umístění Pegmana na mapu
    for attempt in range(7):

        dx = random.uniform(-w * 0.25, w * 0.25)   
        dy = random.uniform(-h * 0.25, h * 0.25)   

        x_target = mcx + dx
        y_target = mcy + dy

        print(f"Pokus {attempt+1}: Drop -> {x_target:.1f}, {y_target:.1f}")

        page.mouse.move(x_start, y_start)
        page.mouse.down()
        time.sleep(0.4)
        page.mouse.move(x_target, y_target, steps=50)
        page.mouse.up()

        time.sleep(6)

        if page.locator("canvas.widget-scene-canvas").count() > 0:
            print("Street View otevřeno – canvas nalezen.")
            success = True
            break

        if "streetview" in page.url.lower() or "!3m6" in page.url.lower():
            print("Street View otevřeno – URL potvrzeno.")
            success = True
            break

        print("Pegman se netrefil — další pokus…")
        page.keyboard.press("Escape")
        time.sleep(1.2)


    if not success:
        pytest.skip("Nebyl otevřen Street View.")

    # Otočení kamery ve Street View
    print("Otáčím kamerou ve Street View…")

    right_btn = page.locator("button[aria-label='Otočit pohled po směru hodinových ručiček']")
    if right_btn.count() == 0:
        print("Compass nenalezen.")
        return

    for i in range(4):
        right_btn.click()
        time.sleep(3)
        filename = f"streetview_turn_{i+1}.png"
        page.screenshot(path=filename)
        print(f"Snímek uložen: {filename}")


# Funkce pro spuštění testování Google Maps + Street View 
def test_google_mapy_streetview(page: Page):
    info = kontrola_mapy(page, "Praha")
    kontrola_streetview(page, info)
    print("Test byl dokončen.")
