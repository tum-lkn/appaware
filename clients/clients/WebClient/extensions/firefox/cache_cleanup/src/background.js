function cleanCache() {
    console.log("cleaning Cache")
	browser.browsingData.removeCache({})
}

function logOnBefore(details) {
  console.log("onBeforeNavigate to: " + details.url);
  cleanCache()
}

browser.browserAction.onClicked.addListener(cleanCache);
browser.webNavigation.onBeforeNavigate.addListener(logOnBefore);
