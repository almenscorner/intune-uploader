# intune-uploader

## Description
This project aims to simplify the process of creating and updating apps and other payloads in Intune by leveraging the power of [AutoPkg](https://github.com/autopkg/autopkg). With AutoPkg, you can automate the process of downloading, packaging, and uploading apps to Intune, saving you time and effort.

Moving forward, additional processors for Intune might be added to this project that uploads more data like Shell scripts to provide a complete automated deployment process. This is why the base class [IntuneUploaderBase](IntuneUploader/IntuneUploaderLib/IntuneUploaderBase.py) was created, to allow for easier creation of additional processors. Contributions are welcome!

Ideas for future processors:
- Teams notifier processor

For getting started help and documentation, please visit the wiki pages:
- [Intune App Uploader](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppUploader)
- [Intune App Icon Getter](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppIconGetter)
- [Intune App Cleaner](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppCleaner)
- [Intune Script Uploader](https://github.com/almenscorner/intune-uploader/wiki/IntuneScriptUploader)
- [Intune App Promoter](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppPromoter)

Join the discussions on Slack  <a href="https://macadmins.slack.com/archives/C05EDN7P337">
    <img height="25" src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/306_Slack_logo-256.png"/>
</a>

### IntuneAppUploader - LOB apps (managed PKG)
LOB type apps support has been added. It is required that you provide a pkg file that is signed with a valid Apple Developer ID certificate and notarized. This app type can be deploy apps in a "available" manner rather than "required". This means that the user can choose to install the app or not. This is useful for apps that are not required for the user to do their job, but are nice to have.

In the override file for a signed and notarized pkg, set the following key to upload as a LOB app:
```xml
<key>lob_app</key>
<true/>
```

## Development
Pull requests are welcome!

Some ground rules before submitting a PR,
* Install [pre-commit](https://pre-commit.com)
   * Once installed, run `pre-commit install` in the forked repo
* Make sure all tests pass before submitting a PR
