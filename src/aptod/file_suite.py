
"""
This class releated with file opertions.
It will create or delete config, dir... and that kind a things.
"""

import shutil
import os
import json
import  re

from .utils import IconHandler


class FileSuite:
    """Creates, updates, deletes neccesary files for Aptod."""
    
    def __init__(self):
        self.cfg_dir = os.path.join(os.path.expanduser('~'), ".config/aptod" )
        self.cfg_pth = os.path.join(self.cfg_dir, 'aptod.conf')
        self.repo_pth = os.path.join(self.cfg_dir, 'aptod_repo.json')
        self.unofficial_repo_pth = os.path.join(self.cfg_dir, 'unofficial_repo.json')

    def create_config(self) -> None:
        """Creates config file for user."""

        if os.path.exists(self.cfg_pth):
            print(f'Config file aldready exist at "{self.cfg_pth}"')
            return

        # If also folder not exist create them.
        if not os.path.exists(self.cfg_dir):
            os.makedirs(self.cfg_dir)

        # Finally create .conf
        cfg_data = {"MainFolder": f"{os.path.expanduser('~')}/appImage"}

        # Write first config
        with open(self.cfg_pth, 'w', encoding="utf-8") as file:
            json.dump(cfg_data, file, indent = 2)

        if not os.path.exists(cfg_data['MainFolder']):
            os.makedirs(cfg_data['MainFolder'])

    def create_repo(self, default=True) -> None:
        """Creates repo file for Aptod."""
        
        if default:
            repo_path = self.repo_pth
        else:
            repo_path = self.unofficial_repo_pth

        if os.path.exists(repo_path):
            return

        with open(repo_path, 'w', encoding="utf-8") as file:
            json.dump({}, file, indent=2)

    def add_unofficial_repo(self, repo_list: list):
        """Initilization purposes"""
        with open(self.unofficial_repo_pth, 'w', encoding="utf-8") as file:
            json.dump(repo_list, file, indent=2)

    def update_repo(self, app_data: dict) -> dict:
        """Adds new url to local repo file."""        
        
        def app_name_generator(url: str) -> str:
            list_of_url = url.split('.com/', 1)[1]
            repo_name = list_of_url.split('/')[1]

            # Capitalize each capital letter, than remove spaces in name
            app_name = ' '.join(re.findall(r'\w+', repo_name)).title().replace(" ", '')

            # If app name not in in file name, change app name
            # Example: BraveAppImage is not in brave-stable.AppImage
            # In bellow we will assing app_name to brave-stable

            # Remove .appimage extension in name            
            clear_name = re.sub('.appimage', '', app_data['name'], flags=re.IGNORECASE)
            if not re.search(app_name, clear_name, re.IGNORECASE):
                app_name = re.findall(r'[A-Za-z]+', clear_name)[0]
            return app_name

        url = app_data['down_url']
        app_name = app_name_generator(url)
        
        if not os.path.exists(self.repo_pth):
            self.create_repo()

        with open(self.repo_pth, "r", encoding="utf-8") as data_file:
            # Reading old data
            data = json.load(data_file)

        data[app_name] = url
        with open(self.repo_pth, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent = 2)

        return data

    def get_repo(self, unofficial=False) -> dict:
        """Returns user added repo"""

        repo_path = self.repo_pth
        if unofficial:
            repo_path = self.unofficial_repo_pth

        if not os.path.exists(repo_path):
            return {}

        with open(repo_path, "r", encoding="utf-8") as data_file:
            data = json.load(data_file)

        return data

    def get_main_app_dir(self) -> str:
        """Returns main appimage installation folder path"""
        with open(self.cfg_pth, 'r', encoding="utf-8") as file:
            data = json.load(file)

        return data['MainFolder']

    def get_config(self) -> dict:
        """If config file is exsists than returns file as dictionary."""
        if not os.path.exists(self.cfg_pth):
            return {}

        with open(self.cfg_pth, "r", encoding="utf-8") as data_file:
            try:
                data = json.load(data_file)
            except json.decoder.JSONDecodeError:
                # If json is corrupted delete and create new one
                os.remove(self.cfg_pth)
                self.create_config()
                with open(self.cfg_pth, "r", encoding="utf-8") as data_file:
                    data = json.load(data_file)

        return data

    def find_app(self, directory: str, name: str) -> str:
        """ Returns first file path that ends with .appimage extension
        from given path's folder that includes name."""

        # Loop all folder names
        for dir_ in os.listdir(directory):
            # name(librewolf, tutanota...).
            if name.lower() in dir_.lower():
                # Than only focus returning .AppImage
                # For make this always work, after-
                #updating, old .AppImage should be deleted.
                for file_ in os.listdir(os.path.join(directory, dir_)):
                    if re.search(r'.AppImage$', file_, re.IGNORECASE):
                        return os.path.join(directory, dir_, file_)
        # raise FileNotFoundError(f'App is not exist in "{directory}"')
        return ''

    def create_desktop(self, app_data) -> None:
        """Creates .desktop files but if they exist
        than only updates with new data."""

        example_dot = """[Desktop Entry]
            Encoding=UTF-8
            Type=Application
            Terminal=false
            Exec={app_path}
            Name={app_name}
            Icon={app_icon_path}"""   

        app_full_path = os.path.join(app_data['app_down_path'], app_data['name'])
        # Make .AppImage file exacutable
        os.system(f'chmod +x {app_full_path}')

        path = f'{os.path.expanduser("~")}/.local/share/applications/'
        if not os.path.exists(path):
            os.makedirs(path)

        app_name = re.findall(r'\w+', app_data['name'])[0].lower()
        desktop_path = f'{path}{app_name}.desktop'
        app_icon_path = os.path.join(app_data['app_down_path'], "icon.png")

        if not os.path.exists(app_icon_path):
            with open(app_icon_path, 'wb') as file:      
                file.write(IconHandler().get_icon(app_name))

        # If .desktop is exist only change version
        if not os.path.exists(desktop_path): 
            example_dot = example_dot.replace(
                '{app_path}', os.path.join(app_data['app_down_path'], app_data['name']))
            example_dot = example_dot.replace('{app_name}', re.findall(r'\w+', app_data['name'])[0])
            example_dot = example_dot.replace('{app_icon_path}', app_icon_path)

            with open(desktop_path, 'w', encoding="utf-8") as file:
                file.write(example_dot)
        else:
            # If .dekstop exist than only update app name in .desktop
            with open(desktop_path, 'r', encoding="utf-8") as file:
                desktop_f = file.read()
            # Get the will replaced item
            first_word = re.findall(r'\w+', app_data['name'])[0]
            to_replace = re.search(f'{first_word}(.*).AppImage', desktop_f).group()
            # When sub dir name is same with app name, remove sub dir name
            if '/' in to_replace:
                to_replace = to_replace.split('/')[-1]
            desktop_f = desktop_f.replace(to_replace, app_data['name'])
            with open(desktop_path, 'w', encoding="utf-8") as file:
                file.write(desktop_f)

    def remove_app_files(self, path) -> None:
        """Removes related files for given appimage."""

        desktop_sub_path = f'{os.path.expanduser("~")}/.local/share/applications/'

        app_desktop_file = desktop_sub_path
        app_desktop_file += re.findall(r'\w+', path.split('/')[-1])[0].lower() + '.desktop'
        path = path.replace('/' + path.split('/')[-1], '')

        # Bellow could be dangerous if any bugs occur!
        # So good to have extra protection with if statment bellow
        if 'appImage' in path:
            shutil.rmtree(path)
            os.remove(app_desktop_file)
