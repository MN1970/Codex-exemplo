// CloudFront Function for Single Page Application (SPA) Routing
// This function rewrites requests to index.html for client-side routing
// while preserving requests to actual static files

function handler(event) {
  var request = event.request;
  var uri = request.uri;

  // List of paths that should NOT be rewritten to index.html
  var staticPaths = [
    '/index.html',
    '/favicon.ico',
    '/manifest.json',
    '/robots.txt'
  ];

  // Check if the URI is for a static file (has a file extension)
  if (uri.match(/\.\w+$/)) {
    // It's a file with an extension (e.g., .js, .css, .png)
    return request;
  }

  // Check if it's in the static paths list
  if (staticPaths.indexOf(uri) !== -1) {
    return request;
  }

  // Check for API routes (shouldn't be rewritten)
  if (uri.startsWith('/api/')) {
    return request;
  }

  // For all other requests, rewrite to index.html for SPA routing
  request.uri = '/index.html';

  return request;
}
