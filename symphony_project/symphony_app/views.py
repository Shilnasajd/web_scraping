from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from .models import EntitiesMaster
from datetime import datetime

def save_entity(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Only add this if you are running Chrome on Linux
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        page_content = driver.page_source
    finally:
        driver.quit()

    # Extract entities from the page content
    entities = extract_entities(page_content)
    
    # Save entities to the EntitiesMaster table
    for artist in entities['artists']:
        EntitiesMaster.objects.create(
            artist_name=artist['artist_name'],
            artist_role=artist['artist_role'],
            program_name='',  # Update as needed
            composer='',  # Update as needed
            location=entities['performances'][0]['location'],  # Assuming only one performance
            date_time=datetime.strptime(entities['performances'][0]['date_time'], '%a, %b %d, %Y at %I:%M%p'),  # Parse date and time
            tickets_info=entities['performances'][0]['tickets_info'],
            url=url
        )
    # Similarly, save program entities if needed

    return JsonResponse(entities)


def extract_entities(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract artist names
    artists = []
    artist_elements = soup.select('.event-detail-artist')
    for artist_element in artist_elements:
        name_element = artist_element.select_one('p.subhead4 a')
        role_element = artist_element.select_one('p.subhead6')
        if name_element and role_element:
            artist_name = name_element.get_text(strip=True)
            artist_role = role_element.get_text(strip=True)
            artists.append({'artist_name': artist_name, 'artist_role': artist_role})

    # Extract program details
    programs = []
    program_elements = soup.select('.text-left .subhead4, .text-left .margin-bottom-1')
    
    # Ensure we have pairs of elements
    program_elements = [elem.get_text(strip=True) for elem in program_elements if elem.get_text(strip=True)]
    if len(program_elements) % 2 != 0:
        program_elements.append('N/A')  # Append 'N/A' if the number of elements is odd

    for i in range(0, len(program_elements), 2):
        program_name = program_elements[i] if i < len(program_elements) else 'N/A'
        program_composer = program_elements[i + 1] if i + 1 < len(program_elements) else 'N/A'
        programs.append({'name': program_name, 'composer': program_composer})

    performances = []
    performance_element = soup.select_one('#buytix')  # Assuming there's only one performance section
    if performance_element:
        location = performance_element.select_one('.location strong')
        date_time = performance_element.select_one('.body-text3')
        tickets_info = performance_element.select_one('.not-available')
        if location and date_time:
            location_text = location.get_text(strip=True)
            date_time_text = date_time.get_text(strip=True)
            tickets_info_text = tickets_info.get_text(strip=True) if tickets_info else "Tickets information not available"
            performances.append({
                'location': location_text,
                'date_time': date_time_text,
                'tickets_info': tickets_info_text
            })

    return {'artists': artists, 'programs': programs, 'performances': performances}

def get_entity(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    # Filter entities based on the provided URL
    entities = EntitiesMaster.objects.filter(url=url).values()

    return JsonResponse(list(entities), safe=False)