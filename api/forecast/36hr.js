/**
 * Vercel Serverless Function - 36小時天氣預報
 * 路徑：/api/forecast/36hr
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
    if (locationName) params.set('locationName', locationName);

    const response = await fetch(`${CWA_BASE_URL}/F-C0032-001?${params.toString()}`, {
      headers: { 'Authorization': CWA_API_KEY, 'Accept': 'application/json' }
    });
    const data = await response.json();

    if (data.success === 'true' || data.success === true) {
      res.status(200).json({ success: true, data: data.records.location });
    } else {
      res.status(400).json({ success: false, message: '無法取得天氣資料' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
