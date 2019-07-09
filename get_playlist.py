from bs4 import BeautifulSoup
import requests
import time
import csv

YOUTUBE_ROOT = 'https://www.youtube.com/'
URL_PLAYLIST = 'playlist?list=UURLxpoBLZs5QDCUcmQlijHA'
# URL_PLAYLIST = 'playlist?list=PLpbfYiSM0rqV13Q-V9LUktXs7PG5UAPTq'

count = 1


def get_html(url):
    r = requests.get(url)
    return r


def write_csv(data):
    with open('playlist_videos.csv', 'a') as f:
        order = ['url', 'time', 'name']
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writerow(data)


def get_playlist_links(response):
    global count

    if 'html' in response.headers['Content-Type']:
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        items = soup.find('table', class_='pl-video-table').find_all('tr', class_='pl-video yt-uix-tile ')

        for item in items:
            name = item.find('td', class_='pl-video-title').find('a', {'dir': 'ltr'}).text.strip()
            url = 'https://www.youtube.com' + item.find('a').get('href')
            video_time = item.find('td', class_='pl-video-time').find('div', {'class': 'timestamp'}).text.strip()
            data = {'url': url, 'name': name, 'time': video_time}
            write_csv(data)
            print(count, data)
            count += 1
    else:
        html = response.json()['content_html']
        soup = BeautifulSoup(html, 'lxml')

        timestamp = soup.find_all('div', {'class': 'timestamp'})

        for i, link in enumerate(soup.find_all('a', {'dir': 'ltr'})):
            href = link.get('href')
            if href.startswith('/watch?'):
                # print(link.string.strip())
                name = link.string.strip()
                url = 'https://www.youtube.com' + href
                video_time = timestamp[i].text
                data = {'url': url, 'name': name, 'time': video_time}
                write_csv(data)
                print(count, data)
                count += 1


def get_next(response):
    if 'html' in response.headers['Content-Type']:
        html = response.text
    else:
        html = response.json()['load_more_widget_html']

    soup = BeautifulSoup(html, 'lxml')

    try:
        url = 'https://youtube.com' + soup.find('button', {'class': 'load-more-button'}).get('data-uix-load-more-href')
    except:
        url = ''

    return url


def main():
    url = YOUTUBE_ROOT + URL_PLAYLIST
    while True:
        response = get_html(url)
        get_playlist_links(response)

        url = get_next(response)
        time.sleep(0.04)

        if url:
            continue
        else:
            break


if __name__ == '__main__':
    main()
