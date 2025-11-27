from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up mobile emulation (iPhone X dimensions)
mobile_emulation = {
    "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

# Set up the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Navigate to Real Madrid's team page
    driver.get("https://www.sofascore.com/team/football/real-madrid/2829")
    
    # Wait for the page to load
    time.sleep(5)
    
    # Find and click the "Matches" tab
    matches_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Matches')]"))
    )
    matches_tab.click()
    
    # Wait for the Matches section to load
    time.sleep(3)
    
    # Find and click the "Results" chip
    results_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-tabid='0' and contains(text(), 'Results')]"))
    )
    results_button.click()
    
    # Wait for the Results section to load
    time.sleep(5)
    
    # Find all match containers
    match_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'bg_surface.s1')]")
    
    # Extract details for each match
    matches = []
    for match in match_containers:
        try:
            # Extract tournament name
            tournament = match.find_element(By.XPATH, ".//a[contains(@href, '/tournament')]").text
            
            # Extract match date
            date = match.find_element(By.XPATH, ".//bdi[@data-testid='event_time']").text
            
            # Extract team names
            home_team = match.find_element(By.XPATH, ".//div[@data-testid='left_team']//bdi").text
            away_team = match.find_element(By.XPATH, ".//div[@data-testid='right_team']//bdi").text
            
            # Extract scores
            home_score = match.find_element(By.XPATH, ".//div[@data-testid='left_score']//span[@class='Text bOoisU currentScore']").text
            away_score = match.find_element(By.XPATH, ".//div[@data-testid='right_score']//span[@class='Text fxWZuu currentScore']").text
            
            # Extract result (W, L, or D)
            result = match.find_element(By.XPATH, ".//div[@class='Text ihwaOf']").text
            
            matches.append({
                "tournament": tournament,
                "date": date,
                "home_team": home_team,
                "away_team": away_team,
                "score": f"{home_score} - {away_score}",
                "result": result
            })
        except Exception as e:
            print(f"Error processing match: {e}")
            continue
    
    # Print extracted matches
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"  Tournament: {match['tournament']}")
        print(f"  Date: {match['date']}")
        print(f"  Teams: {match['home_team']} vs {match['away_team']}")
        print(f"  Score: {match['score']}")
        print(f"  Result: {match['result']}")
        print()

finally:
    # Close the browser
    driver.quit()