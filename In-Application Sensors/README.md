# Reference
The baseline of the in-application sensors is the [evtrack](https://github.com/luileito/evtrack) repository. We have modified different parts of the code to match our requirements.

## Usage

  First, you need to include in `js/trackLib.js` file or its minified version `js/0laso3vm.min.js` in the target webpage.

  Then, add the following script to the `<head>` of the page to setup tracking.

```javascript
<script>
    (function(){
        TrackUI.record({
        postServer: "http://x.x.x.x",
        regularEvents: "*",
        pollingEvents: "*",
        pollingMs: 0,
        debug: false,
        postInterval: 1,
        });
    })();
</script>
```