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
      renderer: create_proxy(pyNode._renderer),
      args: create_proxy(pyNode._args),
      kwargs: create_proxy(pyNode._kwargs),
      py_children: create_proxy(pyNode._children),
    })
  } else if (isinstance(pyNode, blu.Key)) {
    return $(MemoryManagedFragment, { key: pyNode._key },
      ...getArray(pyNode._children),
    );
  } else if (isinstance(pyNode, builtins.tuple)) {
    return $(MemoryManagedFragment, null, ...getArray(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (Symbol.iterator in pyNode) {
    return getArray(pyNode);
  } else if (isinstance(pyNode, blu.HTMLElement)) {
    return $(Fragment, getObj())
  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function PythonElement({}) {

}

function MemoryManagedFragment(props) {

}

function MemoryManagedHTMLElement(props) {

}

function getArray(pyNode) {

}

export function useState(init) {

}

export function useRef(init) {

}

export function useEffect(callback) {

}