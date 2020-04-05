import os
import requests
import semver
import subprocess
from threading import Thread, Event
from plistutils.plistparser import InvalidPlistException, PlistParser
from kivy.core.window import Window


LATEST_RELEASE_URL = 'https://api.github.com/repos/bjoernStriebing/KeaIGC/releases/latest'


class KeaIgcUpdate(Thread):

    def __init__(self, app, **kwargs):
        self.app = app
        super(KeaIgcUpdate, self).__init__(target=self.check_update_available,
                                           args=(), **kwargs)
        self.daemon = True
        self.start()

    def check_update_available(self, *args):
        release_version = None
        download_size = None
        download_url = None
        try:
            # pull update infromation from host
            response = requests.get(LATEST_RELEASE_URL, timeout=10)
        except requests.exceptions.Timeout:
            return

        # just stop on bad response
        if not response:
            return

        r_json = response.json()
        try:
            # parse response
            release_version = r_json['tag_name'].strip('v')
            for asset in r_json['assets']:
                # find distributor disk imge
                if asset['name'].endswith('.dmg'):
                    # continue parsing download info
                    download_size = asset['size']
                    download_url = asset['browser_download_url']
                    download_name = asset['name']
                    break
            if None in (release_version, download_size, download_url):
                raise KeyError()
        except KeyError:
            return

        # get current version info
        plist = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'Info.plist'))
        try:
            with open(plist, 'rb') as plist_file:
                plist_data = PlistParser.parse(plist_file)
                current_version = plist_data['CFBundleShortVersionString']
        except (IOError, InvalidPlistException, KeyError):
            return

        # compare versions
        cur = current_version.split('-')
        rel = release_version.split('-')
        if len(cur) == 1:
            cur.append(0)
        if len(rel) == 1:
            rel.append(0)
        # compare semver
        compare = semver.compare(rel[0], cur[0])
        # compare commit counter
        if compare < 0 or (compare == 0 and int(rel[1]) <= int(cur[1])):
            # already up to date
            return

        continue_update = Event()
        self.app.gui.suggest_update(release_version, current_version, download_size,
                                    continue_update)
        continue_update.wait()
        continue_update.clear()

        # start download
        response = requests.get(download_url, timeout=30)

        # stop on bad response and let the user know
        if not response:
            self.app.gui.show_message("Downloading update failed.\n\n({}) {}".format(
                                      response.status_code, response.content['message']))
            return

        # save to temp
        tmp_dir = '/tmp/keaigc'
        dmg_file = os.path.join(tmp_dir, download_name)
        os.makedirs(tmp_dir, exist_ok=True)
        with open(dmg_file, 'wb') as dmg:
            dmg.write(response.content)

        # tell user what we've done
        self.app.gui.show_message("Download update complete.\n\n(saved to {})\n\n\nYou can install once you close the app.".format(dmg_file))

        # open dmg image when we leave the application
        Window.bind(on_close=lambda window, dmg=dmg_file: self.mount_dmg(dmg))

    def mount_dmg(self, dmg):
        mount_point = ' '.join(dmg.split('.')[:-1])
        mount = subprocess.run(['hdiutil', 'attach', '-mountpoint', mount_point, dmg])
        if mount:
            subprocess.run(['open', mount_point])
