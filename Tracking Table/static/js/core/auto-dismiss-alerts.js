setTimeout(function () {
    document.querySelectorAll(".auto-dismiss-alert").forEach(function (el) {
        if (window.bootstrap && bootstrap.Alert) {
            bootstrap.Alert.getOrCreateInstance(el).close();
        }
    });
}, 5000);
