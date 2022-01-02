import re
import webbrowser
from pathlib import Path
import subprocess
import os
from itertools import repeat


def layout():
    _layout = {"he-עב": '00001006', "en-us": '00000002'}
    _language = subprocess.getoutput("xset -q | grep -A 0 'LED' | cut -c59-67")
    for language, code in _layout.items():
        if code == _language:
            return language


class Commands:
    '''Perfom Commands return (title,msg)'''

    def find(filename, folder):
        file = re.compile(filename, re.IGNORECASE)
        for files in os.listdir(f'{folder}'):
            if re.search(file, files):
                msg = os.path.join(folder, files)
                return ("File found", msg)

    def calc():
        launch = "gtk-launch qalculate-gtk".split(' ')
        focus = "sleep 1; wmctrl -a Qalculate!"
        subprocess.run(launch)
        subprocess.run(focus, shell=True)

    def upgrade():
        cmd = 'apt upgrade -y'.split(' ')
        msg = subprocess.check_output(cmd).decode('utf-8').splitlines()[-1]
        msg = msg.replace(', ', '\n').replace(' and ', '\n')
        return ('Upgrade', msg)

    def update():
        cmd = '/usr/lib/update-notifier/apt-check --human-readable'.split(' ')
        msg = subprocess.check_output(cmd).decode('utf-8')
        return ('Update', msg)


class LookoUt:
    def __init__(self):
        self.folders = ['/home/vegi/Downloads', '/home/vegi/Desktop']
        self.commands = ['calc', 'upgrade', 'update']
        self.websearch = {'g': 'google', 's': 'stackoverflow', 'y': 'youtube'}
        self.web = Search()

    def search(self, str):
        if str[0] in self.websearch.keys() and str[1] == ' ':
            str = str.split(' ')
            name = self.websearch[str[0]]
            query = ''.join(str[1:])
            self.web.search(name, query)
        elif str in self.commands:
            return getattr(Commands, str)()
        elif str.startswith('find'):
            str = str.split(' ')
            find = getattr(Commands, str[0])
            result = list(filter(None, list(
                map(find, repeat(str[1]), self.folders))))
            try:
                return result[0]
            except:
                return None

        else:
            pass
        return None

    def open_file(self, path):
        subprocess.run(f'xdg-open {path}', shell=True)


class Search:
    def __init__(self,):
        self.browser = webbrowser.get('/usr/bin/google-chrome')

    def url_gen(self, name, query):
        query_fild = 'results?search_query=' if name == 'youtube' else 'search?q='
        url = ''.join(['http://www.', name, '.com/', query_fild, query])
        return url

    def search(self, name, query):
        url = self.url_gen(name, query)
        self.browser.open(url)


if __name__ == '__main__':
    search = LookoUt()
    print(search.search('find projects'))
