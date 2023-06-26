#!/usr/local/autopkg/python

"""
IntuneAppUploaderBase is a base class for processors that upload apps among other things to Microsoft Intune using the Microsoft Graph API.

Created by Tobias Almén
"""

import requests
import time
import json
import os
import hashlib
import base64
import hmac

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from autopkglib import Processor, ProcessorError

class IntuneUploaderBase(Processor):
    def obtain_accesstoken(self, client_id: str, client_secret: str, tenant_id: str) -> dict:
        """This function obtains an access token from the Microsoft Graph API.

        Args:
            client_id (str): The client ID to use for authenticating the request.
            client_secret (str): The client secret to use for authenticating the request.
            tenant_id (str): The tenant ID to use for authenticating the request.

        Returns:
            dict: The response from the request as a dictionary.
        """

        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response = json.loads(response.text)
            return response
        else:
            raise ProcessorError(f"Failed to obtain access token. Status code: {response.status_code}")

    def makeapirequest(self, endpoint: str, token: dict, q_param=None) -> dict:
        """This function makes a request to the Graph API and returns the response as a dictionary.

        Args:
            endpoint (str): The endpoint to make the request to.
            token (dict): The access token to use for authenticating the request.
            q_param (dict, optional): The query parameters to use for the request. Defaults to None.

        Returns:
            dict: The response from the request as a dictionary.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(token["access_token"]),
        }
        retry_response_codes = [502, 503, 504]
        if q_param is not None:
            response = requests.get(endpoint, headers=headers, params=q_param)
            if response.status_code in retry_response_codes:
                self.output("Ran into issues with Graph request, waiting 10 seconds and trying again...")
                time.sleep(10)
                response = requests.get(endpoint, headers=headers)
            elif response.status_code == 429:
                self.output(f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds")
                while response.status_code == 429:
                    time.sleep(int(response.headers["Retry-After"]))
                    response = requests.get(endpoint, headers=headers)
        else:
            response = requests.get(endpoint, headers=headers)
            if response.status_code in retry_response_codes:
                self.output("Ran into issues with Graph request, waiting 10 seconds and trying again...")
                time.sleep(10)
                response = requests.get(endpoint, headers=headers)
            elif response.status_code == 429:
                self.output(f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds")
                while response.status_code == 429:
                    time.sleep(int(response.headers["Retry-After"]))
                    response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            json_data = json.loads(response.text)

            if "@odata.nextLink" in json_data.keys():
                record = self.makeapirequest(json_data["@odata.nextLink"], token)
                entries = len(record["value"])
                count = 0
                while count < entries:
                    json_data["value"].append(record["value"][count])
                    count += 1

            return json_data

        else:
            raise ProcessorError("Request failed with ", response.status_code, " - ", response.text)

    def makeapirequestPost(self, postEndpoint: str, token: dict, q_param=None, json_data=None, status_code=200) -> dict:
        """This function makes a request to the Graph API and returns the response as a dictionary.

        Args:
            postEndpoint (str): Endpoint to make the request to.
            token (dict): The access token to use for authenticating the request.
            q_param (dict, optional): The query parameters to use for the request. Defaults to None.
            json_data (dict, optional): The json data to use for the request. Defaults to None.
            status_code (int, optional): The status code to check for. Defaults to 200.

        Returns:
            dict: If there is a response, the response from the request as a dictionary.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(token["access_token"]),
        }

        if q_param is not None:
            response = requests.post(postEndpoint, headers=headers, params=q_param, data=json_data)
        else:
            response = requests.post(postEndpoint, headers=headers, data=json_data)
        if response.status_code == status_code:
            if response.text:
                json_data = json.loads(response.text)
                return json_data
            else:
                pass
        elif response.status_code == 429:
            self.output(f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds")
            while response.status_code == 429:
                time.sleep(int(response.headers["Retry-After"]))
                response = requests.post(postEndpoint, headers=headers, data=json_data)
        else:
            raise ProcessorError("Request failed with ", response.status_code, " - ", response.text)

    def makeapirequestPatch(self, patchEndpoint: str, token: dict, q_param=None, json_data=None, status_code=200) -> None:
        """This function makes a request to the Graph API and returns the response as a dictionary.

        Args:
            postEndpoint (str): Endpoint to make the request to.
            token (dict): The access token to use for authenticating the request.
            q_param (dict, optional): The query parameters to use for the request. Defaults to None.
            json_data (dict, optional): The json data to use for the request. Defaults to None.
            status_code (int, optional): The status code to check for. Defaults to 200.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(token["access_token"]),
        }

        if q_param is not None:
            response = requests.patch(patchEndpoint, headers=headers, params=q_param, data=json_data)
        else:
            response = requests.patch(patchEndpoint, headers=headers, data=json_data)
        if response.status_code == status_code:
            pass
        else:
            raise ProcessorError("Request failed with ", response.status_code, " - ", response.text)

    def makeapirequestDelete(self, deleteEndpoint: str, token: dict, q_param=None, jdata=None, status_code=200) -> None:
        """This function makes a DELETE request to the Graph API and returns the response as a dictionary.

        Args:
            deleteEndpoint (str): Endpoint to make the request to.
            token (dict): The access token to use for authenticating the request.
            q_param (dict, optional): The query parameters to use for the request. Defaults to None.
            jdata (json, optional): The json data to use for the request. Defaults to None.
            status_code (int, optional): The status code to check for. Defaults to 200.

        Raises:
            ProcessorError: If the request fails.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(token["access_token"]),
        }

        if q_param is not None:
            response = requests.delete(
                deleteEndpoint, headers=headers, params=q_param, data=jdata
            )
        else:
            response = requests.delete(deleteEndpoint, headers=headers, data=jdata)
        if response.status_code == status_code:
            pass
        else:
            raise ProcessorError(
                "Request failed with ", response.status_code, " - ", response.text
            )

    def encrypt_app(self) -> tuple:
        """Encrypts the app with AES-256 in CBC mode.

        Returns:
            tuple: Tuple containing:
                str: The encrypted app.
                dict: The encryption info.
        """
        encryptionKey = os.urandom(32)
        hmacKey = os.urandom(32)
        initializationVector = os.urandom(16)
        profileIdentifier = "ProfileVersion1"
        fileDigestAlgorithm = "SHA256"

        with open(self.app_file, "rb") as f:
            plaintext = f.read()

        # Pad the plaintext to a multiple of 16 bytes
        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        # Encrypt the padded plaintext using AES-256 in CBC mode
        cipher = Cipher(algorithms.AES(encryptionKey), modes.CBC(initializationVector))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Combine the IV and encrypted data into a single byte string
        iv_data = initializationVector + encrypted_data

        # Generate a HMAC-SHA256 signature of the IV and encrypted data
        h = hmac.new(hmacKey, iv_data, hashlib.sha256)
        signature = h.digest()

        # Combine the signature and IV + encrypted data into a single byte string
        encrypted_pkg = signature + iv_data

        # Generate a base64-encoded string of the encrypted package
        encoded_pkg = base64.b64encode(encrypted_pkg).decode()

        # Generate a base64-encoded string of the encryption key
        encoded_key = base64.b64encode(encryptionKey).decode()

        # Generate a base64-encoded string of the HMAC key
        encoded_hmac_key = base64.b64encode(hmacKey).decode()

        # Generate a base64-encoded string of the file digest
        filebytes = open(self.app_file, "rb").read()
        filehash_sha256 = hashlib.sha256(filebytes)
        fileDigest = base64.b64encode(filehash_sha256.digest()).decode()

        # Generate the file encryption info dictionary
        fileEncryptionInfo = {}
        fileEncryptionInfo["@odata.type"] = "#microsoft.graph.fileEncryptionInfo"
        fileEncryptionInfo["encryptionKey"] = encoded_key
        fileEncryptionInfo["macKey"] = encoded_hmac_key
        fileEncryptionInfo["initializationVector"] = base64.b64encode(initializationVector).decode()
        fileEncryptionInfo["profileIdentifier"] = profileIdentifier
        fileEncryptionInfo["fileDigestAlgorithm"] = fileDigestAlgorithm
        fileEncryptionInfo["fileDigest"] = fileDigest
        fileEncryptionInfo["mac"] = base64.b64encode(signature).decode()

        return (encrypted_pkg, fileEncryptionInfo)

    def appFile(self, encrypted_app_file: str) -> dict:
        """This function creates the appFile dictionary for the Microsoft Graph API.

        Args:
            encrypted_app_file (str): The path to the encrypted application file.

        Returns:
            dict: The appFile dictionary.
        """
        appFile = {}
        appFile["@odata.type"] = "#microsoft.graph.mobileAppContentFile"
        appFile["name"] = os.path.basename(self.app_file)
        appFile["size"] = os.path.getsize(self.app_file)
        appFile["sizeEncrypted"] = os.path.getsize(encrypted_app_file)
        appFile["manifest"] = None
        appFile["isDependency"] = False
        return appFile

    def create_blocklist(self, file_path: str, azure_storage_uri: str) -> None:
        """Uploads a file to Azure Blob Storage using the block list upload mechanism.

        Args:
            file_path (str): The path to the file to upload.
            azure_storage_uri (str): The URI of the Azure Blob Storage container to upload the file to.
        """
        # Set the chunk size to 6 MB
        chunk_size = 6 * 1024 * 1024

        # Open the file in binary mode
        with open(file_path, "rb") as f:
            # Initialize the block IDs list and the block index
            block_ids = []
            block_index = 0

            # Read the file in chunks and upload each chunk as a block
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Generate a block ID for the current chunk
                block_id = base64.b64encode(f"block-{block_index:04}".encode()).decode()

                # Upload the chunk as a block
                uri = f"{azure_storage_uri}&comp=block&blockid={block_id}"
                headers = {"x-ms-blob-type": "BlockBlob"}
                try:
                    r = requests.put(uri, headers=headers, data=chunk)
                except:
                    raise ProcessorError("Failed to upload block")

                # Add the block ID to the list of block IDs
                block_ids.append(block_id)

                # Increment the block index
                block_index += 1

            # Generate the block list XML
            block_list_xml = "<BlockList>"
            for block_id in block_ids:
                block_list_xml += f"<Latest>{block_id}</Latest>"
            block_list_xml += "</BlockList>"

            # Upload the block list XML
            uri = f"{azure_storage_uri}&comp=blocklist"
            headers = {"Content-Type": "application/xml"}
            r = requests.put(uri, headers=headers, data=block_list_xml)

            if r.status_code != 201:
                raise ProcessorError("Failed to upload block list XML")

    def get_file_content_status(self) -> dict:
        """Returns the status of a file upload.

        Returns:
            dict: The file content status dictionary.
        """
        url = f"{self.BASE_ENDPOINT}/{self.request['id']}/microsoft.graph.macOSLobApp/contentVersions/{self.content_version_request['id']}/files/{self.content_file_request['id']}"
        return self.makeapirequest(url, self.token)

    def delete_app(self) -> None:
        """
        Deletes an app from Intune.
        """
        if self.request.get("id") and self.content_update is False:
            self.makeapirequestDelete(f"{self.BASE_ENDPOINT}/{self.request['id']}", self.token)
    
    def wait_for_file_upload(self) -> None:
        """Waits for a file to be uploaded.

        Raises:
            ProcessorError: If the file upload fails or times out.
        """
        attempt = 1
        status = self.get_file_content_status()

        while status["uploadState"] != "commitFileSuccess":
            time.sleep(5)
            status = self.get_file_content_status()
            attempt += 1
            if status["uploadState"] == "commitFileFailed":
                self.delete_app()
                raise ProcessorError("Failed to commit file")
            elif attempt > 20:
                self.delete_app()
                raise ProcessorError("Timed out waiting for file upload to complete")

    def wait_for_azure_storage_uri(self) -> None:
        """Waits for an Azure Storage upload URL to be generated.

        raises:
            ProcessorError: If the Azure Storage upload URL request fails or times out.
        """
        attempt = 1
        status = self.get_file_content_status()

        while status["uploadState"] != "azureStorageUriRequestSuccess":
            time.sleep(5)
            status = self.get_file_content_status()
            attempt += 1
            if status["uploadState"] == "azureStorageUriRequestFailed":
                self.delete_app()
                raise ProcessorError("Failed to get the Azure Storage upload URL")
            elif attempt > 20:
                self.delete_app()
                raise ProcessorError("Timed out waiting for the Azure Storage upload URL")

    def get_current_app(self, displayname: str, version: int) -> tuple:
        """Gets the current app from Intune.

        Args:
            displayname (str): The display name of the app.
            version (int): The version of the app.

        Returns:
            tuple: The result of the request and the data returned by the request.
        """
        params = {"$filter": f"displayName eq '{displayname}'", "$expand": "categories"}
        request = self.makeapirequest(f"{self.BASE_ENDPOINT}", self.token, q_param=params)
        result = None
        data = {}

        if request["value"]:
            for item in request["value"]:
                if item["primaryBundleVersion"] < version:
                    result = "update"
                    data = item
                else:
                    result = "current"
                    data = item

        return result, data

    def update_categories(self, category_names: list, current_categories: list) -> None:
        """Gets the category IDs for the specified category name(s).

        Args:
            category_names (list): The category name(s).
            current_categories (list): The current categories for the app.
        """
        # Define the URL to retrieve the mobile app categories
        category_url = "https://graph.microsoft.com/v1.0/deviceAppManagement/mobileAppCategories"

        # Retrieve the list of mobile app categories
        categories = self.makeapirequest(category_url, self.token, "")

        # If there are current categories, get their display names
        if current_categories:
            current_categories = [c["displayName"] for c in current_categories]
            # Filter the category IDs to only include those with display names in the category_names list and not in the current_categories list
            category_ids = [c for c in categories["value"] if c["displayName"] in category_names and c["displayName"] not in current_categories]
        # If there are no current categories, filter the category IDs to only include those with display names in the category_names list
        else:
            category_ids = [c for c in categories["value"] if c["displayName"] in category_names]

        # If there are category IDs to add, add them to the app
        if category_ids:
            for category_id in category_ids:
                # Create the data payload to add the category to the app
                data = json.dumps({
                    "@odata.id": f'{category_url}/{category_id["id"]}'
                })
                # Make the API request to add the category to the app
                self.makeapirequestPost(f'{self.BASE_ENDPOINT}/{self.request["id"]}/categories/$ref', self.token, "", data, 204)

    def encode_icon(self, icon_path: str) -> str:
        """Encodes an icon file as a base64 string.

        Args:
            icon_path (str): The path to the icon file.

        Returns:
            str: The base64 encoded icon file.
        """
        with open(icon_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def assign_app(self, app, assignment_info: dict) -> None:
        """Assigns an app to groups.
        
        Args:
            app (class): The app class.
            assignment_info (dict): The assignment information.
        """
        current_assignment = self.makeapirequest(f"{self.BASE_ENDPOINT}/{self.request['id']}/assignments", self.token)
        # Get the current group ids
        current_group_ids = [c["target"].get("groupId") for c in current_assignment["value"] if c["target"].get("groupId")]
        # Check if the group id is not in the current assignments
        missing_assignment = [a for a in assignment_info if a["group_id"] not in current_group_ids]
        data = {"mobileAppAssignments": []}

        if missing_assignment:
            for assignment in missing_assignment:
                # Assign the app to the group
                data["mobileAppAssignments"].append(
                    {
                        "@odata.type": "#microsoft.graph.mobileAppAssignment",
                        "target": {
                            "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                            "groupId": assignment["group_id"],
                        },
                        "intent": assignment["intent"],
                        "settings": None,
                    }
                )

            for assignment in current_assignment["value"]:
                data["mobileAppAssignments"].append(
                    {
                        "@odata.type": "#microsoft.graph.mobileAppAssignment",
                        "target": assignment["target"],
                        "intent": assignment["intent"],
                        "settings": None,
                    }
                )

            self.output(f"Updating assigningments for app {app.displayName} version {app.primaryBundleVersion}")
            self.makeapirequestPost(f"{self.BASE_ENDPOINT}/{self.request['id']}/assign", self.token, "", json.dumps(data), 200)
        
if __name__ == "__main__":
    PROCESSOR = IntuneUploaderBase()
    PROCESSOR.execute_shell()
