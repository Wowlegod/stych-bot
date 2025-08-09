import time
import os
from discord_webhook import DiscordWebhook
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

STYCH_EMAIL = os.getenv("STYCH_EMAIL")
STYCH_PASSWORD = os.getenv("STYCH_PASSWORD")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

last_slots = []

def send_discord_message(message):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    webhook.execute()

def check_slots():
    global last_slots
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Connexion
        page.goto("https://www.stych.fr/elearning/connexion")
        page.fill("input[name='email']", STYCH_EMAIL)
        page.fill("input[name='password']", STYCH_PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_timeout(4000)

        # Accès au planning
        page.goto("https://www.stych.fr/elearning/formation/conduite/reservation/planning")
        page.wait_for_timeout(5000)

        # Sélecteur à ajuster selon le HTML réel
        slots_elements = page.query_selector_all(".calendar-slot")
        slots = [slot.inner_text() for slot in slots_elements]

        browser.close()

    # Comparaison avec l'ancienne liste
    new_slots = [s for s in slots if s not in last_slots]
    if new_slots:
        send_discord_message(f"🚗 **Nouvelles places dispo à Marseille !**\n" + "\n".join(new_slots))
        last_slots = slots

if __name__ == "__main__":
    send_discord_message("✅ Bot Stych démarré")
    while True:
        try:
            check_slots()
        except Exception as e:
            send_discord_message(f"⚠️ Erreur dans le bot : {e}")
        time.sleep(300)  # 5 minutes
