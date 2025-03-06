import { createRoot } from 'https://esm.sh/react-dom/client';
import { createElement as $, Fragment } from 'https://esm.sh/react';

const jsonString = document.querySelector('script[type="react-data"]').textContent;
const rootNodeJson = JSON.parse(jsonString);
const importPromises = getImportPromises(rootNodeJson);
const imports = await Promise.all(importPromises);
// resetRoot();
const rootNode = getNode(rootNodeJson, imports);
if (rootNodeJson.tagname === 'html') {
  createRoot(document).render(rootNode);
} else {
  createRoot(document.body).render(rootNode);
}

function resetRoot(rootNodeJson) {
  const tagname = rootNodeJson.tagname;
  if (tagname !== 'html') {
    document.getElementsByTagName('html')[0].remove();
    // document.appendChild(document.createElement('BODY'));
  }
}

function getImportPromises(json) {
  if (json instanceof Array) {
    return json.map(x => getImportPromises(x)).flat();
  } else if (json instanceof Object) {
    if (json.type === 'object') {
      return [];
    } else if (json.type === 'rendered_element') {
      return [getImport(json.module, json.name), ...getChildImports(json)];
    } else {
      return getChildImports(json);
    }
  } else {
    return [];
  }
}

async function getImport(module, name) {
  return {
    module,
    name,
    import: (await bluget(module))[name]
  }
}

function getChildImports(elementJson) {
  return elementJson.children.map(x => getImportPromises(x)).flat();
}

function getNode(json, imports) {
  if (json instanceof Array) {
    return getArray(json, imports);
  } else if (json instanceof Object) {
    if (json.type === 'object') {
      return getObj(json, imports);
    } else if (json.type === 'rendered_element') {
      const importInfo = imports.find(x => x.module === json.module && x.name === json.name);
      return $(importInfo.import, getObj(json.props, imports), ...getArray(json.children, imports));
    } else if (json.type === 'fragment') {
      return $(Fragment, getObj(json.props, imports), ...getArray(json.children, imports));
    } else if (json.type === 'native_element') {
      return $(json.tagname, getObj(json.props, imports), ...getArray(json.children, imports));
    } else {
      throw Error(`Unknown ReactDict type: '${json.type}'`);
    }
  } else {
    return json;
  }
}

function getObj(obj, imports) {
  return Object.entries(obj).reduce((prev, [k, v]) => ({
    ...prev,
    [k]: getNode(v, imports),
  }), {});
}

function getArray(array, imports) {
  return array.map(x => getNode(x, imports));
}