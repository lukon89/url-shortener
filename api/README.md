



Testing

1. Creating shortened url
curl -X POST http://localhost:8000/api/shrt/ -H "Content-Type: application/json" -d '{"url": "https://example.com/very/long/url"}'

2. Retrieve long url from code
curl http://localhost:8000/api/shrt/<code>/