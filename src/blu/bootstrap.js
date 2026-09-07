import * as mp_mjs from '/_blu_internal/static/micropython.mjs'
import * as fflate from 'https://cdn.jsdelivr.net/npm/fflate@0.8.3/esm/browser.js'
// import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js';
import * as zipJs from 'https://cdn.jsdelivr.net/npm/@zip.js/zip.js@2.11.4/+esm';

const mp = await mp_mjs.loadMicroPython();



async function addPackage(url, dest) {
  const appZipResponse = await fetch(url);
  const appZipContent = await appZipResponse.blob();
  const zipFileReader = new zipJs.BlobReader(appZipContent);
  const zipReader = new zipJs.ZipReader(zipFileReader);
  mp.FS.mkdir(dest)
  for (const entry of await zipReader.getEntries()) {
    const fullPath = `${dest}/${entry.filename}`;
    //console.log(entry);
    if (entry.directory) {
      //mp.FS.mkdir(fullPath);
    } else {
      const fArrayBuff = await entry.arrayBuffer();
      const text = new TextDecoder().decode(fArrayBuff);
      // console.log("text:", text);
      const dir = fullPath.split('/').slice(0, -1).join('/');
      mp.FS.mkdirTree(dir);
      mp.FS.writeFile(fullPath, fArrayBuff);
    }
  }
  await zipReader.close();
}

const PACKAGE_INDEX_ROOT = 'https://micropython.org/pi/v2'

async function mpInstall(packageName) {
  const metadataUrl = `${PACKAGE_INDEX_ROOT}/package/py/${packageName}/latest.json`;
  const metadata = await (await fetch(metadataUrl)).json();
  for (const [name, hash] of metadata.hashes) {
    const fileUrl = `${PACKAGE_INDEX_ROOT}/file/${hash.slice(0, 2)}/${hash}`;
    const content = await (await fetch(fileUrl)).arrayBuffer();
    mp.FS.writeFile(`/${name}`, content);
  }

}

await addPackage('/_blu_internal/app_pkg.zip', '/app');
await addPackage('/_blu_internal/blu_pkg.zip', '/blu');
await mpInstall('pathlib')

mp.replInit

for (const char of 'import mip\nmip.install("pathlib")') {
  mp.replProcessChar(char);
}

// mp.runPython(`
// import mip

// mip.install("pathlib")
// `)

await mp.runPythonAsync(`
    await micropip.install('pathlib')
`)

mp.pyimport('blu._app.client_main');

// console.log('CONTENT:', appZipContent)

// const files = fflate.unzipSync(appZipContent);
// console.log(files)
// for (const [name, data] of Object.entries(files)) {
//   console.log(name, data);
// }


// const ds = new DecompressionStream('deflate');
// const decompressed = appZipContent.stream().pipeThrough(ds);
// const reader = new ReadableStreamDefaultReader(decompressed);
// console.log(await reader.read())
mp.FS.writeFile('/app.zip', appZipContent);
console.log('STAT:', mp.FS.stat('/app.zip'))


// window.result = mp.runPython(`
// import uzipfile
// import os

// print(os.listdir(os.getcwd()))


// `);

window.result = mp.runPython(`
import os

print(os.listdir(os.getcwd()))
`);

// document.body.textContent = 'Hello, World!'