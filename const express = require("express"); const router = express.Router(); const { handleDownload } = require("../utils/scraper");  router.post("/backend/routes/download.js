const express = require("express");
const router = express.Router();
const { handleDownload } = require("../utils/scraper");

router.post("/download", async (req, res) => {
    const { url, type } = req.body;

    try {
        const result = await handleDownload(url, type);

        res.json({
            status: true,
            download: result
        });

    } catch (err) {
        res.json({
            status: false,
            message: err.message
        });
    }
});

module.exports = router;
