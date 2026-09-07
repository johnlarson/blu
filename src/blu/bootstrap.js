import * as mp_mjs from '/_blu_internal/static/micropython.mjs'
import * as zipJs from 'https://cdn.jsdelivr.net/npm/@zip.js/zip.js@2.11.4/+esm';
import * as react from 'https://esm.sh/react';
import * as reactDom from 'https://esm.sh/react-dom/client';

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
await mpInstall('pathlib');
await mpInstall('functools');
await mpInstall('inspect');
await mpInstall('logging');
await mpInstall('base64');
await mpInstall('types');
mp.registerJsModule('_react', react);
mp.registerJsModule('_react_dom', reactDom);

const pyUtils = mp.import('blu._utils');
const root = pyUtils.unpickle_root();
console.log(root);