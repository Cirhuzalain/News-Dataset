import asyncio
import bs4 as bs
import concurrent.futures
import requests
import shutil
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
final_data = []
urls = []
with open("news_final.txt") as f:
    for line in f:
        urls.append(line)

def do_req(url):
    return requests.get(url, headers=headers)

def get_image(url, path):
    r = requests.get(url, headers=headers, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            
def save_file(content):
    with open('data_full_caption.json', 'w') as fout:
        json.dump(content, fout)

async def main():

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor, 
                do_req,
                url
            )
            for url in urls
        ]
        i = 0
        for response in await asyncio.gather(*futures):
            page_soup = bs.BeautifulSoup(response.text, 'html.parser')
            news_title = page_soup.select_one('article h1')
            news_title = news_title.text if news_title else ''
            news_body = page_soup.select_one('article div[itemprop="articleBody"]')
            
            img_caption = page_soup.select_one('article div.media img[itemprop="image"]')
            img_caption_desc = page_soup.select_one('article div.media small')
            news_body = news_body.text if news_body else ''
            
            if img_caption and img_caption_desc:
                file_name = "data/{}.jpg".format(str(i))
                get_image(img_caption['src'], file_name)
                img_caption_desc = img_caption_desc.text if img_caption_desc else ''
                final_data.append({'title' : news_title, 'content' : news_body, 'caption_img' : file_name, 'caption_desc' : img_caption_desc})
                print('Save {} file'.format(i))
            else:
                final_data.append({'title' : news_title, 'content' : news_body, 'caption_img' : '', 'caption_desc' : ''})
            i = i + 1
                
        save_file(final_data)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
