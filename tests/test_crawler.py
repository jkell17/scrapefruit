from scrapefruit import ScrapeFruit


def test_run_twice():

    app = ScrapeFruit()
    app.run()

    app = ScrapeFruit()
    app.run()
    app.run()
