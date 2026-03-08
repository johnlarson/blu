import { createElement as $, Fragment } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import PyScript from 'https://pyscript.net/releases/2026.1.1/core.js';

window.ps = PyScript;

console.log('Hello from client utils!');
console.log('PYSCRIPT INTERPRETER:', PyScript)

let createProxy;
let blu;
let builtins;
let isinstance;

export function init(innerPyImport) {
  const ffi = innerPyImport('pyscript.ffi');
  createProxy = ffi.create_proxy(ffi.create_proxy);
  function pyImport(location) {
    return createProxy(innerPyImport(location))
  }
  blu = pyImport('blu');
  builtins = pyImport('builtins');
  isinstance = builtins.isinstance;
}

export function renderRoot(pyRootIn) {
  const pyRoot = createProxy(pyRootIn);
  const jsNode = getReactNode(pyRoot);
  const renderTarget = jsNode.type === 'html' ? document : document.body;
  createRoot(renderTarget).render(jsNode);
}

function getReactNode(pyNode) {
  if (isinstance(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
      renderer: pyNode._renderer,
      args: pyNode._args,
      kwargs: pyNode._kwargs,
      py_children: pyNode._children,
    })
  } else if (isinstance(pyNode, blu.Key)) {
    return $(Fragment, { key: pyNode._key },
      ...getArray(pyNode._children),
    );
  } else if (isinstance(pyNode, builtins.tuple)) {
    return $(Fragment, null, ...getArray(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (Symbol.iterator in pyNode) {
    return getArray(pyNode);
  } else if (isinstance(pyNode, blu.HTMLElement)) {
    return $(pyNode._tagname, null, ...getArray(pyNode._children));
  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function PythonElement({}) {

}

function getArray(pyNode) {

}

export function useState(init) {

}

export function useRef(init) {

}

export function useEffect(callback) {

}