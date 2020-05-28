import requests
import json
import re
import subprocess
import os
from jsonpath import jsonpath
import threading

ffmpeg_path = r'D:\Application\ffmpeg\ffmpeg-20200429-280383a-win64-static\bin\ffmpeg'


def get_response(url):
    headers = {
        'User-Agent': requests.get('http://127.0.0.1:8888/headers').text,
        'referer': 'https://www.bilibili.com/'
        # 大会员可看高清 1080P+，需要buvid3，SESSDATA
        # buvid3:必填项,expires:2023-05-01T07:15:31.647Z
        # SESSDATA:登录cookies信息,expires:2021-05-01T07:15:31.647Z
        # 'cookie': "buvid3=9C1BF3BB-1E96-4EED-8C90-F21BE43A52D1155821infoc; SESSDATA=1945609a%2C1603869180%2C8ea0b*51;",
    }
    response = requests.get(url=url, headers=headers)
    return response.text


def get_urls(html):
    # 获取资源下载链接
    result = re.findall('<script>window\.__playinfo__=({.+?})</script>', html)
    datas = json.loads(result[0]) if result else ''
    # 获取视频和音频下载链接,分为多种清晰度
    video_list = jsonpath(datas, '$..video..baseUrl')
    audio_list = jsonpath(datas, '$..audio..baseUrl')
    # info = {
    #     '112': '高清 1080P+',
    #     '80': '高清 1080P',
    #     '64': '高清 1080P',
    #     '32': '高清 1080P',
    #     '16': '高清 1080P',
    # }
    # 第一个是最高清晰度
    video = video_list[0] if video_list else ''
    audio = audio_list[0] if audio_list else ''
    return video, audio


def get_author_title(html):
    # 获取作者昵称和视频标题
    author = re.findall('<h1 title="(.+?)"', html)
    title = re.findall('<a href=".+?" target="_blank" report-id="name" class="username">(.+?)</a>', html)
    author = author[0] if author else ''
    title = author[0] if title else ''
    return author, title


def download_flv(referer_url, flv_url, file_path, output_path):
    # 判断资源文件是否下载过
    if not os.path.exists(flv_url) and not os.path.exists(output_path):
        headers = {
            'User-Agent': requests.get('http://127.0.0.1:8888/headers').text,
            'referer': referer_url,
            'Origin': 'https://www.bilibili.com/',
        }
        # 下载资源文件
        with open(file_path, 'wb') as f:
            f.write(requests.get(url=flv_url, headers=headers, stream=True, verify=False).content)


def merge_video_audio(flv1_path, flv2_path, output_path, thread1, thread2):
    while True:
        # 若存在资源文件，则无需合并视频和音频
        if os.path.exists(output_path):
            break
        # 若视频和音频未下载完毕，则继续等待
        elif thread1.isAlive() or thread2.isAlive():
            continue
        else:
            # 当视频和音频均下载完毕，则开始合并视频和音频
            cmd = r'{} -i {} -i {} -vcodec copy -acodec copy {}'.format(ffmpeg_path, flv1_path, flv2_path, output_path)
            # 合并资源文件
            subprocess.call(cmd, shell=True)
            break
    # 删除单音频和视频文件
    os.remove(flv1_path) if os.path.exists(flv1_path) else ''
    os.remove(flv2_path) if os.path.exists(flv2_path) else ''
    print('下载完成:{}'.format(output_path))


def run(url, file_path='.', output_path=None):
    response = get_response(url)

    video_url, audio_url = get_urls(response)
    author, title = get_author_title(response)

    video_path = '{}/video-{}-{}.flv'.format(file_path, author, title)
    audio_path = '{}/audio-{}-{}.flv'.format(file_path, author, title)
    output_path = '{}/{}-{}.flv'.format(file_path, author, title) if not output_path else output_path

    t1 = threading.Thread(target=download_flv, args=(url, video_url, video_path, output_path))
    t2 = threading.Thread(target=download_flv, args=(url, audio_url, audio_path, output_path))
    t1.start()
    t2.start()
    threading.Thread(target=merge_video_audio, args=(video_path, audio_path, output_path, t1, t2)).start()


if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV1wT4y137h3?p=6'
    run(url)
