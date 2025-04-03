---
layout: default
title: Intune Uploader
processors:
    - IntuneAppUploader
    - IntuneAppPromoter
    - IntuneScriptUploader
    - IntuneAppCleaner
    - IntuneVTAppDeleter
    - IntuneTeamsNotifier
    - IntuneSlackNotifier
---
---

{% include intro.html %}

{% include ghinfo.html %}

<!-- Divider Line -->
<div class="w-full max-w-4xl mx-auto border-t border-gray-700 my-6 mt-10 mb-10"></div>

{% include recipes.html %}

{% include quickstart.html %}

<div>
    <div class="flex flex-col items-center text-center mb-16">
        <h2 class="text-white text-2xl font-bold mb-4">See Intune Uploader in Action!</h2>
        <p class="text-gray-300 text-lg mb-4">Watch how it automates app uploads and updates.</p>
        <img src="{{ site.url }}{{ site.baseurl }}/assets/intune-uploader-demo.gif" alt="Intune Uploader Demo" 
             class="demo-run w-full rounded-lg border border-gray-700">
    </div>
</div>

{% include processors.html %}

{% include faq.html %}

<script src="{{ '/js/loadMarkdown.js' | relative_url }}"></script>
<script src="{{ '/js/fetchRecipes.js' | relative_url }}"></script>
<script src="{{ '/js/githubInfo.js' | relative_url }}"></script>
<script src="{{ '/js/copyCommand.js' | relative_url }}"></script>
<script src="{{ '/js/utils.js' | relative_url }}"></script>