const scenarios = require('./scenarios');

const scraperObject = {
    url: 'http://localhost:8080/',
    async scraper(browser){
        let page = await browser.newPage();
        page.setViewport({ width: 0, height: 0 });
        page.setUserAgent(
            "test"
        );
        // await page.setViewport({width:0, height:0});
        console.log(`Navigating to ${this.url}...`);
        await page.setDefaultNavigationTimeout(0);
        const resp = await page.goto(this.url);
        try {
            await scenarios.crawlLinks(page);
        } catch (error) {
            console.log(error);
            process.exit()
        }
        process.exit()
    }
}

module.exports = scraperObject;

