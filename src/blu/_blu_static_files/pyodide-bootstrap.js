// import * as mp_mjs from '/_blu_internal/static/micropython.mjs'
// import * as zipJs from 'https://cdn.jsdelivr.net/npm/@zip.js/zip.js@2.11.4/+esm';

import 'https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.js';
import * as util from '/_blu_internal/static/util.js';

import * as react from 'https://esm.sh/react';
import * as reactDom from 'https://esm.sh/react-dom/client';

// bootstrapMicroPython();
bootstrapPyodide();

async function bootstrapPyodide() {
  const pyodide = await loadPyodide();
  console.log('Starting')
  const config = JSON.parse(document.getElementById('config').textContent);
  await Promise.all([
    unpackArchivePyodide('/_blu_internal/app_pkg.zip', './app', pyodide),
    unpackArchivePyodide('/_blu_internal/blu_pkg.zip', './blu', pyodide),
    pyodide.registerJsModule('_react', react),
    pyodide.registerJsModule('_react_dom', reactDom),
    pyodide.registerJsModule('_js_util', util),
    pyodide.loadPackage('micropip'),
    // pyodide.loadPackage(config.packages),
    // ...config.packages.map(x => pyodide.loadPackage(x)),
  ]);
  console.log('Packages added.');
  await pyodide.pyimport('blu._client_main.pyodide').main(config.packages)
  // await pyodide.pyimport('blu._client_main').main()
}

async function unpackArchivePyodide(url, dest, pyodide) {
  const zipResponse = await fetch(url);
  const buffer = await zipResponse.arrayBuffer();
  await pyodide.unpackArchive(buffer, 'zip', { extractDir: dest });
}

async function bootstrapMicroPython() {
  const mp = await mp_mjs.loadMicroPython();
  const config = JSON.parse(document.getElementById('config').textContent);
  await Promise.all([
    addPackageMicroPython('/_blu_internal/app_pkg.zip', '/app', mp),
    addPackageMicroPython('/_blu_internal/blu_pkg.zip', '/blu', mp),
    mpInstall('pathlib', mp),
    mpInstall('functools', mp),
    mpInstall('inspect', mp),
    mpInstall('logging', mp),
    mpInstall('base64', mp),
    mpInstall('types', mp),
    mpInstall('contextlib', mp),
    ...config.packages.map(x => mpInstall(x, mp)),
  ]);
  mp.registerJsModule('_react', react);
  mp.registerJsModule('_react_dom', reactDom);
  mp.registerJsModule('_js_util', util);
  mp.runPython(`
print('Hi!')
class A:
    def __getitem__(self, x):
        return x
print('1')
a = A()
print('2')
x = a['Hello',]
print('value:', x)
`)
  await mp.pyimport('blu._client_main').main();
}

async function addPackageMicroPython(url, dest, mp) {
  const appZipResponse = await fetch(url);
  const appZipContent = await appZipResponse.blob();
  const zipFileReader = new zipJs.BlobReader(appZipContent);
  const zipReader = new zipJs.ZipReader(zipFileReader);
  mp.FS.mkdir(dest)
  for (const entry of await zipReader.getEntries()) {
    const fullPath = `${dest}/${entry.filename}`;
    if (entry.directory) {
    } else {
      const fArrayBuff = await entry.arrayBuffer();
      const text = new TextDecoder().decode(fArrayBuff);
      writeFileTree(fullPath, fArrayBuff, mp.FS);
    }
  }
  await zipReader.close();
}

const MP_PACKAGE_INDEX_ROOT = 'https://micropython.org/pi/v2'

async function mpInstall(packageName, mp) {
  const metadataUrl = `${MP_PACKAGE_INDEX_ROOT}/package/py/${packageName}/latest.json`;
  const metadata = await (await fetch(metadataUrl)).json();
  for (const [name, hash] of metadata.hashes) {
    const fileUrl = `${MP_PACKAGE_INDEX_ROOT}/file/${hash.slice(0, 2)}/${hash}`;
    const content = await (await fetch(fileUrl)).arrayBuffer();
    const path = `/${name}`;
    writeFileTree(path, content, mp.FS);
  }
}

function writeFileTree(path, content, FS) {
  const dir = path.split('/').slice(0, -1).join('/');
  FS.mkdirTree(dir);
  FS.writeFile(path, content);
}

