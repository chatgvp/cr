from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import httpx

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response

async def scrape_link(link):
    link_url = f'https://www.coindesk.com{link["href"]}'
    link_response = await fetch(link_url)
    if link_response.status_code == 200:
        link_soup = BeautifulSoup(link_response.text, 'html.parser')
        image_selector = '.featured-imagestyles__FeaturedImageWrapper-sc-ojmof1-0.jGviVP.at-rail-aligner.at-rail-aligner-fi img'
        alternative_image_selector = '.featured-imagestyles__FeaturedImageWrapper-sc-ojmof1-0.jGviVP.featured-media.featured-media-fi img'

        image_element = link_soup.select_one(image_selector) or link_soup.select_one(alternative_image_selector)
        image_url = image_element['src'] if image_element else None

        author_selector = '.at-authors .typography__StyledTypography-sc-owin6q-0.dWBCgF a'
        alternative_author_selector = '.block-item .typography__StyledTypography-sc-owin6q-0.dWBCgF a'

        author_element = link_soup.select_one(author_selector) or link_soup.select_one(alternative_author_selector)
        author = author_element.text if author_element else None

        tags_selector = '.typography__StyledTypography-sc-owin6q-0.VOLnO'
        alternative_tags_selector = '.typography__StyledTypography-sc-owin6q-0.giduqy'

        tags_element = link_soup.select_one(tags_selector) or link_soup.select_one(alternative_tags_selector)
        tags = tags_element.text if tags_element else None

        data = {
            'url': link_url,
            'image_url': image_url,
            'tags': tags,
            'title': link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.bSOJsQ').text if link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.bSOJsQ') else None,
            'description': link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.irVmAp').text if link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.irVmAp') else None,
            'author': author,
            'date': link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.hcIsFR').text if link_soup.select_one('.typography__StyledTypography-sc-owin6q-0.hcIsFR') else None,
            'update': link_soup.select_one('.at-updated .typography__StyledTypography-sc-owin6q-0.hcIsFR').text if link_soup.select_one('.at-updated .typography__StyledTypography-sc-owin6q-0.hcIsFR') else None,
        }
        return data



@app.get("/get_coindesk_data")
async def get_coindesk_data():
    url = 'https://www.coindesk.com/'

    response = await fetch(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('.card-imagestyles__CardImageWrapper-sc-1kbd3qh-0.WDSwd')

        data_list = []

        for link in links:
            data = await scrape_link(link)
            if data and data.get('title') is not None:
                data_list.append(data)
                if len(data_list) == 10:
                    break
        return data_list
    else:
        return {"error": f"Failed to retrieve the page. Status code: {response.status_code}"}
