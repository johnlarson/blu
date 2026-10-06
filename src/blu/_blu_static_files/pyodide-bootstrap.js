import 'https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.js';
import * as react from 'https://esm.sh/react';
import * as reactDom from 'https://esm.sh/react-dom/client';
import * as util from '/_blu_internal/static/util.js';

bootstrapPyodide();

async function bootstrapPyodide() {
  const pyodide = await loadPyodide();
  const config = JSON.parse(document.getElementById('config').textContent);
  await Promise.all([
    unpackArchivePyodide('/_blu_internal/app_pkg.zip', './app', pyodide),
    unpackArchivePyodide('/_blu_internal/blu_pkg.zip', './blu', pyodide),
    pyodide.registerJsModule('_react', react),
    pyodide.registerJsModule('_react_dom', reactDom),
    pyodide.registerJsModule('_js_util', util),
    pyodide.loadPackage('micropip'),
  ]);
  await pyodide.pyimport('blu._client_main.pyodide').main(config.packages)
}

async function unpackArchivePyodide(url, dest, pyodide) {
  const zipResponse = await fetch(url);
  const buffer = await zipResponse.arrayBuffer();
  await pyodide.unpackArchive(buffer, 'zip', { extractDir: dest });
}