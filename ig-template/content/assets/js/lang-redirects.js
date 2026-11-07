// Overrides the script of the same path in fhir2.base.template 0.1.0, whose
// `return` sits outside the language check: it stops after the first language,
// which leaves everyone not reading that language on a blank page. Remove this
// file when the pinned base includes the fix.
doRedirect();

function doRedirect() {
  var userLang = navigator.language || navigator.userLanguage;
  var path = window.location.pathname;
  var pageName = path.substring(path.lastIndexOf('/') + 1);
  var suffix = window.location.search + window.location.hash;
  for (var i = 0; i < langs.length; i++) {
    if (userLang == langs[i] || userLang.startsWith(langs[i] + "-")) {
      window.location.replace(langs[i] + "/" + pageName + suffix);
      return;
    }
  }
  window.location.replace(langs[0] + "/" + pageName + suffix);
}
