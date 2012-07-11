var parts = window.location.search.substr(1).split("=");
if (parts.length == 2) {
    if (parts[0] == "debug" && parts[1] == "true") {
        var stats = new Stats();
        stats.setMode(0); // 0: fps, 1: ms
        document.body.appendChild( stats.domElement );

        // Align top-left
        stats.domElement.style.position = 'absolute';
        stats.domElement.style.right = '0px';
        stats.domElement.style.top = '0px';
        stats.begin();
        setInterval( function () {
            stats.end();
            stats.begin();
        }, 1000 / 60);
    }
}