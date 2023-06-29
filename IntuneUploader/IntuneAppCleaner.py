#!/usr/local/autopkg/python

"""
This processor cleans up apps in Intune based on the input variables. 
It will keep the number of versions specified in the keep_version_count variable. It will delete the rest.

Created by Tobias Almén
"""

import sys 
import os

__all__ = ["IntuneAppCleaner"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase

class IntuneAppCleaner(IntuneUploaderBase):
    """This processor cleans up apps in Intune based on the input variables."""

    description = __doc__
    input_variables = {
        "display_name": {
            "required": True,
            "description": "The name of the app to clean up.",
        },
        "keep_version_count": {
            "required": False,
            "description": "The number of versions to keep. Defaults to 3.",
            "default": 3,
        },
        "test_mode": {
            "required": False,
            "description": "If True, will only print what would have been done.",
            "default": False,
        },
    }
    output_variables = {
        "intuneappcleaner_summary_result": {"description": "Description of interesting results."}
    }

    def main(self):
        # Set variables
        self.BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"
        self.CLIENT_ID = self.env.get("CLIENT_ID")
        self.CLIENT_SECRET = self.env.get("CLIENT_SECRET")
        self.TENANT_ID = self.env.get("TENANT_ID")
        app_name = self.env.get("display_name")
        keep_versions = self.env.get("keep_version_count")
        apps_to_delete = []
        test_mode = self.env.get("test_mode")
        
        # Get access token
        self.token = self.obtain_accesstoken(self.CLIENT_ID, self.CLIENT_SECRET, self.TENANT_ID)
        
        
        # When running from the command line, keep_versions is a string, convert to int
        if type(keep_versions) is not int:
            keep_versions = int(keep_versions)
        
        # Get macthing apps
        apps = self.get_matching_apps(app_name)
        self.output(f"Found {str(len(apps))} apps matching {app_name}")
        
        if len(apps) == 0:
            return None
        
        # Get a sorted list of apps by version
        apps = sorted(apps, key=lambda app: app["primaryBundleVersion"], reverse=True)
        
        # If the number of apps is greater than the keep version count, remove the apps that should be kept
        if len(apps) > keep_versions:
            self.output("App count is greater than keep version count, removing apps.")
            # Remove the apps that should be kept
            apps_to_delete = apps[keep_versions:]
            
            # Delete the apps that should not be kept
            for app in apps_to_delete:
                self.output("Deleted app: " + app["displayName"] + " " + app["primaryBundleVersion"])
                # Only delete if not in test mode
                if not test_mode:
                    self.makeapirequestDelete(self.BASE_ENDPOINT + "/" + app["id"], self.token)
                
        self.env["intuneappcleaner_summary_result"] = {
            "summary_text": "Summary of IntuneAppCleaner results:",
            "report_fields": [
                "searched name",
                "keep count",
                "match count",
                "removed count",
                "removed versions"
            ],
            "data": {
                "searched name": app_name,
                "keep count": str(keep_versions),
                "match count": str(len(apps)),
                "removed count": str(len(apps_to_delete)),
                "removed versions": ", ".join([app["primaryBundleVersion"] for app in apps_to_delete]) if len(apps_to_delete) > 0 else ""
            },
        }

if __name__ == "__main__":
    PROCESSOR = IntuneAppCleaner()
    PROCESSOR.execute_shell()