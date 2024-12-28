window.addEventListener('unload', function (event) {
    console.log('Unload event triggered');
    navigator.sendBeacon('/logout', '');
});
