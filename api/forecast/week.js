/**
 * Vercel Serverless Function - 一週天氣預報
 * 路徑：/api/forecast/week
 */
const fetch = require('node-fetch');

const CWA_API_KEY = process.env.CWA_API_KEY;
const CWA_BASE_URL = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore';

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const { locationName } = req.query;
    const params = new URLSearchParams({ format: 'JSON' });
    if (locationName) params.set('LocationName', locationName);

    const response = await fetch(`${CWA_BASE_URL}/F-D0047-091?${params.toString()}`, {
      headers: { 'Authorization': CWA_API_KEY, 'Accept': 'application/json' }
    });
    const data = await response.json();

    if (data.success === 'true' || data.success === true) {
      const records = data.records;
      const locationsArr = records.Locations || records.locations || [];
      let locations = null;

      if (locationsArr.length > 0) {
        locations = locationsArr[0].Location || locationsArr[0].location;
      }

      // 手動過濾縣市
      if (locations && locations.length > 1 && locationName) {
        const filtered = locations.filter(loc =>
          (loc.LocationName || loc.locationName) === locationName
        );
        if (filtered.length > 0) locations = filtered;
      }

      if (locations && locations.length > 0) {
        res.status(200).json({ success: true, data: locations });
      } else {
        res.status(404).json({ success: false, message: '查無天氣預報資料' });
      }
    } else {
      res.status(400).json({ success: false, message: '無法取得一週天氣資料' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
