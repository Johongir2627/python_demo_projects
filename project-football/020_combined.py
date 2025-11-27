from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from bs4 import BeautifulSoup
import re
import time
import random

def setup_driver(headless=True):
    mobile_emulation = {
        "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    # if headless:
    #     chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def fetch_page(url, max_retries=3):
    driver = setup_driver()
    match_html = None
    team1_html = None
    team2_html = None
    try:
        driver.get(url)
        # Wait for match details page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.cbmnyx"))
        )
        # Fetch match details HTML
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.Flex.eIA-DFy"))
        )
        match_html = driver.page_source

        # Navigate to Lineups tab
        try:
            lineups_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//h2[@data-tabid="lineups"]/a'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", lineups_tab)
            driver.execute_script("arguments[0].click();", lineups_tab)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Box.Flex.incwjW.gFqKXs"))
            )
        except TimeoutException as e:
            print("Failed to locate or click Lineups tab:", e)
            return match_html, None, None

        # Fetch Team 1 (Home Team) HTML
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Box.DooVT"))
        )
        team1_html = driver.page_source

        # Switch to Team 2 (Away Team)
        try:
            team2_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="right"]'))
            )
            for attempt in range(max_retries):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", team2_button)
                    driver.execute_script("arguments[0].click();", team2_button)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "Box.DooVT"))
                    )
                    break
                except ElementClickInterceptedException as e:
                    if attempt < max_retries - 1:
                        print(f"Click intercepted, retrying ({attempt + 1}/{max_retries})...")
                        time.sleep(random.uniform(1, 3))
                    else:
                        print(f"Failed to click Team 2 button after {max_retries} attempts: {e}")
                        return match_html, team1_html, None
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Box.DooVT"))
            )
            team2_html = driver.page_source
        except Exception as e:
            print("Error fetching Team 2:", e)
            return match_html, team1_html, None

        return match_html, team1_html, team2_html
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None, None, None
    finally:
        driver.quit()

def scrape_match_timeline(html_content):
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    events = []

    # Event containers
    event_containers = soup.find_all('div', class_='Box cbmnyx')
    additional_time_containers = soup.find_all('div', class_='Box Flex eIA-DFy kFvGEE')
    score_updates = soup.find_all('div', class_='Box Flex ggkAva jHZCTE')

    for container in event_containers:
        event = {}
        minute_tag = container.find('div', class_='Text falluO')
        if minute_tag:
            minute_text = minute_tag.get_text(strip=True)
            minute = re.sub(r'<sup>\+(\d+)</sup>', r'+\1', minute_text)
            event['minute'] = minute
        else:
            event['minute'] = 'N/A'

        svg_tag = container.find('svg', class_='SvgWrapper fyGiev')
        if svg_tag:
            title_tag = svg_tag.find('title')
            if title_tag:
                event['type'] = title_tag.get_text(strip=True)
            else:
                path_tags = svg_tag.find_all('path')
                is_substitution = any(
                    path.get('fill') in ['#C7361F', '#15B168']
                    for path in path_tags
                )
                event['type'] = 'Substitution' if is_substitution else 'Unknown'
        else:
            event['type'] = 'Unknown'

        text_container = container.find('div', class_=re.compile(r'Box Flex iRXnso|Box Flex krNUit|Box Flex kYBcuJ'))
        if text_container:
            primary_text = (text_container.find('span', class_=re.compile(r'Text dGsLCg|Text isFvDP')) or
                           text_container.find('span', class_=re.compile(r'Text')))
            secondary_text = (text_container.find('span', class_=re.compile(r'Text iBaaGe|Text dgNapt')) or
                             text_container.find('span', class_=re.compile(r'Text'), recursive=False))
            
            event['primary'] = primary_text.get_text(strip=True) if primary_text else 'N/A'
            event['secondary'] = secondary_text.get_text(strip=True) if secondary_text and secondary_text != primary_text else None
        else:
            event['primary'] = 'N/A'
            event['secondary'] = None

        score_tag = container.find('div', class_='Text eCiXKb')
        if score_tag:
            event['score'] = score_tag.get_text(strip=True)

        events.append(event)

    for container in additional_time_containers:
        time_tag = container.find('bdi', class_='Text hmQjqn')
        if time_tag:
            events.append({
                'minute': 'N/A',
                'type': 'Additional Time',
                'primary': time_tag.get_text(strip=True),
                'secondary': None,
                'score': None
            })

    for container in score_updates:
        score_tag = container.find('div', class_='Text falluO')
        if score_tag:
            score_text = score_tag.get_text(strip=True)
            if 'HT' in score_text or 'FT' in score_text:
                events.append({
                    'minute': score_text.split(' ')[0],
                    'type': 'Score Update',
                    'primary': score_text,
                    'secondary': None,
                    'score': score_text.split(' ')[1]
                })

    def sort_key(event):
        minute = event['minute']
        if minute == 'N/A':
            return float('inf')
        match = re.match(r'(\d+)(?:\+(\d+))?', minute)
        if match:
            base = int(match.group(1))
            extra = int(match.group(2)) if match.group(2) else 0
            return base + extra
        return 0

    events.sort(key=sort_key, reverse=True)
    return events

def scrape_lineups(html_team1, html_team2):
    soup_team1 = BeautifulSoup(html_team1, 'html.parser') if html_team1 else None
    soup_team2 = BeautifulSoup(html_team2, 'html.parser') if html_team2 else None
    teams_data = {'team1': [], 'team2': []}
    injury_data = {'team1': [], 'team2': []}
    team1_subbed_out = set()
    team2_subbed_out = set()

    def extract_player_data(player, is_starting=False, is_injury=False, is_sub_in=False):
        jersey_number = player.find('bdi', {'data-testid': 'lineups_number'}) or player.find('span', class_='Text wezlr')
        jersey_text = jersey_number.get_text(strip=True) if jersey_number else 'N/A'

        name_span = player.find('span', {'data-testid': 'lineups_name'}) or player.find('span', class_='Text iDqCDP') or player.find('span', class_='Text XWbBL')
        full_text = name_span.get_text(strip=True) if name_span else 'N/A'
        name = full_text.replace(jersey_text, '').replace('(c)', '').strip()

        rating_span = player.find('span', {'aria-valuemin': True})
        rating = rating_span.get_text(strip=True) if rating_span else 'N/A'

        played_status = 0
        if is_starting:
            played_status = 1
        elif is_sub_in:
            played_status = 3
        elif is_injury:
            played_status = 0

        return {
            'jersey_number': jersey_text,
            'name': name,
            'rating': rating,
            'played': played_status
        }

    def extract_injury_data(soup, team_key):
        injury_data = []
        status_to_number = {'Out': 4, 'Doubtful': 5, 'Suspended': 6, 'Injured': 4}
        player_links = soup.find_all('a', href=True)
        for link in player_links:
            name_tag = link.find('span', class_='Text XWbBL')
            status_tag = link.find('div', class_='Text jOIBlo') or link.find('div', class_='Text fcjZlr')
            if name_tag and status_tag:
                status_text = status_tag.text.strip()
                number = status_to_number.get(status_text, 0)
                if number in [4, 5, 6]:
                    injury_data.append({
                        'name': name_tag.text.strip(),
                        'status': status_text,
                        'number': number
                    })
        return injury_data

    if soup_team1:
        team1_container = soup_team1.find('div', class_='Box Flex incwjW gFqKXs sc-f78c658b-0 dKxDBr')
        if team1_container:
            team1_players = team1_container.find_all('div', class_='Box Flex hKRSeb cpiWOn')
            for player in team1_players:
                player_data = extract_player_data(player, is_starting=True)
                teams_data['team1'].append(player_data)

        team1_sub_container = soup_team1.find('div', class_='Box DooVT')
        if team1_sub_container:
            sub_players = team1_sub_container.find_all('a', {'data-testid': 'lineups_player'})
            for player in sub_players:
                sub_info = player.find('div', {'data-testid': 'lineups_sub_info'})
                player_data = extract_player_data(player, is_sub_in=bool(sub_info))
                if sub_info:
                    out_text = sub_info.find('span', class_='Text zySNQ', string=lambda x: 'Out:' in x if x else False)
                    if out_text:
                        out_player = out_text.get_text(strip=True).replace('Out:', '').strip()
                        team1_subbed_out.add(out_player)
                teams_data['team1'].append(player_data)

        team1_injury_container = soup_team1.find('div', class_='bg_surface.s1 md:bg_surface.s2 br_lg md:br_lg elevation_2 md:elevation_none pos_relative')
        if team1_injury_container:
            injury_players = team1_injury_container.find_all('a', recursive=False)
            for player in injury_players:
                player_data = extract_player_data(player, is_injury=True)
                teams_data['team1'].append(player_data)
        injury_data['team1'] = extract_injury_data(soup_team1, 'team1')

    if soup_team2:
        team2_container = soup_team2.find('div', class_='Box Flex eLcoCZ bQZybT sc-f78c658b-0 iFjpve')
        if team2_container:
            team2_players = team2_container.find_all('div', class_='Box Flex hKRSeb cpiWOn')
            for player in team2_players:
                player_data = extract_player_data(player, is_starting=True)
                teams_data['team2'].append(player_data)

        team2_sub_container = soup_team2.find('div', class_='Box DooVT')
        if team2_sub_container:
            sub_players = team2_sub_container.find_all('a', {'data-testid': 'lineups_player'})
            for player in sub_players:
                sub_info = player.find('div', {'data-testid': 'lineups_sub_info'})
                player_data = extract_player_data(player, is_sub_in=bool(sub_info))
                if sub_info:
                    out_text = sub_info.find('span', class_='Text zySNQ', string=lambda x: 'Out:' in x if x else False)
                    if out_text:
                        out_player = out_text.get_text(strip=True).replace('Out:', '').strip()
                        team2_subbed_out.add(out_player)
                teams_data['team2'].append(player_data)

        team2_injury_container = soup_team2.find('div', class_='bg_surface.s1 md:bg_surface.s2 br_lg md:br_lg elevation_2 md:elevation_none pos_relative')
        if team2_injury_container:
            injury_players = team2_injury_container.find_all('a', recursive=False)
            for player in injury_players:
                player_data = extract_player_data(player, is_injury=True)
                teams_data['team2'].append(player_data)
        injury_data['team2'] = extract_injury_data(soup_team2, 'team2')

    for player in teams_data['team1']:
        if player['played'] == 1 and player['name'] in team1_subbed_out:
            player['played'] = 2
    for player in teams_data['team2']:
        if player['played'] == 1 and player['name'] in team2_subbed_out:
            player['played'] = 2

    return teams_data, injury_data

def main():
    url = "https://www.sofascore.com/football/match/real-madrid-barcelona/rgbsEgb#id:12437545"
    match_html, team1_html, team2_html = fetch_page(url)
    
    if match_html or team1_html or team2_html:
        # Scrape match timeline
        if match_html:
            print("Match Timeline Events:")
            events = scrape_match_timeline(match_html)
            for event in events:
                print(f"Minute: {event['minute']}")
                print(f"Type: {event['type']}")
                print(f"Primary: {event.get('primary', 'N/A')}")
                print(f"Secondary: {event.get('secondary', None)}")
                print(f"Score: {event.get('score', None)}")
                print("-" * 40)
        else:
            print("No match timeline data retrieved.")

        # Scrape lineups and injuries
        if team1_html or team2_html:
            teams_data, injury_data = scrape_lineups(team1_html, team2_html)

            print("\nTeam 1 (Home Team) Players Info:")
            if teams_data['team1']:
                for player in teams_data['team1']:
                    print(f"{player['jersey_number']} {player['name']}")
                    print(f"  Rating   : {player['rating']}")
                    print(f"  Played   : {player['played']} ({'Full Time' if player['played'] == 1 else 'Subbed Out' if player['played'] == 2 else 'Subbed In' if player['played'] == 3 else 'Did Not Play'})")
                    print("-" * 40)
            else:
                print("No players found for Team 1.")

            print("\nTeam 2 (Away Team) Players Info:")
            if teams_data['team2']:
                for player in teams_data['team2']:
                    print(f"{player['jersey_number']} {player['name']}")
                    print(f"  Rating   : {player['rating']}")
                    print(f"  Played   : {player['played']} ({'Full Time' if player['played'] == 1 else 'Subbed Out' if player['played'] == 2 else 'Subbed In' if player['played'] == 3 else 'Did Not Play'})")
                    print("-" * 40)
            else:
                print("No players found for Team 2.")

            print("\n--- Team 1 Injured Players ---")
            if injury_data['team1']:
                for p in injury_data['team1']:
                    print(f"{p['name']} {p['number']}")
            else:
                print("No injured players found for Team 1.")

            print("\n--- Team 2 Injured Players ---")
            if injury_data['team2']:
                for p in injury_data['team2']:
                    print(f"{p['name']} {p['number']}")
            else:
                print("No injured players found for Team 2.")
        else:
            print("No lineup data retrieved.")
    else:
        print("Failed to retrieve page content.")

if __name__ == "__main__":
    main()