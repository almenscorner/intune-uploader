#!/usr/local/autopkg/python

"""
This processor uploads a script to Microsoft Intune using the Microsoft Graph API, it also assigns the script to group(s) if specified
It also supports updating the script if it already exists in Intune.

Created by Tobias Almén
"""

import sys
import os
import base64
import json

from autopkglib import ProcessorError
from dataclasses import dataclass, field

__all__ = ["IntuneScriptUploader"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase


class IntuneScriptUploader(IntuneUploaderBase):
    """Uploads a script to Microsoft Intune using the Microsoft Graph API."""

    input_variables = {
        "script_path": {
            "required": True,
            "description": "Path to script to upload.",
        },
        "description": {
            "required": False,
            "description": "Description of script.",
        },
        "display_name": {
            "required": False,
            "description": "Display name of script. If not provided, will use IU-<filename>.",
        },
        "run_as_account": {
            "required": False,
            "description": "Run as account.",
            "default": "system",
        },
        "retry_count": {
            "required": False,
            "description": "Number of times to retry script.",
            "default": 3,
        },
        "block_execution_notifications": {
            "required": False,
            "description": "Block execution notifications.",
            "default": True,
        },
        "assignment_info": {
            "required": False,
            "description": "The assignment info of the app. Provided as an array of dicts containing keys 'group_id' and 'intent'. See https://github.com/almenscorner/intune-uploader/wiki/IntuneScriptUploader#input-variables for more information.",
        },
    }
    output_variables = {
        "intunescriptuploader_summary_result": {"description": "Description of interesting results."}
    }
    
    def main(self):
        
        def assign_script(self, script_id: str, assignment_info: dict) -> None:
            """Assigns a script to groups.
            
            Args:
                script_id (str): The id of the script.
                assignment_info (dict): The assignment information.
            """
            assignment_endpoint = self.BASE_ENDPOINT.replace("deviceShellScripts", "deviceManagementScripts")
            current_assignment = self.makeapirequest(f"{assignment_endpoint}/{script_id}/assignments", self.token)
            # Get the current group ids
            current_group_ids = [c["target"].get("groupId") for c in current_assignment["value"] if c["target"].get("groupId")]
            # Check if the group id is not in the current assignments
            missing_assignment = [a for a in assignment_info if a["group_id"] not in current_group_ids]
            data = {"deviceManagementScriptAssignments": []}

            if missing_assignment:
                for assignment in missing_assignment:
                    if assignment["intent"] == "exclude":
                        type = "#microsoft.graph.exclusionGroupAssignmentTarget"
                    else:
                        type = "#microsoft.graph.groupAssignmentTarget"
                        
                    # Assign the script to the group
                    data["deviceManagementScriptAssignments"].append(
                        {
                            "target": {
                                "@odata.type": type,
                                "groupId": assignment["group_id"],
                            },
                        }
                    )

                for assignment in current_assignment["value"]:
                    data["deviceManagementScriptAssignments"].append(
                        {
                            "target": assignment["target"],
                        }
                    )
                    
                self.makeapirequestPost(f"{assignment_endpoint}/{script_id}/assign", self.token, "", json.dumps(data), 200)
                    
        # Set variables
        self.BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceShellScripts"
        self.CLIENT_ID = self.env.get("CLIENT_ID")
        self.CLIENT_SECRET = self.env.get("CLIENT_SECRET")
        self.TENANT_ID = self.env.get("TENANT_ID")
        script_path = self.env.get("script_path")
        script_description = self.env.get("description")
        script_name = self.env.get("display_name")
        run_as_account = self.env.get("run_as_account")
        retry_count = self.env.get("retry_count")
        block_execution_notifications = self.env.get("block_execution_notifications")
        assignment_info = self.env.get("assignment_info")
        filename = os.path.basename(script_path)
        action = ""
        
        # Check if script name is provided
        if not script_name:
            # If not, use filename
            script_name = f"IU-{os.path.basename(script_path).removesuffix(os.path.splitext(script_path)[1])}"

        # Check if script path exists
        if os.path.exists(script_path):
            if os.path.isdir(script_path):
                raise ProcessorError(f"Path is a directory: {script_path}")
        else:
            raise ProcessorError(f"Path does not exist: {script_path}")
        
        # Get token
        self.token = self.obtain_accesstoken(self.CLIENT_ID, self.CLIENT_SECRET, self.TENANT_ID)
        
        @dataclass
        class ShellScript:
            """
            Class to represent a shell script.
            """
            
            displayName: str = script_name
            description: str = script_description
            scriptContent: str = field(default_factory=str)
            retryCount: int = retry_count
            runAsAccount: str = run_as_account
            blockExecutionNotifications: bool = block_execution_notifications
            fileName: str = filename
        
        # Create script object
        script = ShellScript()
        
        with open(script_path, "r") as f:
            # Encode script content as base64
            script.scriptContent = base64.b64encode(f.read().encode("utf-8")).decode("utf-8")
        
        # Convert script object to json
        script_data = json.dumps(script.__dict__)
        
        # Check if script exists in Intune
        params = {"$filter": f"displayName eq '{script_name}'"}
        current_script = self.makeapirequest(self.BASE_ENDPOINT, self.token, params)
        
        if current_script["value"]:
            # Get script content
            current_script_content = self.makeapirequest(f"{self.BASE_ENDPOINT}/{current_script['value'][0]['id']}", self.token)
            # Check if script matches current script
            if current_script_content["scriptContent"] == script.scriptContent:
                self.output(f"Script '{script_name}' already exists and matches current script.")
                action = "none"
            else:
                self.output(f"Script '{script_name}' already exists but does not match current script. Updating script.")
                action = "update"
                self.makeapirequestPatch(f"{self.BASE_ENDPOINT}('{current_script_content['id']}')", self.token, "", script_data)
                
        else:
            self.output(f"Script '{script_name}' does not exist. Creating script.")
            action = "create"
            create_request = self.makeapirequestPost(self.BASE_ENDPOINT, self.token, None, script_data, 201)
            
        
        if assignment_info and action != "none":
            # Assign script to groups
            if action == "create":
                script_id = create_request["id"]
            else:
                script_id = current_script["value"][0]["id"]
                
            assign_script(self, script_id, assignment_info)

        self.env["intunescriptuploader_summary_result"] = {
            "summary_text": "Summary of IntuneScriptUploader results:",
            "report_fields": [
                "script name",
                "script path",
                "run as account",
                "retry count",
                "block execution notifications",
                "action",
            ],
            "data": {
                "script name": script_name,
                "script path": script_path,
                "run as account": run_as_account,
                "retry count": str(retry_count),
                "block execution notifications": str(block_execution_notifications),
                "action": action,
            },
        }

if __name__ == "__main__":
    PROCESSOR = IntuneScriptUploader()
    PROCESSOR.execute_shell()