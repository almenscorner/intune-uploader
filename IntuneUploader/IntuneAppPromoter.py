#!/usr/local/autopkg/python

"""
This processor promotes apps in Intune based on the input variables. It will promote the app to the first group in the promotion_info list.
If the app has been promoted before, it will promote the app to the next group in the list, if the number of days since the last promotion is greater than or equal to the number of days in the previous ring.

Created by Tobias Almén
"""

import sys
import os
import json
from datetime import datetime

__all__ = ["IntuneAppPromoter"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase


class App:
    def __init__(self, app_name, app_version):
        self.displayName = app_name
        self.primaryBundleVersion = app_version


class IntuneAppPromoter(IntuneUploaderBase):
    "This processor promotes an app to groups in Intune based on the input variables."
    description = __doc__
    input_variables = {
        "display_name": {
            "required": True,
            "description": "The name of the app to assign.",
        },
        "blacklist_version": {
            "required": False,
            "description": "If the app version is in this list, it will not be assigned.",
        },
        "promotion_info": {
            "required": True,
            "description": "A list of lists containing the assignment info and rings for the app.",
        },
    }
    output_variables = {"intuneapppromoter_summary_result": {"description": "Description of interesting results."}}

    def main(self):
        # Set variables
        self.BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"
        self.CLIENT_ID = self.env.get("CLIENT_ID")
        self.CLIENT_SECRET = self.env.get("CLIENT_SECRET")
        self.TENANT_ID = self.env.get("TENANT_ID")
        app_name = self.env.get("display_name")
        app_version = self.env.get("version")
        app_blacklist_versions = self.env.get("blacklist_versions")
        promotion_info = self.env.get("promotion_info")

        def promote_app(group):
            notes = {
                "promotion_date": date.strftime("%Y-%m-%d"),
                "ring": group.get("ring"),
            }
            self.assign_app(app, [group])
            notes["ring"] = group.get("ring")
            data = json.dumps(
                {
                    "notes": json.dumps(notes),
                    "@odata.type": intune_app.get("@odata.type"),
                }
            )
            self.makeapirequestPatch(
                f"{self.BASE_ENDPOINT}/{intune_app.get('id')}",
                self.token,
                None,
                data,
                204,
            )
            promotions.append({"version": app_version, "ring": group.get("ring")})

        # Get access token
        self.token = self.obtain_accesstoken(self.CLIENT_ID, self.CLIENT_SECRET, self.TENANT_ID)

        # Check if promotion info is set
        if promotion_info == None:
            self.output("No promotion info found, exiting.")
            return None

        promotions = []

        # Get matching apps
        intune_apps = self.get_matching_apps(app_name)
        # If no apps are found, exit
        if intune_apps == None:
            self.output(f"No app found with name: {app_name}, exiting.")
            return None

        formatted_date_string = datetime.now().strftime("%Y-%m-%d")
        date = datetime.strptime(formatted_date_string, "%Y-%m-%d")

        def match_version(version, blacklist_versions):
            # Check if version is a wildcard
            for v in blacklist_versions:
                if v.endswith("*") and version.startswith(v[:-1]):
                    return True
            # Check if version is in blacklist
            if version in blacklist_versions:
                return True

            # If no match, return False
            return False

        for intune_app in intune_apps:
            self.request = intune_app
            # Create app object
            app = App(app_name, app_version)

            # Get assignments for app
            assignments = self.makeapirequest(
                f"{self.BASE_ENDPOINT}/{intune_app.get('id')}/assignments",
                self.token,
                None,
            )
            current_group_ids = [c["target"].get("groupId") for c in assignments["value"] if c["target"].get("groupId")]

            # Check if app version is blacklisted
            version = lambda v: v.get("primaryBundleVersion") if v.get("primaryBundleVersion") else v.get("buildNumber")
            if app_blacklist_versions is not None and (
                match_version(version(intune_app), app_blacklist_versions)
                or match_version(version(intune_app), app_blacklist_versions)
            ):
                self.output(f"App version {version(intune_app)} is blacklisted, skipping version.")
                continue
            # Get all promotion group ids
            promotion_ids = [group.get("group_id") for group in promotion_info]
            # If all promotion group ids are in current group ids, exits
            if all(id in current_group_ids for id in promotion_ids):
                self.output(f"{intune_app.get('displayName')} {app_version} is already assigned to all groups, skipping.")
                return None

            # If app has not been promoted before, assign to first group in promotion_info
            if not intune_app.get("notes"):
                promote_app(promotion_info[0])
            # If app has been promoted before, check if it is time to promote again
            else:
                # Get days since last promotion and previous ring
                notes_data = json.loads(intune_app.get("notes"))
                promote_date = notes_data.get("promotion_date")
                delta = (date - datetime.strptime(promote_date, "%Y-%m-%d")).days
                previous_ring = notes_data.get("ring")
                previous_ring_days = sum([group.get("days") for group in promotion_info if group.get("ring") == previous_ring])

                for group in promotion_info:
                    # If the delta is greater than or equal to the previous ring days, promote
                    if group.get("group_id") not in current_group_ids and delta >= previous_ring_days:
                        promote_app(group)
                        break

        self.env["intuneapppromoter_summary_result"] = {
            "summary_text": "Summary of IntuneAppPromoter results:",
            "report_fields": ["app name", "promotions", "blacklisted versions"],
            "data": {
                "app name": app_name,
                "promotions": ", ".join([f"{promotion.get('version')} ({promotion.get('ring')})" for promotion in promotions])
                if len(promotions) > 0
                else "",
                "blacklisted versions": ", ".join(app_blacklist_versions) if app_blacklist_versions is not None else "",
            },
        }


if __name__ == "__main__":
    processor = IntuneAppPromoter()
    processor.execute_shell()
