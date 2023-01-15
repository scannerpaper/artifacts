function sleep (milliseconds) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(), milliseconds)
    })
}

async function typeSlowly(page, selector, text) {
    for (const char of text) {
        await page.type(selector, char);
        await sleep(randomInRange(180,280));
    }
}

function getLineFunction(P, Q) {
    var a = Q.y - P.y
    var b = P.x - Q.x
    var c = a*(P.x) + b*(P.y)
    return function(x) {
        return (c - a*x)/b 
    }
}

async function randomMouseMove(page, n) {
    let points = [];
    for (let i = 0; i < n; i++) {
        let x = randomInRange(0, 1800);
        let y = randomInRange(0, 900);
        points.push({x, y});
    }
    for (let i = 0; i < n; i++) {
        let timestamp = Date.now();
        console.log('before', timestamp);
        await page.mouse.move(points[i].x, points[i].y);
        timestamp = Date.now();
        console.log('after', timestamp);
    }    
}


async function randomLineMouseMove(page, n) {
    for (let i = 0; i < n; i++) {
        initPos = {
            x: randomInRange(0, 1800),
            y: randomInRange(0, 900)
        }
    
        targetPos = {
            x: randomInRange(0, 1800),
            y: randomInRange(0, 900)
        }
            
        lineFuntion = getLineFunction(initPos, targetPos)

        nStep = 50
        if (initPos.x > targetPos.x) {
            step = -1 * (initPos.x - targetPos.x) / nStep
        } else {
            step = 1 * (targetPos.x - initPos.x) / nStep
        }
        xRange = []
        for (let i = 0; i < nStep; i++) {
            xRange.push(initPos.x + i*step)
        }
        for (const x of xRange) {
            y = lineFuntion(x)
            await page.mouse.move(x, y);
        }
    }    
}

async function mouseMove(page, element, zeroDiff) {
    initPos = {
        x: randomInRange(0, 1800),
        y: randomInRange(0, 900)
    }

    targetPos = {
        x: randomInRange(0, 1800),
        y: randomInRange(0, 900)
    }

    lineFuntion = getLineFunction(initPos, targetPos)

    nStep = 50
    if (initPos.x > targetPos.x) {
        step = -1 * (initPos.x - targetPos.x) / nStep
    } else {
        step = 1 * (targetPos.x - initPos.x) / nStep
    }
    xRange = []
    for (let i = 0; i < nStep; i++) {
        xRange.push(initPos.x + i*step)
    }

    for (const x of xRange) {
        y = lineFuntion(x)
        await page.mouse.move(x, y);
    }

    
}

function randomInRange(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

const methods = {
    login: async(page) => {
        for (let i = 0; i < 5; i++) {
            for (let j = 0; j < 5; j++) {
                await page.mouse.move(i*j, j*i);
                sleep(randomInRange(80,160))
            }
        }

        await Promise.all([
            page.click('a[class=login-link]'),
            page.waitForNavigation({waitUntil:'networkidle2'})]
        );

        for (let i = 0; i < 2; i++) {
            for (let j = 0; j < 4; j++) {
                await page.mouse.move(i*j, j*i);
                sleep(randomInRange(80,160))
            }
        }

        await typeSlowly(page, '#username', 'test');
        sleep(100);
        await typeSlowly(page, '#password', 'test');

        for (let i = 0; i < 2; i++) {
            for (let j = 0; j < 2; j++) {
                await page.mouse.move(i*j, j*i);
                sleep(randomInRange(80,160))
            }
        }

        await page.click('input[type=submit]');
    },

    crawlLinks: async(page) => {
        let zeroDiff;
        if (randomInRange(1, 12) < 4) {
            zeroDiff = true
        } else {
            zeroDiff = true
        }

        var aTags = await page.$$("a");

        aTags = aTags.slice(0, 40);

        for (let i = 0; i < aTags.length; i++) {
            
            let aTags = await page.$$("a");
            aTags = aTags.slice(0, 40)
            const aTag = aTags[i];
            try {
                await aTag.click()
            } catch (error) {
                continue
            }
            
            await sleep(100)
            await page.goBack()
            
        }

    },

    randomMouseMove: async(page) => {
        await randomMouseMove(page, 200);
    }
}

module.exports = methods;