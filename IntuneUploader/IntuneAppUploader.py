#!/usr/local/autopkg/python

"""
This processor uploads an app to Microsoft Intune using the Microsoft Graph API, it also assigns the app to group(s) if specified
and adds the app to categories if specified. It also supports updating the app if it already exists in Intune.

It is heavily inspired by the IntuneImporter processor by @SteveKueng.

Created by Tobias Almén
"""

import sys
import tempfile
import json
import os

from dataclasses import dataclass, field
from autopkglib import ProcessorError

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase

__all__ = ["IntuneAppUploader"]


class IntuneAppUploader(IntuneUploaderBase):
    description = __doc__
    input_variables = {
        "CLIENT_ID": {
            "required": True,
            "description": "The client ID to use for authenticating the request.",
        },
        "CLIENT_SECRET": {
            "required": True,
            "description": "The client secret to use for authenticating the request.",
        },
        "TENANT_ID": {
            "required": True,
            "description": "The tenant ID to use for authenticating the request.",
        },
        "app_file": {
            "required": True,
            "description": "The app file to upload to Intune.",
        },
        "displayname": {
            "required": True,
            "description": "The display name of the app.",
        },
        "description": {
            "required": True,
            "description": "The description of the app.",
        },
        "publisher": {
            "required": True,
            "description": "The publisher of the app.",
        },
        "owner": {
            "required": False,
            "description": "The owner of the app.",
        },
        "developer": {
            "required": False,
            "description": "The developer of the app.",
        },
        "categories": {
            "required": False,
            "description": "An array of categories to add to the app by name. Must be created in Intune first"
        },
        "information_url": {
            "required": False,
            "description": "The information URL of the app.",
        },
        "privacy_information_url": {
            "required": False,
            "description": "The privacy information URL of the app.",
        },
        "notes": {
            "required": False,
            "description": "The notes of the app.",
        },
        "bundleId": {
            "required": True,
            "description": "The bundle ID of the app.",
        },
        "bundleVersion": {
            "required": True,
            "description": "The bundle version of the app.",
        },
        "minimumSupportedOperatingSystem": {
            "required": False,
            "description": "The minimum supported operating system of the app.",
            "default": "v11_0",
        },
        "install_as_managed": {
            "required": False,
            "description": "Whether to install the app as managed or not.",
            "default": False,
        },
        "icon": {
            "required": False,
            "description": "Path to the PNG icon of the app.",
        },
        "ignore_current_app": {
            "required": False,
            "description": "Whether to ignore the current app in Intune and create either way.",
            "default": False,
        },
        "ignore_current_version": {
            "required": False,
            "description": "Whether to ignore the current version in Intune and upload binary either way.",
            "default": False,
        },
        "assignment_info": {
            "required": False,
            "description": "The assignment info of the app. Provided as an array of dicts containing keys 'group_id' and 'intent'. See https://github.com/almenscorner/intune-uploader/wiki/IntuneAppUploader#input-variables for more information.",
        },
    }
    output_variables = {
        "name": {
            "description": "The name of the app that was uploaded."
        },
        "version": {
            "description": "The version of the app that was uploaded or updated."
        },
        "intune_app_id": {
            "description": "The ID of the app that was uploaded or updated."
        },
        "content_version_id": {
            "description": "The content version ID of the app that was uploaded or updated."
        },
        "intune_app_changed": {
            "description": "Returns True if the app was updated or created, False if not."
        },
        "intuneappuploader_summary_result": {
            "description": "Description of interesting results.",
        },
    }

    def main(self):
        # Set up variables
        self.BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"
        self.CLIENT_ID = self.env.get("CLIENT_ID")
        self.CLIENT_SECRET = self.env.get("CLIENT_SECRET")
        self.TENANT_ID = self.env.get("TENANT_ID")
        self.RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR")
        # Set the content_updated variable to false
        self.content_update = False
        # Set the intune_app_changed variable to false
        self.env["intune_app_changed"] = False
        # Get the app info from the environment variables
        self.app_file = self.env.get("app_file")
        app_displayname = self.env.get("displayname")
        app_description = self.env.get("description")
        app_publisher = self.env.get("publisher")
        app_owner = self.env.get("owner")
        app_developer = self.env.get("developer")
        app_categories = self.env.get("categories")
        app_information_url = self.env.get("information_url")
        app_privacy_information_url = self.env.get("privacy_information_url")
        app_notes = self.env.get("notes")
        app_bundleId = self.env.get("bundleId")
        app_bundleVersion = self.env.get("bundleVersion")
        app_type = os.path.splitext(self.app_file)[1][1:]
        app_assignment_info = self.env.get("assignment_info")
        app_install_as_managed = self.env.get("install_as_managed")
        app_minimum_os_version = self.env.get("minimumSupportedOperatingSystem")
        app_icon = self.env.get("icon")
        filename = os.path.basename(self.app_file)
        ignore_current_app = self.env.get("ignore_current_app")
        ignore_current_version = self.env.get("ignore_current_version")

        # Get the access token
        self.token = self.obtain_accesstoken(self.CLIENT_ID, self.CLIENT_SECRET, self.TENANT_ID)

        @dataclass
        class App:
            """
            A class to represent an app.
            """

            displayName: str = app_displayname
            description: str = app_description
            publisher: str = app_publisher
            owner: str = app_owner
            developer: str = app_developer
            notes: str = app_notes
            fileName: str = filename
            privacyInformationUrl: str = app_privacy_information_url
            informationUrl: str = app_information_url
            primaryBundleId: str = app_bundleId
            primaryBundleVersion: str = app_bundleVersion
            ignoreVersionDetection: bool = False
            installAsManaged: bool = app_install_as_managed
            minimumSupportedOperatingSystem: dict = field(default_factory=dict)
            largeIcon: dict = field(default_factory=dict, init=False)

            def __post_init__(self):
                """
                Creates app data based on the app type.
                """
                
                if app_type == "dmg":
                    self.includedApps = [
                        {
                            "@odata.type": "#microsoft.graph.macOSIncludedApp",
                            "bundleId": app_bundleId,
                            "bundleVersion": app_bundleVersion,
                        }
                    ]
                    self.__dict__["@odata.type"] = "#microsoft.graph.macOSDmgApp"
                    
                elif app_type == "pkg":
                    self.childApps = [
                        {
                            "@odata.type": "#microsoft.graph.macOSChildApp",
                            "bundleId": app_bundleId,
                            "bundleVersion": app_bundleVersion,
                        }
                    ]
                    self.__dict__["@odata.type"] = "#microsoft.graph.macOSPkgApp"
                    
                self.minimumSupportedOperatingSystem = {
                    "@odata.type": "#microsoft.graph.macOSMinimumOperatingSystem",
                    app_minimum_os_version: True,
                }

        # Create the app data
        app_data = App()
        if app_icon:
            app_data.largeIcon = {
                "type": "image/png",
                "value": self.encode_icon(app_icon),
            }
            
        # Get the app data as a dictionary
        app_data_dict = app_data.__dict__
        # Convert the dictionary to JSON
        data = json.dumps(app_data_dict)
        # Check if app already exists
        current_app_result, current_app_data = self.get_current_app(app_displayname, app_bundleVersion)

        # If the ignore_current_app variable is set to true, create the app regardless of whether it already exists
        if ignore_current_app and not current_app_data:
            raise ProcessorError("App not found in Intune. Please set ignore_current_app to false.")
        if ignore_current_app and app_bundleVersion != current_app_data["primaryBundleVersion"]:
            self.output(f"Creating app {app_data.displayName} version {app_bundleVersion}")
            # Create the app
            self.request = self.makeapirequestPost(f"{self.BASE_ENDPOINT}", self.token, "", data, 201)

        # If the ignore_current_app variable is not set to true, check if the app already exists and update it if necessary
        else:
            # If the app needs to be updated or the current version should be ignored
            if current_app_result == "update" or ignore_current_version is True:
                # If the app is not found, raise an error
                if not current_app_data:
                    raise ProcessorError("App not found in Intune. Please set ignore_current_version to false.")
                
                # If the app version is the same, update the file contents
                if current_app_data["primaryBundleVersion"] == app_bundleVersion:
                    self.output(
                        f'Upadating File Contents for app {current_app_data["displayName"]} version {current_app_data["primaryBundleVersion"]}'
                    )
                # If the app version is different, update the app
                else:
                    self.output(
                        f'Updating app {current_app_data["displayName"]} from {current_app_data["primaryBundleVersion"]} to version {app_bundleVersion}'
                    )
                # Update the app
                self.content_update = True
                self.makeapirequestPatch(f'{self.BASE_ENDPOINT}/{current_app_data["id"]}', self.token, "", data, 204)
                self.request = current_app_data
                
            # If the app is up to date and the current version should not be ignored
            if current_app_result == "current" and ignore_current_version is False:
                self.output(
                    f'App {current_app_data["displayName"]} version {current_app_data["primaryBundleVersion"]} is up to date'
                )
                return
                
            # If the app does not exist
            if current_app_result is None:
                self.output(f"Creating app {app_data.displayName} version {app_data.primaryBundleVersion}")
                # Create the app
                self.request = self.makeapirequestPost(f"{self.BASE_ENDPOINT}", self.token, "", data, 201)
        
        # Create the content version
        content_version_url = f'{self.BASE_ENDPOINT}/{self.request["id"]}/{str(app_data_dict["@odata.type"]).replace("#","")}/contentVersions'
        self.content_version_request = self.makeapirequestPost(
            content_version_url,
            self.token,
            "",
            json.dumps({}),
            201,
        )

        if not self.content_version_request:
            self.output("Failed to create content version, trying again")
            self.content_version_request = self.makeapirequestPost(
                content_version_url,
                self.token,
                "",
                json.dumps({}),
                201,
            )
            if not self.content_version_request:
                self.delete_app()
                raise ProcessorError("Failed to create content version")

        # Encrypt the app
        encryptionData, encryptionInfo = self.encrypt_app()

        # Write the encryption data to a file
        new_file, tempfilename = tempfile.mkstemp(dir=self.RECIPE_CACHE_DIR)
        with open(new_file, "wb") as f:
            f.write(encryptionData)

        # Get the app file info
        content_file = self.appFile(tempfilename)
        # Post the app file info
        data = json.dumps(content_file)
        self.content_file_request = self.makeapirequestPost(
            f'{self.BASE_ENDPOINT}/{self.request["id"]}/microsoft.graph.macOSLobApp/contentVersions/{self.content_version_request["id"]}/files',
            self.token,
            "",
            data,
            201,
        )

        # Get the content file upload URL
        file_content_request_url = f'{self.BASE_ENDPOINT}/{self.request["id"]}/microsoft.graph.macOSLobApp/contentVersions/{self.content_version_request["id"]}/files/{self.content_file_request["id"]}'
        file_content_request = self.makeapirequest(
            file_content_request_url,
            self.token,
        )

        self.wait_for_azure_storage_uri()

        if not file_content_request["azureStorageUri"]:
            # try again
            file_content_request = self.makeapirequest(
                file_content_request_url,
                self.token,
            )
            
            if not file_content_request["azureStorageUri"]:
                self.delete_app()
                raise ProcessorError("Failed to get the Azure Storage upload URL")
        
        # Create the block list
        self.create_blocklist(tempfilename, file_content_request["azureStorageUri"])

        # Clean up temp file
        os.unlink(tempfilename)

        # Commit the file
        data = json.dumps({"fileEncryptionInfo": encryptionInfo})
        self.makeapirequestPost(
            f'{self.BASE_ENDPOINT}/{self.request["id"]}/microsoft.graph.macOSLobApp/contentVersions/{self.content_version_request["id"]}/files/{self.content_file_request["id"]}/commit',
            self.token,
            "",
            data,
            200,
        )

        # Wait for the file to upload
        self.wait_for_file_upload()

        # Patch the app to use the new content version
        data = {
            "@odata.type": "#microsoft.graph.macOSLobApp",
            "committedContentVersion": self.content_version_request["id"],
        }

        self.makeapirequestPatch(f"{self.BASE_ENDPOINT}/{self.request['id']}", self.token, "", json.dumps(data), 204)
        
        if app_categories:
            self.update_categories(app_categories, self.request.get("categories"))
        
        if app_assignment_info:
            self.assign_app(app_data, app_assignment_info)

        self.env["intune_app_changed"] = True
        self.env["intuneappuploader_summary_result"] = {
            "summary_text": "The following new items were imported into Intune:",
            "report_fields": [
                "name",
                "version",
                "intune_app_id",
                "content_version_id",
            ],
            "data": {
                "name": app_displayname,
                "version": app_bundleVersion,
                "intune_app_id": self.request["id"],
                "content_version_id": self.content_version_request["id"],
            },
        }

if __name__ == "__main__":
    PROCESSOR = IntuneAppUploader()
    PROCESSOR.execute_shell()
