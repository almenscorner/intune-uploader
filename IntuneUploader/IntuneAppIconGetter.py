import glob
import os
import plistlib
import subprocess

from autopkglib import DmgMounter


class IntuneAppIconGetter(DmgMounter):
    """Extracts the app icon from a .app or .dmg file and saves it as a .png file.
    This is a very basic processor that uses the sips command to convert the icon to png format.
    For more advanced icon extraction, use the AppIconExtractor processor."""

    input_variables = {
        "app_file": {
            "required": True,
            "description": "Path to the .app or .dmg file to extract the icon from.",
        },
        "name": {
            "required": True,
            "description": "Name of the app to use in the output file name.",
        },
    }
    output_variables = {
        "icon_file_path": {
            "description": "Path to the extracted icon file, if successful.",
        }
    }

    def main(self):
        # Get input variables
        app_file = self.env.get("app_file")
        name = self.env.get("name")
        recipe_cache_dir = self.env.get("RECIPE_CACHE_DIR")
        self.env["icon_file_path"] = None
        mount_point = None

        # If app bundle not found, skip icon extraction
        if not os.path.exists(app_file):
            self.output(f"Could not find {app_file}.app, skipping icon extraction")
            return None

        # If app bundle is a .dmg file, mount it and get path to .app file
        if os.path.splitext(app_file)[1] == ".dmg":
            mount_point = self.mount(app_file)
            app_path = glob.glob(os.path.join(mount_point, "*.app"))
            if not app_file:
                self.output(f"Could not find .app file, skipping icon extraction")
                return None
            else:
                # It is assumed that we will get the first .app file in the mounted .dmg
                app_path = app_path[0]
                info_plist = os.path.join(app_path, "Contents", "Info.plist")
        elif os.path.splitext(app_file)[1] == ".app":
            app_path = app_file
            info_plist = os.path.join(app_path, "Contents", "Info.plist")
        else:
            self.output(f"File is not a .app or .dmg file, skipping icon extraction")
            return None

        # Load Info.plist file and get icon file path
        try:
            with open(info_plist, "rb") as f:
                info_dict = plistlib.load(f)
        except plistlib.InvalidFileException:
            return None

        icon_name = info_dict.get("CFBundleIconFile", name)  # use name as default if CFBundleIconFile is missing
        icon_path = os.path.join(app_path, "Contents", "Resources", f"{icon_name}")
        icon_output_path = os.path.join(recipe_cache_dir, f"{name}.png")
        sips_path = "/usr/bin/sips"

        # If icon file path does not end with .icns, append .icns extension
        if not os.path.splitext(icon_path)[1] == ".icns":
            icon_path += ".icns"

        # If icon file not found, skip icon extraction
        if not os.path.exists(icon_path):
            self.output(f"Could not find icon for {name}, skipping icon extraction")
            return None

        # If sips command not found, skip icon extraction
        if not os.path.exists(sips_path):
            self.output(f"Could not find sips, skipping icon extraction")
            return None

        # Use sips command to convert icon to png format and save to output path
        try:
            cmd = [sips_path, "-s", "format", "png", icon_path, "--out", icon_output_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            
            # change icon size to 256x256
            cmd = [sips_path, icon_output_path, "-z", "256", "256", "--out", icon_output_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
        except subprocess.CalledProcessError as err:
            self.output(f"Error converting icon: {err}")
            return None

        # Set output variable to path of extracted icon file
        if os.path.exists(icon_output_path):
            self.env["icon_file_path"] = icon_output_path

        # If app bundle was a .dmg file, unmount it
        if mount_point:
            self.unmount(app_file)
        
if __name__ == "__main__":
    PROCESSOR = IntuneAppIconGetter()
    PROCESSOR.execute_shell()