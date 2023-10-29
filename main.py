import os
#import youtube_dl
import yt_dlp
import PySimpleGUI as sg
from utils.StatusLogger import StatusLogger
from pathlib import Path
from moviepy.editor import *


class SimpleYTGui:

    def __init__(self):
        self.downloaded_filename = None
        self.layout = []
        self.window = None
        self.options = {}
        self.defaultSaveLocation = Path.home()
        if os.uname().sysname == "Darwin":
            listdir = os.listdir(self.defaultSaveLocation)
            if "Desktop" in listdir:
                print("Desktop!")
                self.defaultSaveLocation = str(self.defaultSaveLocation) + '/' + 'Desktop'
            elif "Pulpit" in listdir:
                self.defaultSaveLocation = str(self.defaultSaveLocation) + '/' + 'Pulpit'
            elif "Biurko" in listdir:
                self.defaultSaveLocation = str(self.defaultSaveLocation) + '/' + 'Biurko'

    def initializeWindow(self):
        self.layout = [
            [
                sg.Frame('', [
                    [
                        sg.Column([
                            [sg.Text('Podaj link do utworu na YouTube')],
                            [sg.InputText('', key='link')]
                        ])
                    ],
                    [
                        sg.Column([
                            [sg.Radio("Wideo", 'type', key='video', default=True)],
                            [sg.Radio('Dźwięk', 'type', key='music')]
                        ]),
                        sg.Column([
                            [
                                sg.Text('Lokalizacja zapisu:'),
                            ],
                            [
                                sg.Text(self.defaultSaveLocation, key='save_location'),
                            ],
                            [
                                sg.FolderBrowse('Wybierz inną',
                                                initial_folder=str(self.defaultSaveLocation),
                                                tooltip="Wybierz inną ścieżkę w której docelowo ma zostać zapisany plik",
                                                key="browse",
                                                enable_events=True,
                                                )],
                            [sg.HSeparator()],
                            [sg.Text("Status pobierania:")],
                            [sg.Text("Program oczekuje na wprowadzenie linku", key='status_text')],
                            [sg.ProgressBar(100,
                                            orientation='h',
                                            expand_x=True,
                                            size=(200, 10),
                                            key='status'
                                            )
                             ],
                            [sg.Button('Pobierz', key='download')]
                        ])
                    ]

                ])
            ]
        ]
        sg.theme('Gray Gray Gray')
        self.window = sg.Window('Simple YT Downloader',
                                self.layout,
                                size=(400, 300))

    def progress_hook(self, d):
        print(d)
        status = d['status']
        if status == 'finished':
            # sprawdzenie czy plik istnieje jezeli istnieje przeniesiono
            self.set_status_text_value('Pomyślnie pobrano, trwa konwersja')
            self.set_status_value(100)
            self.downloaded_filename = d['filename']
            if self.window['music'].get():
                if ".mp4" in self.downloaded_filename:
                    video = VideoFileClip(self.downloaded_filename)
                    old_file = self.downloaded_filename
                    convert_mp3 = self.downloaded_filename.replace('.mp4', '.mp3')
                    video.audio.write_audiofile(convert_mp3)
                    self.downloaded_filename = convert_mp3
                    # usuniecie oryginalnego pliku
                    os.remove(old_file)
            curr_dir = os.getcwd()
            curr_directory_data = os.listdir(curr_dir)
            now_location = os.getcwd() + '/' + self.downloaded_filename
            if self.downloaded_filename in curr_directory_data:
                destination = str(self.defaultSaveLocation) + '/' + self.downloaded_filename
                os.replace(now_location, destination)
                self.set_status_text_value("Ukończono, plik przeniesiono \ndo docelowego miejsca")
            else:
                self.set_status_text_value("Problem z przeniesieniem pliku")
            self.enable_download_button()
            return
        procent = d['_percent_str'].replace('%', '').replace('\x1b[0;', '').replace('94m', '').replace('\x1b[0m', '').replace('\x1b[0', '')
        print("heheheprocent")
        print(procent)
        procent_int = int(float(procent.replace(' ', '')))

        print('procent')
        print(procent_int)
        self.set_status_value(procent)
        self.set_status_text_value('Trwa pobieranie procent pobierania:' + procent + " %")

        if d['status'] == 'finished':
            print('Done downloading, now converting....')

    def start_download(self):
        ydl_opts = {}
        if self.window['video'].get():
            ydl_opts['format'] = 'bestvideo[ext=mp4]/best[ext=mp4]/best'

        elif self.window['music'].get():
            ydl_opts['format'] = 'bestaudio[ext=mp3]/best[ext=mp3]/best'
            '''ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]'''
        ydl_opts['logger'] = StatusLogger()
        ydl_opts['nocheckcertificate'] = True
        ydl_opts['progress_hooks'] = [self.progress_hook]

        # print("pobieram")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.window['link'].get()])

    def check_link_exist(self):
        link = self.window['link'].get()
        print("link:")
        print(link)
        if link != None and link == '':
            return False
        return True

    def disable_download_button(self):
        print("disable download")
        self.window['download'].update(disabled=True)
        self.window['link'].update(disabled=True)

    def enable_download_button(self):
        self.window['download'].update(disabled=False)
        self.window['link'].update(disabled=False)

    def set_status_text_value(self, text):
        self.window['status_text'].update(value=text)

    def set_status_value(self, value):
        self.window['status'].update(value)

    def events(self):
        while True:
            event, values = self.window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'exit':
                break
            elif event == 'download':
                if not self.check_link_exist():
                    pass
                else:
                    self.disable_download_button()
                    self.start_download()
            elif event == 'browse':
                print("Browse, wybor innej ścieżki!")
                direction = values['browse']
                self.defaultSaveLocation = direction
                self.window['save_location'].update(value=self.defaultSaveLocation)
                print('ustalono nową scieżkę docelową!')
        self.window.close()


window = SimpleYTGui()
window.initializeWindow()
window.events()
